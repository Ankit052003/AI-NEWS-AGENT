import html
import logging
import re
from datetime import date, datetime
from html.parser import HTMLParser

import httpx
from pydantic import HttpUrl

from app.config import Settings, get_settings
from app.schemas.article import ExtractedArticle
from app.schemas.research import ResearchSource

logger = logging.getLogger(__name__)

CONTENT_TAGS = {
    "blockquote",
    "h1",
    "h2",
    "h3",
    "li",
    "p",
}
SKIP_TAGS = {
    "aside",
    "button",
    "canvas",
    "footer",
    "form",
    "header",
    "iframe",
    "nav",
    "noscript",
    "script",
    "style",
    "svg",
}
VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}
AUTHOR_META_NAMES = {
    "article:author",
    "author",
    "byl",
    "byline",
    "dc.creator",
    "parsely-author",
    "twitter:creator",
}
PUBLISHED_META_NAMES = {
    "article:published_time",
    "date",
    "datepublished",
    "dc.date",
    "parsely-pub-date",
    "pubdate",
    "publishdate",
}
BOILERPLATE_PATTERNS = (
    "accept cookies",
    "advertisement",
    "all rights reserved",
    "cookie policy",
    "privacy policy",
    "sign in",
    "sign up",
    "subscribe",
)


class ContentExtractionError(Exception):
    """Raised when a URL cannot be converted into useful article text."""


class _ArticleHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.heading = ""
        self.author: str | None = None
        self.published_date: date | None = None
        self.blocks: list[str] = []
        self._skip_depth = 0
        self._active_block_tag: str | None = None
        self._active_block_parts: list[str] = []
        self._in_title = False
        self._title_parts: list[str] = []
        self._in_h1 = False
        self._h1_parts: list[str] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        tag = tag.lower()
        attrs_dict = {key.lower(): value or "" for key, value in attrs}

        if self._skip_depth:
            if tag not in VOID_TAGS:
                self._skip_depth += 1
            return

        if tag in SKIP_TAGS or self._is_hidden(attrs_dict):
            self._skip_depth += 1
            return

        if tag == "title":
            self._in_title = True
            self._title_parts = []
        elif tag == "h1":
            self._in_h1 = True
            self._h1_parts = []
            self._start_block(tag)
        elif tag in CONTENT_TAGS:
            self._start_block(tag)
        elif tag == "meta":
            self._capture_meta(attrs_dict)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if self._skip_depth:
            self._skip_depth -= 1
            return

        if tag == "title":
            self._in_title = False
            self.title = _clean_text(" ".join(self._title_parts))
        elif tag == "h1":
            self._in_h1 = False
            self.heading = _clean_text(" ".join(self._h1_parts))
            self._finish_block()
        elif tag == self._active_block_tag:
            self._finish_block()

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return

        if self._in_title:
            self._title_parts.append(data)
        if self._in_h1:
            self._h1_parts.append(data)
        if self._active_block_tag:
            self._active_block_parts.append(data)

    def _start_block(self, tag: str) -> None:
        if self._active_block_tag:
            self._finish_block()

        self._active_block_tag = tag
        self._active_block_parts = []

    def _finish_block(self) -> None:
        block = _clean_text(" ".join(self._active_block_parts))
        self._active_block_tag = None
        self._active_block_parts = []

        if _is_useful_block(block):
            self.blocks.append(block)

    def _capture_meta(self, attrs: dict[str, str]) -> None:
        name = attrs.get("name") or attrs.get("property") or attrs.get("itemprop")
        content = attrs.get("content")
        if not name or not content:
            return

        normalized_name = name.lower()
        if not self.author and normalized_name in AUTHOR_META_NAMES:
            self.author = _clean_text(content)
        if not self.published_date and normalized_name in PUBLISHED_META_NAMES:
            self.published_date = _parse_date(content)

    def _is_hidden(self, attrs: dict[str, str]) -> bool:
        if "hidden" in attrs:
            return True

        style = attrs.get("style", "").replace(" ", "").lower()
        return "display:none" in style or "visibility:hidden" in style


