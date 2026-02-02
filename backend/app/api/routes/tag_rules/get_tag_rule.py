"""Get tag rule endpoint."""

import uuid
from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.domains.tag_rules.domain.models import TagRulePublic
from app.domains.tag_rules.usecases import provide_get_tag_rule

router = APIRouter()


@router.get("/{rule_id}", response_model=TagRulePublic)
def get_tag_rule(
    current_user: CurrentUser,
    rule_id: uuid.UUID,
) -> Any:
    """Get a tag rule by ID.

    Users can only access their own tag rules unless they are superusers.
    """
    usecase = provide_get_tag_rule()
    rule = usecase.execute(rule_id)

    # Check ownership
    if not current_user.is_superuser and rule.user_id != current_user.id:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this tag rule",
        )

    return rule
