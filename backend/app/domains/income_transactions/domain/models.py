"""Income transactions domain models."""

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


# Income model
class IncomeBase(TransactionBase):
    """Base model for income transactions."""

    origin: str = Field(index=True)


class IncomeCreate(IncomeBase):
    """Model for creating income transactions."""

    pass


class Income(IncomeBase, table=True):
    """Database model for income transactions."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class Incomes(SQLModel):
    """Response model for paginated income transactions."""

    data: list[Income]
    count: int
    pagination: dict[str, int] | None = None


class IncomeSummary(TypedDict):
    """Type definition for a summary of amounts."""

    amount_ars: float
    amount_usd: float
    amount_cars: float
    group: str


class IncomeSummaryResponse(TypedDict):
    """Type definition for the summary response."""

    data: list[IncomeSummary]
    from_date: str
    to: str
