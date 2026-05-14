from __future__ import annotations

import json
import logging
import re
from collections import Counter

import httpx

from app.config import Settings, get_settings
from app.schemas.article import ExtractedArticle
from app.schemas.research import ArticleSummary, ResearchRequest, ResearchSource

logger = logging.getLogger(__name__)

MAX_SUMMARY_CHARS = 9000

CATEGORY_KEYWORDS = {
    "Funding activity": {
        "funding",
        "investment",
        "investor",
        "raise",
        "raised",
        "round",
        "series",
        "valuation",
    },
    "Acquisitions and partnerships": {
        "acquire",
        "acquired",
        "acquisition",
        "merge",
        "merger",
        "partner",
        "partnership",
    },
    "Generative AI products": {
        "chatbot",
        "copilot",
        "foundation",
        "generative",
        "llm",
        "model",
    },
    "AI infrastructure": {
        "chip",
        "cloud",
        "compute",
        "data center",
        "gpu",
        "infrastructure",
        "training",
    },
    "Healthcare AI": {
        "biotech",
        "clinical",
        "drug",
        "healthcare",
        "hospital",
        "medical",
        "patient",
    },
}

STOPWORDS = {
    "about",
    "after",
    "again",
    "also",
    "and",
    "are",
    "because",
    "been",
    "being",
    "but",
    "can",
    "from",
    "has",
    "have",
    "into",
    "latest",
    "more",
    "news",
    "not",
    "over",
    "said",
    "that",
    "the",
    "their",
    "this",
    "through",
    "with",
    "would",
    "your",
}


class SummarizationProviderError(Exception):
    """Raised when an LLM provider cannot return a usable structured summary."""


