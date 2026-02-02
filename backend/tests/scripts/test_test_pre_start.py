from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

from sqlmodel import select

from tests_pre_start import init, logger


def test_init_successful_connection() -> None:
    # Use an in-memory SQLite engine to verify init() can open a session and execute.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    # Should not raise
    init(engine)
