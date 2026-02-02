"""Legacy CRUD helpers.

These functions are used by the existing test suite and provide a thin wrapper
around the current domain models.

Important: these functions are *database-session injected* (caller provides the
SQLModel Session). No global engine access.
"""

from __future__ import annotations

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import User, UserCreate, UserUpdate


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """Return a user by email using the provided session."""
    return session.exec(select(User).where(User.email == email)).first()


def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create a user using the provided session."""
    db_obj = User.model_validate(
        user_create,
        update={"hashed_password": get_password_hash(user_create.password)},
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    """Authenticate user by email + password using the provided session."""
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    """Update an existing user using the provided session."""
    user_dict = user_in.model_dump(exclude_unset=True)
    extra_data: dict[str, object] = {}

    if "password" in user_dict and user_dict["password"]:
        extra_data["hashed_password"] = get_password_hash(str(user_dict["password"]))
        user_dict.pop("password", None)

    db_user.sqlmodel_update(user_dict, update=extra_data)  # pyright: ignore[reportUnknownArgumentType]
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
