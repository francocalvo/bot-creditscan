"""Tag service implementation."""

import uuid
from typing import Any

from app.domains.tags.domain.errors import DuplicateTagLabelError
from app.domains.tags.domain.models import (
    TagCreate,
    TagPublic,
    TagsPublic,
    TagUpdate,
)
from app.domains.tags.repository import TagRepository
from app.domains.tags.repository import provide as provide_repository


class TagService:
    """Service for tags."""

    def __init__(self, repository: TagRepository):
        """Initialize the service with a repository."""
        self.repository = repository

    def create_tag(self, tag_data: TagCreate) -> TagPublic:
        """Create a new tag.

        Raises:
            DuplicateTagLabelError: If a tag with the same label exists for user.
        """
        # Check for duplicate label
        existing = self.repository.get_by_user_and_label(
            tag_data.user_id, tag_data.label
        )
        if existing:
            raise DuplicateTagLabelError(
                f"Tag with label '{tag_data.label}' already exists for this user"
            )

        tag = self.repository.create(tag_data)
        return TagPublic.model_validate(tag)

    def get_tag(self, tag_id: uuid.UUID) -> TagPublic:
        """Get a tag by ID."""
        tag = self.repository.get_by_id(tag_id)
        return TagPublic.model_validate(tag)

    def list_tags(
        self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None
    ) -> TagsPublic:
        """List tags with pagination and filtering."""
        tags = self.repository.list(skip=skip, limit=limit, filters=filters)
        count = self.repository.count(filters=filters)

        return TagsPublic(
            data=[TagPublic.model_validate(t) for t in tags],
            count=count,
        )

    def update_tag(self, tag_id: uuid.UUID, tag_data: TagUpdate) -> TagPublic:
        """Update a tag."""
        tag = self.repository.update(tag_id, tag_data)
        return TagPublic.model_validate(tag)

    def delete_tag(self, tag_id: uuid.UUID) -> None:
        """Delete a tag and its associated tag rules."""
        # Import here to avoid circular imports
        from app.domains.tag_rules.repository import provide_tag_rule_repository

        # Delete associated tag rules first
        tag_rule_repo = provide_tag_rule_repository()
        rules = tag_rule_repo.list(filters={"tag_id": tag_id})
        for rule in rules:
            tag_rule_repo.delete(rule.id)

        # Then delete the tag
        self.repository.delete(tag_id)


def provide(repository: TagRepository | None = None) -> TagService:
    """Provide an instance of TagService.

    Args:
        repository: Optional repository to use.
    """
    repo = repository if repository is not None else provide_repository()
    return TagService(repo)
