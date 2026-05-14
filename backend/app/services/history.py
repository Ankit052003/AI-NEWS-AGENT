from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.research import Article, Report, ResearchQuery, User
from app.schemas.research import (
    ResearchHistoryItem,
    ResearchRequest,
    ResearchResponse,
    ResearchSource,
    SavedArticle,
    SavedReportResponse,
)


@dataclass(frozen=True)
class SavedResearchIds:
    query_id: str
    report_id: str


class ReportNotFoundError(Exception):
    """Raised when a saved report does not exist."""


class ResearchHistoryService:
    def save_response(
        self,
        db: Session,
        request: ResearchRequest,
        response: ResearchResponse,
    ) -> SavedResearchIds:
        user = self._get_or_create_user(db, request.user_id)
        query = ResearchQuery(
            user_id=user.id if user else None,
            query=request.query,
            status="completed",
        )
        db.add(query)
        db.flush()

        extracted_articles = {
            str(article.url).rstrip("/"): article for article in response.articles
        }
        article_summaries = {
            summary.url.rstrip("/"): summary for summary in response.article_summaries
        }

        for index, source in enumerate(response.sources, start=1):
            url_key = str(source.url).rstrip("/")
            extracted_article = extracted_articles.get(url_key)
            article_summary = article_summaries.get(url_key)

            db.add(
                Article(
                    query_id=query.id,
                    source_index=index,
                    title=source.title,
                    url=str(source.url),
                    source=source.source,
                    snippet=source.snippet,
                    published_date=source.published_date,
                    extracted_text=(
                        extracted_article.extracted_text if extracted_article else None
                    ),
                    summary=article_summary.summary if article_summary else None,
                    word_count=extracted_article.word_count
                    if extracted_article
                    else None,
                ),
            )

        report = Report(
            query_id=query.id,
            title=self._build_report_title(request.query),
            summary=response.summary,
            report_content=response.report,
            generated_at=response.generated_at,
        )
        db.add(report)
        db.commit()
        db.refresh(query)
        db.refresh(report)

        return SavedResearchIds(query_id=query.id, report_id=report.id)

    def list_reports(
        self,
        db: Session,
        limit: int,
        user_id: str | None = None,
    ) -> list[ResearchHistoryItem]:
        statement = (
            select(Report)
            .join(Report.query)
            .options(selectinload(Report.query).selectinload(ResearchQuery.articles))
            .order_by(Report.generated_at.desc())
            .limit(limit)
        )
        if user_id:
            statement = statement.where(ResearchQuery.user_id == user_id)

        reports = db.scalars(statement).all()
        return [self._to_history_item(report) for report in reports]

    def get_report(self, db: Session, report_id: str) -> SavedReportResponse:
        statement = (
            select(Report)
            .where(Report.id == report_id)
            .options(selectinload(Report.query).selectinload(ResearchQuery.articles))
        )
        report = db.scalars(statement).one_or_none()
        if not report:
            raise ReportNotFoundError(report_id)

        articles = report.query.articles
        sources = [
            ResearchSource(
                title=article.title,
                url=article.url,
                source=article.source,
                snippet=article.snippet or "No snippet available.",
                published_date=article.published_date,
            )
            for article in articles
        ]

        return SavedReportResponse(
            id=report.id,
            query_id=report.query_id,
            query=report.query.query,
            title=report.title,
            summary=report.summary,
            report=report.report_content,
            status=report.query.status,
            sources=sources,
            articles=[
                SavedArticle(
                    id=article.id,
                    title=article.title,
                    url=article.url,
                    source=article.source,
                    snippet=article.snippet,
                    published_date=article.published_date,
                    extracted_text=article.extracted_text,
                    summary=article.summary,
                    word_count=article.word_count,
                    created_at=article.created_at,
                )
                for article in articles
            ],
            generated_at=report.generated_at,
        )

    def _get_or_create_user(self, db: Session, user_id: str | None) -> User | None:
        if not user_id:
            return None

        user = db.get(User, user_id)
        if user:
            return user

        user = User(id=user_id, name=user_id)
        db.add(user)
        db.flush()
        return user

    def _to_history_item(self, report: Report) -> ResearchHistoryItem:
        articles = report.query.articles
        extracted_count = sum(1 for article in articles if article.extracted_text)

        return ResearchHistoryItem(
            id=report.id,
            query_id=report.query_id,
            query=report.query.query,
            title=report.title,
            summary=report.summary,
            status=report.query.status,
            source_count=len(articles),
            article_count=extracted_count,
            generated_at=report.generated_at,
        )

    def _build_report_title(self, query: str) -> str:
        title = " ".join(query.split())
        if len(title) <= 90:
            return title

        return f"{title[:87].rstrip()}..."
