"""Tag rule domain errors."""


class TagRuleError(Exception):
    """Base exception for tag rule errors."""

    pass


class TagRuleNotFoundError(TagRuleError):
    """Raised when a tag rule is not found."""

    pass


class InvalidTagRuleDataError(TagRuleError):
    """Raised when tag rule data is invalid."""

    pass


class TagRuleOwnershipError(TagRuleError):
    """Raised when tag rule ownership validation fails."""

    pass


class RuleEvaluationError(TagRuleError):
    """Raised when rule evaluation fails."""

    pass
