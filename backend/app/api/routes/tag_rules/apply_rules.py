"""Apply rules endpoint."""

from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.domains.tag_rules.domain.models import ApplyRulesRequest, ApplyRulesResponse
from app.domains.tag_rules.usecases import provide_apply_rules

router = APIRouter()


@router.post("/apply", response_model=ApplyRulesResponse)
def apply_rules(
    current_user: CurrentUser,
    request: ApplyRulesRequest,
) -> Any:
    """Apply tag rules to transactions.

    Applies enabled tag rules to transactions matching the given filters.
    Non-superusers can only apply rules for their own transactions.
    """
    usecase = provide_apply_rules()
    return usecase.execute(current_user.id, request)
