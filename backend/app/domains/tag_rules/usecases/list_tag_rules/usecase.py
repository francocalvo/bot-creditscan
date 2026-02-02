"""List tag rules usecase."""

from typing import Any

from app.domains.tag_rules.domain.models import TagRulesPublic
from app.domains.tag_rules.service import TagRuleService, provide_tag_rule_service


class ListTagRulesUseCase:
    """Usecase for listing tag rules with pagination."""

    def __init__(self, service: TagRuleService) -> None:
        """Initialize the usecase with a service."""
        self.service = service

    def execute(
        self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None
    ) -> TagRulesPublic:
        """Execute the usecase to list tag rules.

        Args:
            skip: Number of records to skip
            limit: Number of records to return
            filters: Optional filters to apply

        Returns:
            TagRulesPublic: Paginated tag rules data
        """
        return self.service.list_tag_rules(skip=skip, limit=limit, filters=filters)


def provide() -> ListTagRulesUseCase:
    """Provide an instance of ListTagRulesUseCase."""
    return ListTagRulesUseCase(provide_tag_rule_service())
