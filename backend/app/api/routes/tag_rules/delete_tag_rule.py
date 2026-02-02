"""Delete tag rule endpoint."""

import uuid
from typing import Any

from fastapi import APIRouter, status

from app.api.deps import CurrentUser
from app.domains.tag_rules.usecases import provide_delete_tag_rule, provide_get_tag_rule

router = APIRouter()


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag_rule(
    current_user: CurrentUser,
    rule_id: uuid.UUID,
) -> None:
    """Delete a tag rule.

    Users can only delete their own tag rules unless they are superusers.
    """
    # Get the rule to check ownership first
    get_usecase = provide_get_tag_rule()
    rule = get_usecase.execute(rule_id)

    # Check ownership
    if not current_user.is_superuser and rule.user_id != current_user.id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this tag rule",
        )

    # Delete the rule
    delete_usecase = provide_delete_tag_rule()
    delete_usecase.execute(rule_id)
