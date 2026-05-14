from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _connect_args(database_url: str) -> dict[str, bool]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}

    return {}


settings = get_settings()
engine = create_engine(
    settings.database_url,
    connect_args=_connect_args(settings.database_url),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
_tables_ready = False


def create_db_and_tables() -> None:
    import app.models.research  # noqa: F401

    Base.metadata.create_all(bind=engine)


def ensure_db_ready() -> None:
    global _tables_ready

    if _tables_ready:
        return

    create_db_and_tables()
    _tables_ready = True


def get_db() -> Generator[Session]:
    ensure_db_ready()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
