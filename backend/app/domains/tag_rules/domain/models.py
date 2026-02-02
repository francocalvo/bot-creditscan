"""Tag rule domain models."""

import re
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import field_validator, model_validator
from sqlmodel import Field, SQLModel


# Base model with shared properties
class TagRuleBase(SQLModel):
    """Base model for tag rules."""

    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    tag_id: uuid.UUID = Field(foreign_key="tags.tag_id", index=True)
    name: str | None = Field(default=None, max_length=200)
    enabled: bool = Field(default=True)
    priority: int = Field(default=100)

    # Match inputs (nullable)
    payee_contains: str | None = Field(default=None, max_length=200)
    description_contains: str | None = Field(default=None, max_length=500)
    payee_regex: str | None = Field(default=None, max_length=500)
    description_regex: str | None = Field(default=None, max_length=500)
    amount_min: Decimal | None = Field(default=None, decimal_places=2, max_digits=32)
    amount_max: Decimal | None = Field(default=None, decimal_places=2, max_digits=32)
    currency: str | None = Field(default=None, max_length=3)


# For creating new records
class TagRuleCreate(TagRuleBase):
    """Model for creating tag rule."""

    @field_validator("payee_regex", "description_regex", mode="before")
    @classmethod
    def validate_regex(cls, v: str | None) -> str | None:
        """Validate that regex patterns are valid."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v

    @model_validator(mode="after")
    def validate_at_least_one_condition(self) -> "TagRuleCreate":
        """Validate that at least one match condition is set."""
        conditions = [
            self.payee_contains,
            self.description_contains,
            self.payee_regex,
            self.description_regex,
            self.amount_min,
            self.amount_max,
            self.currency,
        ]
        if all(c is None for c in conditions):
            raise ValueError("At least one match condition must be set")
        return self


# Database table model
class TagRule(TagRuleBase, table=True):
    """Database model for tag rules."""

    __tablename__ = "tag_rules"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Public API response model
class TagRulePublic(TagRuleBase):
    """Public model for tag rules."""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# For updates (all fields optional)
class TagRuleUpdate(SQLModel):
    """Model for updating tag rule."""

    name: str | None = Field(default=None, max_length=200)
    tag_id: uuid.UUID | None = None  # Allow tag reassignment
    enabled: bool | None = None
    priority: int | None = None
    payee_contains: str | None = Field(default=None, max_length=200)
    description_contains: str | None = Field(default=None, max_length=500)
    payee_regex: str | None = Field(default=None, max_length=500)
    description_regex: str | None = Field(default=None, max_length=500)
    amount_min: Decimal | None = Field(default=None, decimal_places=2, max_digits=32)
    amount_max: Decimal | None = Field(default=None, decimal_places=2, max_digits=32)
    currency: str | None = Field(default=None, max_length=3)

    @field_validator("payee_regex", "description_regex", mode="before")
    @classmethod
    def validate_regex(cls, v: str | None) -> str | None:
        """Validate that regex patterns are valid."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v


# API input models (user_id set server-side)
class TagRuleCreateIn(SQLModel):
    """API input model for creating tag rule (user_id set server-side)."""

    tag_id: uuid.UUID
    name: str | None = Field(default=None, max_length=200)
    enabled: bool = Field(default=True)
    priority: int = Field(default=100)
    payee_contains: str | None = Field(default=None, max_length=200)
    description_contains: str | None = Field(default=None, max_length=500)
    payee_regex: str | None = Field(default=None, max_length=500)
    description_regex: str | None = Field(default=None, max_length=500)
    amount_min: Decimal | None = Field(default=None, decimal_places=2, max_digits=32)
    amount_max: Decimal | None = Field(default=None, decimal_places=2, max_digits=32)
    currency: str | None = Field(default=None, max_length=3)

    @field_validator("payee_regex", "description_regex", mode="before")
    @classmethod
    def validate_regex(cls, v: str | None) -> str | None:
        """Validate that regex patterns are valid."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v

    @model_validator(mode="after")
    def validate_at_least_one_condition(self) -> "TagRuleCreateIn":
        """Validate that at least one match condition is set."""
        conditions = [
            self.payee_contains,
            self.description_contains,
            self.payee_regex,
            self.description_regex,
            self.amount_min,
            self.amount_max,
            self.currency,
        ]
        if all(c is None for c in conditions):
            raise ValueError("At least one match condition must be set")
        return self

    def to_create(self, user_id: uuid.UUID) -> TagRuleCreate:
        """Convert to TagRuleCreate with server-side user_id."""
        return TagRuleCreate(
            user_id=user_id,
            tag_id=self.tag_id,
            name=self.name,
            enabled=self.enabled,
            priority=self.priority,
            payee_contains=self.payee_contains,
            description_contains=self.description_contains,
            payee_regex=self.payee_regex,
            description_regex=self.description_regex,
            amount_min=self.amount_min,
            amount_max=self.amount_max,
            currency=self.currency,
        )


# API input model for updates (no user_id needed)
class TagRuleUpdateIn(SQLModel):
    """API input model for updating tag rule."""

    name: str | None = Field(default=None, max_length=200)
    tag_id: uuid.UUID | None = None  # Allow tag reassignment
    enabled: bool | None = None
    priority: int | None = None
    payee_contains: str | None = Field(default=None, max_length=200)
    description_contains: str | None = Field(default=None, max_length=500)
    payee_regex: str | None = Field(default=None, max_length=500)
    description_regex: str | None = Field(default=None, max_length=500)
    amount_min: Decimal | None = Field(default=None, decimal_places=2, max_digits=32)
    amount_max: Decimal | None = Field(default=None, decimal_places=2, max_digits=32)
    currency: str | None = Field(default=None, max_length=3)

    @field_validator("payee_regex", "description_regex", mode="before")
    @classmethod
    def validate_regex(cls, v: str | None) -> str | None:
        """Validate that regex patterns are valid."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v

    def to_update(self) -> TagRuleUpdate:
        """Convert to TagRuleUpdate."""
        return TagRuleUpdate(
            name=self.name,
            tag_id=self.tag_id,
            enabled=self.enabled,
            priority=self.priority,
            payee_contains=self.payee_contains,
            description_contains=self.description_contains,
            payee_regex=self.payee_regex,
            description_regex=self.description_regex,
            amount_min=self.amount_min,
            amount_max=self.amount_max,
            currency=self.currency,
        )


# For paginated lists
class TagRulesPublic(SQLModel):
    """Response model for paginated tag rules."""

    data: list[TagRulePublic]
    count: int


# Model for apply rules request
class ApplyRulesRequest(SQLModel):
    """Request model for applying rules."""

    transaction_id: uuid.UUID | None = None
    statement_id: uuid.UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    dry_run: bool = Field(default=False)


# Model for apply rules response
class ApplyRulesResponse(SQLModel):
    """Response model for applying rules."""

    evaluated_count: int
    applied_count: int
    details: list[dict[str, Any]] | None = Field(default=None)
