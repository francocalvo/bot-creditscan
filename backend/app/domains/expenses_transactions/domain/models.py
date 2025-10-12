"""Expense transactions domain models."""

import uuid
from datetime import date as date_type
from typing import TypedDict

from sqlmodel import Field, SQLModel


# Base Transaction model
class TransactionBase(SQLModel):
    """Base model for all financial transactions."""

    date: date_type = Field(index=True)
    account: str = Field(index=True)
    payee: str | None = None
    narration: str
    amount_ars: float
    amount_usd: float
    amount_cars: float


# Expense model
class ExpenseBase(TransactionBase):
    """Base model for expense transactions."""

    category: str = Field(index=True)
    subcategory: str = Field(index=True)
    tags: str | None = Field(default=None, index=True)


class ExpenseCreate(ExpenseBase):
    """Model for creating expense transactions."""

    pass


class Expense(ExpenseBase, table=True):
    """Database model for expense transactions."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class ExpensePublic(ExpenseBase):
    """Public model for expense transactions."""

    id: uuid.UUID


class ExpensesPublic(SQLModel):
    """Response model for paginated expense transactions."""

    data: list[ExpensePublic]
    count: int
    pagination: dict[str, int] | None = None


class ExpenseSummary(TypedDict):
    """Type definition for a summary of amounts."""

    amount_ars: float
    amount_usd: float
    amount_cars: float
    group: str


class ExpenseSummaryPublic(TypedDict):
    """Type definition for the summary response."""

    data: list[ExpenseSummary]
    from_date: str
    to_date: str
