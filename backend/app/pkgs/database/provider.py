"""Database provider implementation."""

from collections.abc import Generator

from sqlmodel import Session, create_engine

from app.core.config import settings

# Create SQLAlchemy engine
# Convert MultiHostUrl to string properly
database_url = settings.SQLALCHEMY_DATABASE_URI
engine = create_engine(database_url.unicode_string(), pool_pre_ping=True)


def get_db() -> Generator[Session, None, None]:
    """
    Get a database session.

    Yields:
        Session: A SQLModel session.
    """
    with Session(engine) as session:
        yield session


def get_db_session() -> Session:
    """
    Get a database session directly (not as a generator).

    Returns:
        Session: A SQLModel session.
    """
    return Session(engine)
