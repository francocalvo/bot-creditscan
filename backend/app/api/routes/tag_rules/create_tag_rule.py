"""Create tag rule endpoint."""

from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.domains.tag_rules.domain.models import TagRuleCreateIn, TagRulePublic
from app.domains.tag_rules.usecases import provide_create_tag_rule

router = APIRouter()


@router.post("/", response_model=TagRulePublic, status_code=201)
def create_tag_rule(
    current_user: CurrentUser,
    tag_rule_data_in: TagRuleCreateIn,
) -> Any:
    """Create a new tag rule."""
    usecase = provide_create_tag_rule()

    # Convert API input to domain model with server-side user_id
    tag_rule_data = tag_rule_data_in.to_create(current_user.id)

    return usecase.execute(tag_rule_data)
