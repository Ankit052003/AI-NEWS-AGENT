from datetime import UTC, date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.search import SearchResult


class DateRange(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    @model_validator(mode="after")
    def validate_date_order(self) -> "DateRange":
        if self.start_date and self.end_date and self.start_date > self.end_date:
            msg = "start_date must be before or equal to end_date"
            raise ValueError(msg)

        return self


class ResearchRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The research question the user wants answered.",
        examples=["Latest AI startup funding news this week"],
    )
    user_id: str | None = Field(
        default=None,
        max_length=100,
        description="Optional user identifier for future report history.",
    )
    max_sources: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Maximum number of sources to collect for the report.",
    )
    date_range: DateRange | None = Field(
        default=None,
        description="Optional date range to guide search in later phases.",
    )


class ResearchSource(SearchResult):
    pass


class ResearchResponse(BaseModel):
    query: str
    summary: str
    report: str
    sources: list[ResearchSource]
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
