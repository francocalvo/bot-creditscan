"""Tag rule repository implementation."""

import builtins
import uuid
from typing import Any

from sqlmodel import Session, func, select

from app.domains.tag_rules.domain.errors import TagRuleNotFoundError
from app.domains.tag_rules.domain.models import TagRule, TagRuleCreate, TagRuleUpdate
from app.pkgs.database import get_db_session


class TagRuleRepository:
    """Repository for tag rules."""

    def __init__(self, db_session: Session):
        """Initialize the repository with a database session."""
        self.db_session = db_session

    def create(self, rule_data: TagRuleCreate) -> TagRule:
        """Create a new tag rule."""
        rule = TagRule.model_validate(rule_data)
        self.db_session.add(rule)
        self.db_session.commit()
        self.db_session.refresh(rule)
        return rule

    def get_by_id(self, rule_id: uuid.UUID) -> TagRule:
        """Get a tag rule by ID."""
        rule = self.db_session.get(TagRule, rule_id)
        if not rule:
            raise TagRuleNotFoundError(f"Tag rule with ID {rule_id} not found")
        return rule

    def list(
        self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None
    ) -> list[TagRule]:
        """List tag rules with pagination and filtering."""
        query = select(TagRule)

        if filters:
            for field, value in filters.items():
                if hasattr(TagRule, field):
                    query = query.where(getattr(TagRule, field) == value)

        result = self.db_session.exec(query.offset(skip).limit(limit))
        return list(result)

    def list_applicable_for_user(
        self, user_id: uuid.UUID, enabled_only: bool = True
    ) -> builtins.list[TagRule]:
        """List applicable tag rules for a user, ordered by priority and created_at."""
        query = select(TagRule).where(TagRule.user_id == user_id)

        if enabled_only:
            query = query.where(TagRule.enabled)

        # Order by priority (lower first), then created_at
        query = query.order_by(TagRule.priority.asc(), TagRule.created_at.asc())

        result = self.db_session.exec(query)
        return list(result)

    def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count tag rules with optional filtering."""
        query = select(TagRule)

        if filters:
            for field, value in filters.items():
                if hasattr(TagRule, field):
                    query = query.where(getattr(TagRule, field) == value)

        count_q = (
            query.with_only_columns(func.count())
            .order_by(None)
            .select_from(query.get_final_froms()[0])
        )

        result = self.db_session.exec(count_q)
        for count in result:
            return count  # type: ignore
        return 0

    def update(self, rule_id: uuid.UUID, rule_data: TagRuleUpdate) -> TagRule:
        """Update a tag rule."""
        rule = self.get_by_id(rule_id)

        update_dict = rule_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(rule, field, value)

        self.db_session.add(rule)
        self.db_session.commit()
        self.db_session.refresh(rule)
        return rule

    def delete(self, rule_id: uuid.UUID) -> None:
        """Delete a tag rule."""
        rule = self.get_by_id(rule_id)
        self.db_session.delete(rule)
        self.db_session.commit()


def provide() -> TagRuleRepository:
    """Provide an instance of TagRuleRepository."""
    return TagRuleRepository(get_db_session())
