"""Get tag rule usecase."""

import uuid

from app.domains.tag_rules.domain.models import TagRulePublic
from app.domains.tag_rules.service import TagRuleService, provide_tag_rule_service


class GetTagRuleUseCase:
    """Usecase for getting a tag rule by ID."""

    def __init__(self, service: TagRuleService) -> None:
        """Initialize the usecase with a service."""
        self.service = service

    def execute(self, rule_id: uuid.UUID) -> TagRulePublic:
        """Execute the usecase to get a tag rule.

        Args:
            rule_id: The ID of the tag rule to get

        Returns:
            TagRulePublic: The tag rule
        """
        return self.service.get_tag_rule(rule_id)


def provide() -> GetTagRuleUseCase:
    """Provide an instance of GetTagRuleUseCase."""
    return GetTagRuleUseCase(provide_tag_rule_service())
