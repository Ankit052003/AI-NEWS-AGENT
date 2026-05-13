from datetime import UTC, date, datetime

from pydantic import BaseModel, Field, HttpUrl


class ExtractedArticle(BaseModel):
    title: str
    url: HttpUrl
    source: str
    extracted_text: str
    word_count: int = Field(ge=1)
    author: str | None = None
    published_date: date | None = None
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
