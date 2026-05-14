"""initial research history schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-15 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=100), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "research_queries",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=True),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_memory",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=100), nullable=False),
        sa.Column("interest_topics", sa.Text(), nullable=True),
        sa.Column("research_history", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "articles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("query_id", sa.String(length=36), nullable=False),
        sa.Column("source_index", sa.Integer(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("snippet", sa.Text(), nullable=True),
        sa.Column("published_date", sa.Date(), nullable=True),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("word_count", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["query_id"], ["research_queries.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "reports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("query_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("report_content", sa.Text(), nullable=False),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["query_id"], ["research_queries.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("query_id"),
    )


def downgrade() -> None:
    op.drop_table("reports")
    op.drop_table("articles")
    op.drop_table("user_memory")
    op.drop_table("research_queries")
    op.drop_table("users")
