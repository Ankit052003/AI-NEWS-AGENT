import json
import logging
import re
from datetime import UTC, date, datetime
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from pydantic import ValidationError

from app.config import Settings, get_settings
from app.schemas.research import ResearchRequest
from app.schemas.search import SearchResult

logger = logging.getLogger(__name__)

TRACKING_QUERY_PREFIXES = ("utm_",)
TRACKING_QUERY_PARAMS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
}


class SearchProviderError(Exception):
    """Raised when a search provider cannot return usable results."""


class SearchProviderUnavailable(SearchProviderError):
    """Raised when search is not configured for the current environment."""


class WebSearchService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def search(self, request: ResearchRequest) -> list[SearchResult]:
        provider = self.settings.search_provider.lower()
        if provider != "newsapi":
            msg = f"Unsupported search provider: {self.settings.search_provider}"
            raise SearchProviderError(msg)

        results = self._search_newsapi(request)
        deduped_results = self._dedupe_results(results)
        ranked_results = self._rank_results(request.query, deduped_results)

        return ranked_results[: request.max_sources]

    def _search_newsapi(self, request: ResearchRequest) -> list[SearchResult]:
        if not self.settings.search_api_key:
            raise SearchProviderUnavailable("SEARCH_API_KEY is not configured")

        query_params = {
            "q": request.query,
            "pageSize": str(min(request.max_sources * 3, 100)),
            "language": self.settings.search_language,
            "sortBy": self.settings.search_sort_by,
            "apiKey": self.settings.search_api_key,
        }

        if request.date_range:
            if request.date_range.start_date:
                query_params["from"] = request.date_range.start_date.isoformat()
            if request.date_range.end_date:
                query_params["to"] = request.date_range.end_date.isoformat()

        url = f"{self.settings.search_api_base_url}?{urlencode(query_params)}"
        http_request = Request(
            url,
            headers={"User-Agent": "NewsResearchAgent/0.1"},
            method="GET",
        )

        try:
            with urlopen(  # noqa: S310 - URL is configured by application settings.
                http_request,
                timeout=self.settings.search_timeout_seconds,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            msg = f"NewsAPI request failed with status {exc.code}: {detail}"
            raise SearchProviderError(msg) from exc
        except (TimeoutError, URLError, json.JSONDecodeError) as exc:
            msg = "NewsAPI request failed"
            raise SearchProviderError(msg) from exc

        if payload.get("status") != "ok":
            message = payload.get("message", "unknown NewsAPI error")
            msg = f"NewsAPI returned an error: {message}"
            raise SearchProviderError(msg)

        articles = payload.get("articles", [])
        if not isinstance(articles, list):
            raise SearchProviderError("NewsAPI returned an invalid articles payload")

        return self._normalize_newsapi_articles(articles)

    def _normalize_newsapi_articles(
        self,
        articles: list[object],
    ) -> list[SearchResult]:
        results: list[SearchResult] = []

        for article in articles:
            if not isinstance(article, dict):
                continue

            title = self._clean_text(article.get("title"))
            url = self._clean_text(article.get("url"))
            snippet = self._clean_text(article.get("description")) or self._clean_text(
                article.get("content"),
            )

            source_payload = article.get("source")
            source = "Unknown source"
            if isinstance(source_payload, dict):
                source = self._clean_text(source_payload.get("name")) or source

            if not title or not url or title == "[Removed]" or url == "[Removed]":
                continue

            try:
                results.append(
                    SearchResult(
                        title=title,
                        url=url,
                        source=source,
                        snippet=snippet or "No snippet available.",
                        published_date=self._parse_published_date(
                            article.get("publishedAt"),
                        ),
                    ),
                )
            except ValidationError:
                logger.debug("Skipping invalid search result: %s", article)

        return results

    def _dedupe_results(self, results: list[SearchResult]) -> list[SearchResult]:
        seen_urls: set[str] = set()
        deduped_results: list[SearchResult] = []

        for result in results:
            normalized_url = self._normalize_url(str(result.url))
            if normalized_url in seen_urls:
                continue

            seen_urls.add(normalized_url)
            deduped_results.append(result)

        return deduped_results

    def _rank_results(
        self,
        query: str,
        results: list[SearchResult],
    ) -> list[SearchResult]:
        query_terms = {
            term.lower()
            for term in re.findall(r"[A-Za-z0-9]+", query)
            if len(term) > 2
        }
        today = datetime.now(UTC).date()

        def score(result: SearchResult) -> tuple[float, date]:
            title = result.title.lower()
            searchable_text = f"{result.title} {result.snippet} {result.source}".lower()
            term_matches = sum(1 for term in query_terms if term in searchable_text)
            title_matches = sum(1 for term in query_terms if term in title)

            freshness_score = 0.0
            published_date = result.published_date
            if published_date:
                age_days = max((today - published_date).days, 0)
                freshness_score = max(0.0, 30 - age_days) / 30

            return (
                (title_matches * 3) + term_matches + freshness_score,
                published_date or date.min,
            )

        return sorted(results, key=score, reverse=True)

    def _normalize_url(self, url: str) -> str:
        parsed_url = urlsplit(url)
        query_params = []

        for key, value in parse_qsl(parsed_url.query, keep_blank_values=True):
            if key in TRACKING_QUERY_PARAMS:
                continue
            if key.startswith(TRACKING_QUERY_PREFIXES):
                continue
            query_params.append((key, value))

        return urlunsplit(
            (
                parsed_url.scheme.lower(),
                parsed_url.netloc.lower(),
                parsed_url.path.rstrip("/"),
                urlencode(query_params),
                "",
            ),
        )

    def _parse_published_date(self, raw_value: object) -> date | None:
        if not isinstance(raw_value, str) or not raw_value:
            return None

        try:
            return datetime.fromisoformat(raw_value.replace("Z", "+00:00")).date()
        except ValueError:
            logger.debug(
                "Could not parse published date from search result: %s",
                raw_value,
            )
            return None

    def _clean_text(self, raw_value: object) -> str:
        if not isinstance(raw_value, str):
            return ""

        return " ".join(raw_value.split())
