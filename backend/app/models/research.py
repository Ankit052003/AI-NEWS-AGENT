from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utc_now() -> datetime:
    return datetime.now(UTC)


def _new_id() -> str:
    return str(uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        nullable=False,
    )

    queries: Mapped[list[ResearchQuery]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    memory: Mapped[UserMemory | None] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )


class ResearchQuery(Base):
    __tablename__ = "research_queries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="completed", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        nullable=False,
    )

    user: Mapped[User | None] = relationship(back_populates="queries")
    articles: Mapped[list[Article]] = relationship(
        back_populates="query",
        cascade="all, delete-orphan",
        order_by="Article.source_index",
    )
    report: Mapped[Report | None] = relationship(
        back_populates="query",
        cascade="all, delete-orphan",
        uselist=False,
    )


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    query_id: Mapped[str] = mapped_column(ForeignKey("research_queries.id"))
    source_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    published_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        nullable=False,
    )

    query: Mapped[ResearchQuery] = relationship(back_populates="articles")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    query_id: Mapped[str] = mapped_column(
        ForeignKey("research_queries.id"),
        unique=True,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    report_content: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        nullable=False,
    )

    query: Mapped[ResearchQuery] = relationship(back_populates="report")


class UserMemory(Base):
    __tablename__ = "user_memory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_id)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )
    interest_topics: Mapped[str | None] = mapped_column(Text, nullable=True)
    research_history: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
        nullable=False,
    )

    user: Mapped[User] = relationship(back_populates="memory")
