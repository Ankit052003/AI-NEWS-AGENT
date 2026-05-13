import logging
from datetime import UTC, datetime, timedelta

from app.config import Settings, get_settings
from app.schemas.article import ExtractedArticle
from app.schemas.research import ResearchRequest, ResearchResponse, ResearchSource
from app.schemas.search import SearchResult
from app.services.content_extraction import ContentExtractionService
from app.services.web_search import (
    SearchProviderError,
    SearchProviderUnavailable,
    WebSearchService,
)

logger = logging.getLogger(__name__)


class ResearchServiceError(Exception):
    """Raised when the research service cannot generate a report."""


class ResearchService:
    def __init__(
        self,
        settings: Settings | None = None,
        web_search_service: WebSearchService | None = None,
        content_extraction_service: ContentExtractionService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.web_search_service = web_search_service or WebSearchService(self.settings)
        self.content_extraction_service = (
            content_extraction_service or ContentExtractionService(self.settings)
        )

    def generate_report(self, request: ResearchRequest) -> ResearchResponse:
        logger.info("Generating research report for query=%s", request.query)

        try:
            search_results = self.web_search_service.search(request)
            sources = self._to_research_sources(search_results)
            articles = self.content_extraction_service.extract_many(sources)
            is_live_search = True
            summary = (
                f"Found {len(sources)} relevant source"
                f"{'' if len(sources) == 1 else 's'} for '{request.query}'. "
                f"Extracted clean article text from {len(articles)} source"
                f"{'' if len(articles) == 1 else 's'}. "
                "This Phase 4 response is ready for AI summarization."
            )
        except SearchProviderUnavailable as exc:
            logger.warning("%s. Falling back to mocked development sources.", exc)
            sources = self._mock_sources()[: request.max_sources]
            articles = []
            is_live_search = False
            summary = (
                f"Mock research report for '{request.query}'. Configure "
                "SEARCH_API_KEY to replace these placeholders with live NewsAPI "
                "search results and article extraction."
            )
        except SearchProviderError as exc:
            msg = "Web search failed"
            raise ResearchServiceError(msg) from exc

        return ResearchResponse(
            query=request.query,
            summary=summary,
            report=self._build_report(
                request=request,
                sources=sources,
                articles=articles,
                is_live_search=is_live_search,
            ),
            sources=sources,
            articles=articles,
        )

    def generate_mock_report(self, request: ResearchRequest) -> ResearchResponse:
        logger.info("Generating mocked research report for query=%s", request.query)

        sources = self._mock_sources()[: request.max_sources]
        summary = (
            f"Mock research report for '{request.query}'. "
            "This Phase 2 response proves the API contract before live search, "
            "article extraction, and LLM summarization are added."
        )

        return ResearchResponse(
            query=request.query,
            summary=summary,
            report=self._build_report(
                request=request,
                sources=sources,
                articles=[],
                is_live_search=False,
            ),
            sources=sources,
            articles=[],
        )

    def _to_research_sources(
        self,
        search_results: list[SearchResult],
    ) -> list[ResearchSource]:
        return [
            ResearchSource.model_validate(search_result.model_dump())
            for search_result in search_results
        ]

    def _mock_sources(self) -> list[ResearchSource]:
        today = datetime.now(UTC).date()

        return [
            ResearchSource(
                title="Mock: AI infrastructure startup funding update",
                url="https://example.com/ai-infrastructure-funding",
                source="Example Tech News",
                snippet=(
                    "Placeholder result representing a future web search result "
                    "about AI infrastructure funding."
                ),
                published_date=today - timedelta(days=1),
            ),
            ResearchSource(
                title="Mock: Healthcare AI companies attract investor interest",
                url="https://example.com/healthcare-ai-investors",
                source="Example Market Daily",
                snippet=(
                    "Placeholder result representing an article about funding "
                    "activity in healthcare AI."
                ),
                published_date=today - timedelta(days=2),
            ),
            ResearchSource(
                title="Mock: Generative AI product launches and funding signals",
                url="https://example.com/generative-ai-product-funding",
                source="Example Startup Brief",
                snippet=(
                    "Placeholder result representing a future source on "
                    "generative AI company announcements."
                ),
                published_date=today - timedelta(days=3),
            ),
            ResearchSource(
                title="Mock: Robotics startup market activity",
                url="https://example.com/robotics-startup-market",
                source="Example Robotics Wire",
                snippet=(
                    "Placeholder result representing a future source on robotics "
                    "startup news."
                ),
                published_date=today - timedelta(days=4),
            ),
            ResearchSource(
                title="Mock: AI acquisition and partnership roundup",
                url="https://example.com/ai-acquisition-partnerships",
                source="Example Deal Desk",
                snippet=(
                    "Placeholder result representing a future source on AI "
                    "acquisitions and partnerships."
                ),
                published_date=today - timedelta(days=5),
            ),
        ]

    def _build_report(
        self,
        request: ResearchRequest,
        sources: list[ResearchSource],
        articles: list[ExtractedArticle],
        is_live_search: bool,
    ) -> str:
        date_range = self._format_date_range(request)
        report_intro = (
            f"This Phase 4 report is for: **{request.query}**."
            if is_live_search
            else (
                "This Phase 4 development report uses mocked sources for: "
                f"**{request.query}**."
            )
        )
        source_context = (
            "Source objects were collected through the NewsAPI web search provider."
            if is_live_search
            else "Source objects are placeholders until SEARCH_API_KEY is configured."
        )
        extraction_context = self._format_extraction_context(
            source_count=len(sources),
            article_count=len(articles),
            is_live_search=is_live_search,
        )
        source_lines = "\n".join(
            f"{index}. [{source.title}]({source.url}) - {source.source}"
            for index, source in enumerate(sources, start=1)
        )
        article_lines = self._format_article_lines(sources, articles)

        return f"""# Research Report

## Executive Summary

{report_intro}

The backend now accepts a structured research request and returns the same shape
the real pipeline will use later: summary, Markdown report, source metadata, and
generation timestamp.

## Request Settings

- Max sources: {request.max_sources}
- Date range: {date_range}
- Extraction timeout: {self.settings.content_extraction_timeout_seconds} seconds
- Extraction minimum: {self.settings.content_extraction_min_words} words
- LLM provider: {self.settings.default_llm_provider}
- Model: {self.settings.default_model}

## Key Findings

- The API contract is ready for frontend integration.
- {source_context}
- {extraction_context}
- The report is Markdown so it can be rendered directly in the frontend later.

## Important Articles

{article_lines}

## Emerging Trends

- This section is mocked for now.
- Phase 5 will replace it with LLM-generated synthesis.
- Phase 11 will add deeper structured trend analysis.

## Source List

{source_lines}
"""

    def _format_date_range(self, request: ResearchRequest) -> str:
        if not request.date_range:
            return "not provided"

        start = request.date_range.start_date or "open start"
        end = request.date_range.end_date or "open end"
        return f"{start} to {end}"

    def _format_extraction_context(
        self,
        source_count: int,
        article_count: int,
        is_live_search: bool,
    ) -> str:
        if not is_live_search:
            return (
                "Article extraction is skipped while using mocked development "
                "sources."
            )

        if article_count:
            return (
                f"Clean text was extracted from {article_count} of "
                f"{source_count} collected sources."
            )

        return (
            "No collected sources produced enough clean article text; blocked, "
            "paywalled, or non-article pages were skipped."
        )

    def _format_article_lines(
        self,
        sources: list[ResearchSource],
        articles: list[ExtractedArticle],
    ) -> str:
        if articles:
            return "\n".join(
                (
                    f"- [{index}] {article.title} "
                    f"({article.word_count} words extracted): "
                    f"{self._preview_text(article.extracted_text)}"
                )
                for index, article in enumerate(articles, start=1)
            )

        return "\n".join(
            f"- [{index}] {source.title}: {source.snippet}"
            for index, source in enumerate(sources, start=1)
        )

    def _preview_text(self, text: str, limit: int = 260) -> str:
        if len(text) <= limit:
            return text

        return f"{text[:limit].rstrip()}..."
