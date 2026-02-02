from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, delete

from app.core.config import settings
from app.core.db import init_db
from app.main import app
from app.models import User
from tests.utils.user import authentication_token_from_email
from tests.utils.utils import get_superuser_token_headers


@pytest.fixture(scope="session")
def test_engine() -> Engine:
    """Create an in-memory SQLite database for testing.

    This fixture creates a fresh SQLite database at session scope,
    allowing tests to run quickly without external dependencies.
    """
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    # Inject the engine globally for domain-layer providers that open their own sessions.
    # This is not a mock: it's explicit DB injection for tests.
    from app.pkgs.database import provider as db_provider

    db_provider._engine = engine  # type: ignore[attr-defined]

    # Create baseline data expected by the API tests (first superuser).
    from app.core.db import init_db

    init_db(db_engine=engine, create_initial_data=True)

    return engine


@pytest.fixture(scope="function")
def db(test_engine: Engine) -> Generator[Session, None, None]:
    """Create a database session using the test engine.

    Each test function gets a fresh session with a transaction
    that rolls back automatically.
    """
    with Session(test_engine) as session:
        # Ensure tables + baseline users exist for each test.
        init_db(db_engine=test_engine, create_initial_data=True)
        yield session

        # Clean up: delete all users created by the test, but keep the baseline superuser.
        statement = delete(User).where(User.email != settings.FIRST_SUPERUSER)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client(test_engine: Engine) -> Generator[TestClient, None, None]:
    # Ensure FastAPI routes use the same test database.
    from app.api import deps

    def _override_get_db() -> Generator[Session, None, None]:
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[deps.get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="function")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
