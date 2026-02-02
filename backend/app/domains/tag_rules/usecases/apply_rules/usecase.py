"""Apply rules usecase."""

import uuid

from app.domains.tag_rules.domain.models import (
    ApplyRulesRequest,
    ApplyRulesResponse,
)
from app.domains.tag_rules.service import TagRuleService, provide_tag_rule_service


class ApplyRulesUseCase:
    """Usecase for applying tag rules to transactions."""

    def __init__(self, service: TagRuleService) -> None:
        """Initialize the usecase with a service."""
        self.service = service

    def execute(
        self, user_id: uuid.UUID, request: ApplyRulesRequest
    ) -> ApplyRulesResponse:
        """Execute the usecase to apply rules to transactions.

        Args:
            user_id: The user ID to apply rules for
            request: The apply rules request

        Returns:
            ApplyRulesResponse: The result of applying rules
        """
        return self.service.apply_rules(user_id, request)


def provide() -> ApplyRulesUseCase:
    """Provide an instance of ApplyRulesUseCase."""
    return ApplyRulesUseCase(provide_tag_rule_service())
