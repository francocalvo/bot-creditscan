"""Tag rule service."""

from .tag_rule_service import TagRuleService
from .tag_rule_service import provide as provide_tag_rule_service

__all__ = ["TagRuleService", "provide_tag_rule_service"]
