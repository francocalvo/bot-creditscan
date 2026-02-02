"""List tag rules endpoint."""

import uuid
from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.domains.tag_rules.domain.models import TagRulesPublic
from app.domains.tag_rules.usecases import provide_list_tag_rules

router = APIRouter()


@router.get("/", response_model=TagRulesPublic)
def list_tag_rules(
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    user_id: uuid.UUID | None = None,
    enabled: bool | None = None,
) -> Any:
    """Retrieve tag rules.

    By default, returns the current user's tag rules. Superusers can filter by user_id.
    """
    usecase = provide_list_tag_rules()

    # If user_id is not provided, use current user's ID
    # If user_id is provided but user is not superuser, only show their own rules
    filter_user_id = (
        user_id if (user_id and current_user.is_superuser) else current_user.id
    )

    filters: dict[str, Any] = {"user_id": filter_user_id}
    if enabled is not None:
        filters["enabled"] = enabled

    return usecase.execute(skip=skip, limit=limit, filters=filters)
