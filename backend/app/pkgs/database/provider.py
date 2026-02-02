"""Database provider implementation.

This module intentionally avoids creating a database engine at import time.
That keeps tests lightweight (e.g. SQLite in-memory) and avoids requiring
Postgres/libpq just to import application modules.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from app.core.config import settings

_engine: Engine | None = None


def get_engine() -> Engine:
    """Return the global application engine (created lazily)."""
    global _engine
    if _engine is None:
        database_url = settings.SQLALCHEMY_DATABASE_URI
        _engine = create_engine(database_url.unicode_string(), pool_pre_ping=True)
    return _engine


def get_db(engine_arg: Engine | None = None) -> Generator[Session, None, None]:
    """Get a database session.

    Args:
        engine_arg: Optional engine to use. If not provided, uses the global engine.

    Yields:
        Session: A SQLModel session.
    """
    db_engine = engine_arg if engine_arg is not None else get_engine()
    with Session(db_engine) as session:
        yield session


def get_db_session(engine_arg: Engine | None = None) -> Session:
    """Get a database session directly (not as a generator).

    Args:
        engine_arg: Optional engine to use. If not provided, uses the global engine.

    Returns:
        Session: A SQLModel session.
    """
    db_engine = engine_arg if engine_arg is not None else get_engine()
    return Session(db_engine)
