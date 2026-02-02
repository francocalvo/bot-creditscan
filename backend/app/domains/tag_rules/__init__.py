"""Tag rule domain module."""

from .domain import (
    ApplyRulesRequest,
    ApplyRulesResponse,
    InvalidTagRuleDataError,
    RuleEvaluationError,
    TagRule,
    TagRuleBase,
    TagRuleCreate,
    TagRuleError,
    TagRuleNotFoundError,
    TagRuleOwnershipError,
    TagRulePublic,
    TagRulesPublic,
    TagRuleUpdate,
)
from .repository import TagRuleRepository, provide_tag_rule_repository
from .service import TagRuleService, provide_tag_rule_service

__all__ = [
    "TagRule",
    "TagRuleBase",
    "TagRuleCreate",
    "TagRuleError",
    "TagRuleNotFoundError",
    "TagRulePublic",
    "TagRulesPublic",
    "TagRuleUpdate",
    "InvalidTagRuleDataError",
    "TagRuleOwnershipError",
    "RuleEvaluationError",
    "ApplyRulesRequest",
    "ApplyRulesResponse",
    "TagRuleRepository",
    "TagRuleService",
    "provide_tag_rule_repository",
    "provide_tag_rule_service",
]
