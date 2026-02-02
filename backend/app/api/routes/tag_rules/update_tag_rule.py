"""Update tag rule endpoint."""

import uuid
from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.domains.tag_rules.domain.models import TagRulePublic, TagRuleUpdateIn
from app.domains.tag_rules.usecases import provide_get_tag_rule, provide_update_tag_rule

router = APIRouter()


@router.patch("/{rule_id}", response_model=TagRulePublic)
def update_tag_rule(
    current_user: CurrentUser,
    rule_id: uuid.UUID,
    tag_rule_data_in: TagRuleUpdateIn,
) -> Any:
    """Update a tag rule.

    Users can only update their own tag rules unless they are superusers.
    """
    # Get the rule to check ownership first
    get_usecase = provide_get_tag_rule()
    rule = get_usecase.execute(rule_id)

    # Check ownership
    if not current_user.is_superuser and rule.user_id != current_user.id:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this tag rule",
        )

    # Convert API input to domain model
    tag_rule_data = tag_rule_data_in.to_update()

    # Update the rule
    update_usecase = provide_update_tag_rule()
    return update_usecase.execute(rule_id, tag_rule_data)
