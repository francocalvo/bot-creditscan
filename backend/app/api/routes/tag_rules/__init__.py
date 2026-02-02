"""Tag rules routes module."""

from fastapi import APIRouter

from .apply_rules import router as apply_rules_router
from .create_tag_rule import router as create_tag_rule_router
from .delete_tag_rule import router as delete_tag_rule_router
from .get_tag_rule import router as get_tag_rule_router
from .list_tag_rules import router as list_tag_rules_router
from .update_tag_rule import router as update_tag_rule_router

router = APIRouter(prefix="/tag-rules", tags=["tag-rules"])

router.include_router(list_tag_rules_router)
router.include_router(create_tag_rule_router)
router.include_router(get_tag_rule_router)
router.include_router(update_tag_rule_router)
router.include_router(delete_tag_rule_router)
router.include_router(apply_rules_router)

__all__ = ["router"]
