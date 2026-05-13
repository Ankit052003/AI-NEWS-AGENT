from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "News Research Agent"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"

    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    search_api_key: str | None = None
    search_provider: str = "newsapi"
    search_api_base_url: str = "https://newsapi.org/v2/everything"
    search_language: str = "en"
    search_sort_by: str = "relevancy"
    search_timeout_seconds: int = Field(default=10, ge=1, le=60)
    content_extraction_timeout_seconds: int = Field(default=10, ge=1, le=60)
    content_extraction_min_words: int = Field(default=80, ge=1, le=500)
    content_extraction_user_agent: str = "NewsResearchAgent/0.1"

    default_llm_provider: str = "mock"
    default_model: str = "mock-news-researcher"
    default_max_sources: int = Field(default=5, ge=1, le=20)

    database_url: str | None = None
    redis_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
