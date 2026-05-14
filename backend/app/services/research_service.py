import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.schemas.research import (
    ResearchHistoryItem,
    ResearchRequest,
    ResearchResponse,
    ResearchSource,
    SavedReportResponse,
)
from app.schemas.search import SearchResult
from app.services.content_extraction import ContentExtractionService
from app.services.history import ResearchHistoryService
from app.services.summarization import SummarizationService
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
        summarization_service: SummarizationService | None = None,
        history_service: ResearchHistoryService | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.web_search_service = web_search_service or WebSearchService(self.settings)
        self.content_extraction_service = (
            content_extraction_service or ContentExtractionService(self.settings)
        )
        self.summarization_service = summarization_service or SummarizationService(
            self.settings,
        )
        self.history_service = history_service or ResearchHistoryService()

    def generate_report(
        self,
        request: ResearchRequest,
        db: Session | None = None,
    ) -> ResearchResponse:
        logger.info("Generating research report for query=%s", request.query)

        try:
            search_results = self.web_search_service.search(request)
            sources = self._to_research_sources(search_results)
            articles = self.content_extraction_service.extract_many(sources)
            is_live_search = True
        except SearchProviderUnavailable as exc:
            logger.warning("%s. Falling back to mocked development sources.", exc)
            sources = self._mock_sources()[: request.max_sources]
            articles = []
            is_live_search = False
        except SearchProviderError as exc:
            msg = "Web search failed"
            raise ResearchServiceError(msg) from exc

        article_summaries = self.summarization_service.summarize_articles(
            request=request,
            sources=sources,
            articles=articles,
        )
        summary, report = self.summarization_service.build_report(
            request=request,
            sources=sources,
            articles=articles,
            article_summaries=article_summaries,
            is_live_search=is_live_search,
        )

        response = ResearchResponse(
            query=request.query,
            summary=summary,
            report=report,
            sources=sources,
            articles=articles,
            article_summaries=article_summaries,
        )

        if db:
            self._persist_response(db=db, request=request, response=response)

        return response

    def generate_mock_report(self, request: ResearchRequest) -> ResearchResponse:
        logger.info("Generating mocked research report for query=%s", request.query)

        sources = self._mock_sources()[: request.max_sources]
        article_summaries = self.summarization_service.summarize_articles(
            request=request,
            sources=sources,
            articles=[],
        )
        summary, report = self.summarization_service.build_report(
            request=request,
            sources=sources,
            articles=[],
            article_summaries=article_summaries,
            is_live_search=False,
        )

        return ResearchResponse(
            query=request.query,
            summary=summary,
            report=report,
            sources=sources,
            articles=[],
            article_summaries=article_summaries,
        )

    def list_history(
        self,
        db: Session,
        limit: int,
        user_id: str | None = None,
    ) -> list[ResearchHistoryItem]:
        return self.history_service.list_reports(db=db, limit=limit, user_id=user_id)

    def get_saved_report(self, db: Session, report_id: str) -> SavedReportResponse:
        return self.history_service.get_report(db=db, report_id=report_id)

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

    def _persist_response(
        self,
        db: Session,
        request: ResearchRequest,
        response: ResearchResponse,
    ) -> None:
        try:
            saved_ids = self.history_service.save_response(
                db=db,
                request=request,
                response=response,
            )
        except SQLAlchemyError as exc:
            db.rollback()
            msg = "Could not save research report"
            raise ResearchServiceError(msg) from exc

        response.query_id = saved_ids.query_id
        response.report_id = saved_ids.report_id
