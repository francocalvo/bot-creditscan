"""Tag rule usecases."""

from .apply_rules import ApplyRulesUseCase
from .apply_rules import provide as provide_apply_rules
from .create_tag_rule import CreateTagRuleUseCase
from .create_tag_rule import provide as provide_create_tag_rule
from .delete_tag_rule import DeleteTagRuleUseCase
from .delete_tag_rule import provide as provide_delete_tag_rule
from .get_tag_rule import GetTagRuleUseCase
from .get_tag_rule import provide as provide_get_tag_rule
from .list_tag_rules import ListTagRulesUseCase
from .list_tag_rules import provide as provide_list_tag_rules
from .update_tag_rule import UpdateTagRuleUseCase
from .update_tag_rule import provide as provide_update_tag_rule

__all__ = [
    "ListTagRulesUseCase",
    "provide_list_tag_rules",
    "CreateTagRuleUseCase",
    "provide_create_tag_rule",
    "GetTagRuleUseCase",
    "provide_get_tag_rule",
    "UpdateTagRuleUseCase",
    "provide_update_tag_rule",
    "DeleteTagRuleUseCase",
    "provide_delete_tag_rule",
    "ApplyRulesUseCase",
    "provide_apply_rules",
]
