"""Get user by ID endpoint."""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser
from app.domains.users.domain.errors import UserNotFoundError
from app.domains.users.domain.models import UserPublic
from app.domains.users.service import provide as provide_user_service

router = APIRouter()


@router.get("/{user_id}", response_model=UserPublic)
def get_user_by_id(user_id: uuid.UUID, current_user: CurrentUser) -> Any:
    """Get a specific user by id."""
    # Check privileges BEFORE loading the target user.
    # Non-superusers may only fetch their own profile.
    if not current_user.is_superuser and user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )

    try:
        service = provide_user_service()
        user = service.get_user(user_id)
        return user
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
