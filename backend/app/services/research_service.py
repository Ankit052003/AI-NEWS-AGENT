import logging
from datetime import UTC, datetime, timedelta

from app.config import Settings, get_settings
from app.schemas.research import ResearchRequest, ResearchResponse, ResearchSource

logger = logging.getLogger(__name__)


class ResearchServiceError(Exception):
    """Raised when the research service cannot generate a report."""


class ResearchService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

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
            report=self._build_report(request=request, sources=sources),
            sources=sources,
        )

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
    ) -> str:
        date_range = self._format_date_range(request)
        source_lines = "\n".join(
            f"{index}. [{source.title}]({source.url}) - {source.source}"
            for index, source in enumerate(sources, start=1)
        )
        article_lines = "\n".join(
            f"- [{index}] {source.title}: {source.snippet}"
            for index, source in enumerate(sources, start=1)
        )

        return f"""# Research Report

## Executive Summary

This is a mocked Phase 2 report for: **{request.query}**.

The backend now accepts a structured research request and returns the same shape
the real pipeline will use later: summary, Markdown report, source metadata, and
generation timestamp.

## Request Settings

- Max sources: {request.max_sources}
- Date range: {date_range}
- LLM provider: {self.settings.default_llm_provider}
- Model: {self.settings.default_model}

## Key Findings

- The API contract is ready for frontend integration.
- Source objects are already shaped for citations and future search results.
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