class SummarizationService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def summarize_articles(
        self,
        request: ResearchRequest,
        sources: list[ResearchSource],
        articles: list[ExtractedArticle],
    ) -> list[ArticleSummary]:
        article_by_url = {_url_key(article.url): article for article in articles}
        summaries: list[ArticleSummary] = []

        for index, source in enumerate(sources, start=1):
            article = article_by_url.get(_url_key(source.url))
            summary = self._summarize_one(
                request=request,
                source=source,
                article=article,
                citation_index=index,
            )
            summaries.append(summary)

        return summaries

    def build_report(
        self,
        request: ResearchRequest,
        sources: list[ResearchSource],
        articles: list[ExtractedArticle],
        article_summaries: list[ArticleSummary],
        is_live_search: bool,
    ) -> tuple[str, str]:
        extracted_count = len(articles)
        summary = self._build_executive_summary(
            request=request,
            source_count=len(sources),
            extracted_count=extracted_count,
            article_summaries=article_summaries,
            is_live_search=is_live_search,
        )

        report = "\n\n".join(
            [
                "# Research Report",
                "## Executive Summary",
                summary,
                "## Key Findings",
                self._format_key_findings(article_summaries),
                "## Important Articles",
                self._format_important_articles(article_summaries),
                "## Emerging Trends",
                self._format_trends(article_summaries),
                "## Source List",
                self._format_sources(sources),
            ],
        )

        return summary, report

    def _summarize_one(
        self,
        request: ResearchRequest,
        source: ResearchSource,
        article: ExtractedArticle | None,
        citation_index: int,
    ) -> ArticleSummary:
        text = (
            article.extracted_text
            if article
            else f"{source.title}. {source.snippet}"
        )
        title = article.title if article else source.title
        published_date = article.published_date if article else source.published_date

        if self._can_use_openai():
            try:
                return self._summarize_with_openai(
                    request=request,
                    source=source,
                    text=text,
                    title=title,
                    published_date=published_date,
                    citation_index=citation_index,
                )
            except SummarizationProviderError as exc:
                logger.warning(
                    "OpenAI summarization failed for %s; using local fallback: %s",
                    source.url,
                    exc,
                )

        return self._summarize_locally(
            request=request,
            source=source,
            text=text,
            title=title,
            published_date=published_date,
            citation_index=citation_index,
        )

    def _can_use_openai(self) -> bool:
        return (
            self.settings.default_llm_provider.lower() == "openai"
            and bool(self.settings.openai_api_key)
            and not self.settings.default_model.startswith("mock")
        )

    def _summarize_with_openai(
        self,
        request: ResearchRequest,
        source: ResearchSource,
        text: str,
        title: str,
        published_date,
        citation_index: int,
    ) -> ArticleSummary:
        prompt = {
            "query": request.query,
            "title": title,
            "source": source.source,
            "snippet": source.snippet,
            "article_text": _trim_text(text, MAX_SUMMARY_CHARS),
        }
        payload = {
            "model": self.settings.default_model,
            "temperature": self.settings.llm_temperature,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You summarize news articles for a market research "
                        "report. Return compact JSON with keys summary and "
                        "key_points. key_points must be an array of 2 to 4 "
                        "source-backed strings. Do not invent facts."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt),
                },
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openai_api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.settings.llm_timeout_seconds) as client:
                response = client.post(
                    self.settings.openai_api_base_url,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                raw_payload = response.json()
            content = raw_payload["choices"][0]["message"]["content"]
            parsed = json.loads(content)
        except (
            KeyError,
            TypeError,
            ValueError,
            httpx.HTTPError,
            json.JSONDecodeError,
        ) as exc:
            msg = "provider returned an invalid response"
            raise SummarizationProviderError(msg) from exc

        summary = _clean_text(str(parsed.get("summary", "")))
        key_points = [
            _clean_text(str(point))
            for point in parsed.get("key_points", [])
            if _clean_text(str(point))
        ][:4]

        if not summary:
            msg = "provider response did not include a summary"
            raise SummarizationProviderError(msg)

        if not key_points:
            key_points = self._extract_key_points(text, request.query)

        return ArticleSummary(
            citation_index=citation_index,
            title=title,
            url=str(source.url),
            source=source.source,
            summary=summary,
            key_points=key_points,
            published_date=published_date,
        )

    def _summarize_locally(
        self,
        request: ResearchRequest,
        source: ResearchSource,
        text: str,
        title: str,
        published_date,
        citation_index: int,
    ) -> ArticleSummary:
        sentences = _split_sentences(text)
        query_terms = _important_terms(request.query)
        scored_sentences = sorted(
            sentences,
            key=lambda sentence: self._sentence_score(sentence, query_terms),
            reverse=True,
        )
        summary_sentences = scored_sentences[:2] or sentences[:2]
        summary = " ".join(summary_sentences).strip() or source.snippet

        return ArticleSummary(
            citation_index=citation_index,
            title=title,
            url=str(source.url),
            source=source.source,
            summary=_trim_text(summary, 520),
            key_points=self._extract_key_points(text, request.query),
            published_date=published_date,
        )

    def _sentence_score(self, sentence: str, query_terms: set[str]) -> int:
        normalized = sentence.lower()
        score = sum(2 for term in query_terms if term in normalized)
        score += sum(
            1
            for keywords in CATEGORY_KEYWORDS.values()
            for keyword in keywords
            if keyword in normalized
        )
        has_amount = re.search(
            r"\$[\d,.]+|\d+\s?(million|billion|m|bn)",
            normalized,
        )
        score += 1 if has_amount else 0
        return score

    def _extract_key_points(self, text: str, query: str) -> list[str]:
        sentences = _split_sentences(text)
        query_terms = _important_terms(query)
        ranked = sorted(
            sentences,
            key=lambda sentence: self._sentence_score(sentence, query_terms),
            reverse=True,
        )
        points: list[str] = []

        for sentence in ranked:
            cleaned = _trim_text(sentence, 220)
            if cleaned and cleaned not in points:
                points.append(cleaned)
            if len(points) == 3:
                break

        return points or [_trim_text(_clean_text(text), 220)]

    def _build_executive_summary(
        self,
        request: ResearchRequest,
        source_count: int,
        extracted_count: int,
        article_summaries: list[ArticleSummary],
        is_live_search: bool,
    ) -> str:
        if not article_summaries:
            return (
                f"No usable sources were available for '{request.query}'. Try a "
                "broader query or configure a live search provider."
            )

        top_themes = self._theme_counts(article_summaries).most_common(2)
        theme_text = ", ".join(theme.lower() for theme, _ in top_themes)
        source_text = (
            f"{source_count} live source"
            f"{'' if source_count == 1 else 's'}"
            if is_live_search
            else f"{source_count} mocked development source"
            f"{'' if source_count == 1 else 's'}"
        )
        extraction_text = (
            f" Clean article text was extracted from {extracted_count} source"
            f"{'' if extracted_count == 1 else 's'}."
            if is_live_search
            else (
                " Configure SEARCH_API_KEY to replace mocked sources with live "
                "results."
            )
        )
        trend_text = f" Repeated themes include {theme_text}." if theme_text else ""

        return (
            f"For '{request.query}', the system reviewed {source_text} and built "
            f"a cited Markdown report from the available source text."
            f"{extraction_text}{trend_text}"
        )

    def _format_key_findings(self, article_summaries: list[ArticleSummary]) -> str:
        findings: list[str] = []

        for article_summary in article_summaries:
            point = (
                article_summary.key_points[0]
                if article_summary.key_points
                else article_summary.summary
            )
            findings.append(
                f"- {point} [{article_summary.citation_index}]",
            )

        return "\n".join(findings) if findings else "- No key findings available."

    def _format_important_articles(
        self,
        article_summaries: list[ArticleSummary],
    ) -> str:
        if not article_summaries:
            return "- No article summaries available."

        sections: list[str] = []
        for article_summary in article_summaries:
            date_text = (
                f", {article_summary.published_date.isoformat()}"
                if article_summary.published_date
                else ""
            )
            points = "\n".join(
                f"  - {point}" for point in article_summary.key_points[:3]
            )
            sections.append(
                "\n".join(
                    [
                        (
                            f"- [{article_summary.citation_index}] "
                            f"{article_summary.title} ({article_summary.source}"
                            f"{date_text})"
                        ),
                        f"  - {article_summary.summary}",
                        points,
                    ],
                ).rstrip(),
            )

        return "\n".join(sections)

    def _format_trends(self, article_summaries: list[ArticleSummary]) -> str:
        theme_counts = self._theme_counts(article_summaries)
        if not theme_counts:
            return (
                "- No repeated cross-source theme emerged from the available "
                "source text."
            )

        lines: list[str] = []
        for theme, count in theme_counts.most_common(4):
            citation_indexes = [
                summary.citation_index
                for summary in article_summaries
                if self._summary_has_theme(summary, theme)
            ]
            citations = ", ".join(f"[{index}]" for index in citation_indexes[:5])
            lines.append(
                f"- {theme} appears in {count} source"
                f"{'' if count == 1 else 's'} {citations}."
            )

        return "\n".join(lines)

    def _format_sources(self, sources: list[ResearchSource]) -> str:
        if not sources:
            return "- No sources available."

        return "\n".join(
            f"{index}. [{source.title}]({source.url}) - {source.source}"
            for index, source in enumerate(sources, start=1)
        )

    def _theme_counts(
        self,
        article_summaries: list[ArticleSummary],
    ) -> Counter[str]:
        counts: Counter[str] = Counter()
        for theme in CATEGORY_KEYWORDS:
            for article_summary in article_summaries:
                if self._summary_has_theme(article_summary, theme):
                    counts[theme] += 1

        return Counter({theme: count for theme, count in counts.items() if count > 0})

    def _summary_has_theme(self, article_summary: ArticleSummary, theme: str) -> bool:
        text = " ".join(
            [
                article_summary.title,
                article_summary.summary,
                *article_summary.key_points,
            ],
        ).lower()

        return any(keyword in text for keyword in CATEGORY_KEYWORDS[theme])


def _url_key(raw_url: object) -> str:
    return str(raw_url).rstrip("/")


def _split_sentences(text: str) -> list[str]:
    cleaned_text = _clean_text(text)
    sentences = re.split(r"(?<=[.!?])\s+", cleaned_text)
    return [
        sentence.strip()
        for sentence in sentences
        if 45 <= len(sentence.strip()) <= 320
    ]


def _important_terms(text: str) -> set[str]:
    return {
        term
        for term in re.findall(r"[a-z0-9]+", text.lower())
        if len(term) > 2 and term not in STOPWORDS
    }


def _clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _trim_text(text: str, limit: int) -> str:
    cleaned = _clean_text(text)
    if len(cleaned) <= limit:
        return cleaned

    return f"{cleaned[:limit].rstrip()}..."
