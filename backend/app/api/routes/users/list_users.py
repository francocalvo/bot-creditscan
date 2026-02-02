"""List users endpoint."""

from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_active_superuser
from app.domains.users.domain.models import UsersPublic
from app.domains.users.usecases.search_users import provide as provide_search_users

router = APIRouter()


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def list_users(skip: int = 0, limit: int = 100) -> Any:
    """List all users (superuser only)."""
    usecase = provide_search_users()
    return usecase.execute(skip=skip, limit=limit)
