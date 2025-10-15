"""Account domain models."""

import uuid
from datetime import date

from sqlmodel import Field, SQLModel


class AccountBase(SQLModel):
    """Base model for financial accounts."""

    name: str = Field(index=True)
    open_from: date = Field(default_factory=date.today, index=True)
    open_to: date | None = None
    type: str = Field(index=True)
    is_active: bool = True


class AccountCreate(AccountBase):
    """Model for creating account."""

    pass


class Account(AccountBase, table=True):
    """Database model for accounts."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class AccountPublic(AccountBase):
    """Public model for accounts."""

    id: uuid.UUID


class AccountsPublic(SQLModel):
    """Response model for paginated accounts."""

    data: list[AccountPublic]
    count: int
    pagination: dict[str, int] | None = None
