import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.research import ResearchRequest, ResearchResponse
from app.services.research_service import ResearchService, ResearchServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["research"])


def get_research_service() -> ResearchService:
    return ResearchService()


@router.post(
    "",
    response_model=ResearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate a mocked research report",
)
def create_research_report(
    request: ResearchRequest,
    service: Annotated[ResearchService, Depends(get_research_service)],
) -> ResearchResponse:
    try:
        return service.generate_mock_report(request)
    except ResearchServiceError as exc:
        logger.exception("Research report generation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Research report generation failed.",
        ) from exc
