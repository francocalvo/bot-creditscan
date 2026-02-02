"""Create tag endpoint."""

from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.deps import CurrentUser
from app.domains.tags.domain.errors import InvalidTagDataError
from app.domains.tags.domain.models import TagCreateIn, TagPublic
from app.domains.tags.usecases.create_tag import provide as provide_create_tag

router = APIRouter()


@router.post("/", response_model=TagPublic, status_code=201)
def create_tag(
    tag_in: TagCreateIn,
    current_user: CurrentUser,
) -> Any:
    """Create a new tag.

    Users can only create tags for themselves.
    Superusers can create tags for any user.
    """
    # Convert API input to domain model with server-side user_id
    # Non-superusers always create tags for themselves.
    user_id = current_user.id
    if current_user.is_superuser and tag_in.user_id is not None:
        user_id = tag_in.user_id
    elif not current_user.is_superuser and tag_in.user_id not in (
        None,
        current_user.id,
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only create tags for yourself",
        )

    tag_data = tag_in.to_create(user_id)

    try:
        usecase = provide_create_tag()
        return usecase.execute(tag_data)
    except InvalidTagDataError as e:
        raise HTTPException(status_code=400, detail=str(e))