class ContentExtractionService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def extract_many(self, sources: list[ResearchSource]) -> list[ExtractedArticle]:
        extracted_articles: list[ExtractedArticle] = []

        with httpx.Client(
            follow_redirects=True,
            headers={"User-Agent": self.settings.content_extraction_user_agent},
            timeout=self.settings.content_extraction_timeout_seconds,
        ) as client:
            for source in sources:
                try:
                    extracted_articles.append(self.extract(source, client=client))
                except ContentExtractionError as exc:
                    logger.warning(
                        "Skipping article extraction for %s: %s",
                        source.url,
                        exc,
                    )

        return extracted_articles

    def extract(
        self,
        source: ResearchSource,
        client: httpx.Client | None = None,
    ) -> ExtractedArticle:
        if client:
            html_content = self._fetch_html(source, client)
        else:
            with httpx.Client(
                follow_redirects=True,
                headers={"User-Agent": self.settings.content_extraction_user_agent},
                timeout=self.settings.content_extraction_timeout_seconds,
            ) as owned_client:
                html_content = self._fetch_html(source, owned_client)

        return self.extract_from_html(source=source, html_content=html_content)

    def extract_from_html(
        self,
        source: ResearchSource,
        html_content: str,
    ) -> ExtractedArticle:
        parser = _ArticleHtmlParser()
        parser.feed(html_content)
        parser.close()

        blocks = self._dedupe_blocks(parser.blocks)
        extracted_text = "\n\n".join(blocks)
        word_count = len(re.findall(r"\b[\w'-]+\b", extracted_text))

        if word_count < self.settings.content_extraction_min_words:
            msg = (
                "extracted text was too short "
                f"({word_count} words; minimum is "
                f"{self.settings.content_extraction_min_words})"
            )
            raise ContentExtractionError(msg)

        return ExtractedArticle(
            title=self._choose_title(source, parser),
            url=HttpUrl(str(source.url)),
            source=source.source,
            author=parser.author,
            published_date=parser.published_date or source.published_date,
            extracted_text=extracted_text,
            word_count=word_count,
        )

    def _fetch_html(self, source: ResearchSource, client: httpx.Client) -> str:
        try:
            response = client.get(str(source.url))
            response.raise_for_status()
        except httpx.HTTPError as exc:
            msg = f"request failed: {exc}"
            raise ContentExtractionError(msg) from exc

        content_type = response.headers.get("content-type", "").lower()
        if content_type and not _is_html_content_type(content_type):
            msg = f"unsupported content type: {content_type}"
            raise ContentExtractionError(msg)

        return response.text

    def _dedupe_blocks(self, blocks: list[str]) -> list[str]:
        seen_blocks: set[str] = set()
        deduped_blocks: list[str] = []

        for block in blocks:
            normalized_block = block.lower()
            if normalized_block in seen_blocks:
                continue

            seen_blocks.add(normalized_block)
            deduped_blocks.append(block)

        return deduped_blocks

    def _choose_title(self, source: ResearchSource, parser: _ArticleHtmlParser) -> str:
        for candidate in (parser.heading, source.title, parser.title):
            cleaned_candidate = _clean_text(candidate)
            if cleaned_candidate:
                return cleaned_candidate

        return "Untitled article"


def _clean_text(raw_value: str) -> str:
    cleaned = html.unescape(raw_value)
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _is_useful_block(block: str) -> bool:
    if len(block) < 35:
        return False

    normalized_block = block.lower()
    if any(pattern in normalized_block for pattern in BOILERPLATE_PATTERNS):
        return False

    return True


def _is_html_content_type(content_type: str) -> bool:
    return "text/html" in content_type or "application/xhtml+xml" in content_type


def _parse_date(raw_value: str) -> date | None:
    cleaned_value = raw_value.strip()
    if not cleaned_value:
        return None

    for value in (
        cleaned_value,
        cleaned_value.replace("Z", "+00:00"),
        cleaned_value[:10],
    ):
        try:
            return datetime.fromisoformat(value).date()
        except ValueError:
            continue

    return None
