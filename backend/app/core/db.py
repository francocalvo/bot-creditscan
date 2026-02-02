"""Database bootstrap utilities.

Important: this module avoids creating a Postgres engine at import time.
Tests may run without libpq installed, using SQLite in-memory.
"""

from __future__ import annotations

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel

from app.core.config import settings
from app.domains.users.domain import UserCreate
from app.domains.users.repository import provide as provide_user_repository
from app.domains.users.service import provide as provide_user_service
from app.domains.users.usecases.create_user import CreateUserUseCase
from app.pkgs.database import get_engine


def init_db(
    *,
    db_engine: Engine | None = None,
    create_initial_data: bool = True,
) -> None:
    """Initialize database with tables and (optionally) the first superuser.

    Args:
        db_engine: Optional engine to use. If not provided, uses the global engine.
        create_initial_data: If True, creates the first superuser (when missing).
                             Tests should pass False.
    """
    target_engine = db_engine if db_engine is not None else get_engine()

    # Create all tables
    SQLModel.metadata.create_all(target_engine)

    if not create_initial_data:
        return

    with Session(target_engine) as session:
        user_repo = provide_user_repository(db_session=session)
        user_service = provide_user_service(user_repository=user_repo)

        existing_user = user_service.get_user_by_email(settings.FIRST_SUPERUSER)
        if existing_user:
            return

        create_user_usecase = CreateUserUseCase(user_service)
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        create_user_usecase.execute(user_in, send_welcome_email=False)
