"""Update tag rule usecase."""

import uuid

from app.domains.tag_rules.domain.models import TagRulePublic, TagRuleUpdate
from app.domains.tag_rules.service import TagRuleService, provide_tag_rule_service


class UpdateTagRuleUseCase:
    """Usecase for updating a tag rule."""

    def __init__(self, service: TagRuleService) -> None:
        """Initialize the usecase with a service."""
        self.service = service

    def execute(
        self, rule_id: uuid.UUID, tag_rule_data: TagRuleUpdate
    ) -> TagRulePublic:
        """Execute the usecase to update a tag rule.

        Args:
            rule_id: The ID of the tag rule to update
            tag_rule_data: The tag rule data to update

        Returns:
            TagRulePublic: The updated tag rule
        """
        return self.service.update_tag_rule(rule_id, tag_rule_data)


def provide() -> UpdateTagRuleUseCase:
    """Provide an instance of UpdateTagRuleUseCase."""
    return UpdateTagRuleUseCase(provide_tag_rule_service())
