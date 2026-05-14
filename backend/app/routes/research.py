import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.research import (
    ResearchHistoryItem,
    ResearchRequest,
    ResearchResponse,
    SavedReportResponse,
)
from app.services.history import ReportNotFoundError
from app.services.research_service import ResearchService, ResearchServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["research"])


def get_research_service() -> ResearchService:
    return ResearchService()


@router.post(
    "",
    response_model=ResearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a research report",
)
def create_research_report(
    request: ResearchRequest,
    service: Annotated[ResearchService, Depends(get_research_service)],
    db: Annotated[Session, Depends(get_db)],
) -> ResearchResponse:
    try:
        return service.generate_report(request=request, db=db)
    except ResearchServiceError as exc:
        logger.exception("Research report generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Research report generation failed.",
        ) from exc


@router.get(
    "/history",
    response_model=list[ResearchHistoryItem],
    summary="List saved research reports",
)
def list_research_history(
    service: Annotated[ResearchService, Depends(get_research_service)],
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    user_id: str | None = None,
) -> list[ResearchHistoryItem]:
    return service.list_history(db=db, limit=limit, user_id=user_id)


@router.get(
    "/reports/{report_id}",
    response_model=SavedReportResponse,
    summary="Fetch a saved research report",
)
def get_research_report(
    report_id: str,
    service: Annotated[ResearchService, Depends(get_research_service)],
    db: Annotated[Session, Depends(get_db)],
) -> SavedReportResponse:
    try:
        return service.get_saved_report(db=db, report_id=report_id)
    except ReportNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research report not found.",
        ) from exc
