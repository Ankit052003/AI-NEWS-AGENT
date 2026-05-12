from datetime import date

from pydantic import BaseModel, HttpUrl


class SearchResult(BaseModel):
    title: str
    url: HttpUrl
    source: str
    snippet: str
    published_date: date | None = None
