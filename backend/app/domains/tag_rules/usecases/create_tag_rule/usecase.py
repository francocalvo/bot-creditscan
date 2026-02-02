"""Create tag rule usecase."""

from app.domains.tag_rules.domain.models import TagRuleCreate, TagRulePublic
from app.domains.tag_rules.service import TagRuleService, provide_tag_rule_service


class CreateTagRuleUseCase:
    """Usecase for creating a tag rule."""

    def __init__(self, service: TagRuleService) -> None:
        """Initialize the usecase with a service."""
        self.service = service

    def execute(self, tag_rule_data: TagRuleCreate) -> TagRulePublic:
        """Execute the usecase to create a tag rule.

        Args:
            tag_rule_data: The tag rule data to create

        Returns:
            TagRulePublic: The created tag rule
        """
        return self.service.create_tag_rule(tag_rule_data)


def provide() -> CreateTagRuleUseCase:
    """Provide an instance of CreateTagRuleUseCase."""
    return CreateTagRuleUseCase(provide_tag_rule_service())
