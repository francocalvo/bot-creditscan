"""Delete tag rule usecase."""

import uuid

from app.domains.tag_rules.service import TagRuleService, provide_tag_rule_service


class DeleteTagRuleUseCase:
    """Usecase for deleting a tag rule."""

    def __init__(self, service: TagRuleService) -> None:
        """Initialize the usecase with a service."""
        self.service = service

    def execute(self, rule_id: uuid.UUID) -> None:
        """Execute the usecase to delete a tag rule.

        Args:
            rule_id: The ID of the tag rule to delete
        """
        self.service.delete_tag_rule(rule_id)


def provide() -> DeleteTagRuleUseCase:
    """Provide an instance of DeleteTagRuleUseCase."""
    return DeleteTagRuleUseCase(provide_tag_rule_service())
