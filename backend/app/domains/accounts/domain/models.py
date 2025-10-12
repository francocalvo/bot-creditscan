"""Account domain models."""

import uuid
from datetime import date

from sqlmodel import Field, SQLModel

from app.domains.expenses_transactions.domain.models import ExpensePublic
from app.domains.income_transactions.domain.models import Income


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


class AccountTransactionSummary(SQLModel):
    """Summary of account transactions."""

    amount_ars: float
    amount_usd: float
    amount_cars: float
    count: int


class AccountTransactionsPublic(SQLModel):
    """Response model for account transactions."""

    account_name: str
    from_date: str
    to_date: str
    expenses: list[ExpensePublic]
    incomes: list[Income]
    expenses_summary: AccountTransactionSummary
    incomes_summary: AccountTransactionSummary
    total_transactions: int
    pagination: dict[str, int] | None = None


class AccountBalanceSummary(SQLModel):
    """Summary of account balance by currency."""

    amount_ars: float
    amount_usd: float
    amount_cars: float


class AccountBalanceDetails(SQLModel):
    """Detailed breakdown of account balance."""

    income: AccountTransactionSummary
    expenses: AccountTransactionSummary


class AccountBalancePublic(SQLModel):
    """Response model for account balance."""

    account_name: str
    as_of_date: str
    balance: AccountBalanceSummary
    totals: AccountBalanceDetails
    transaction_count: int
    pagination: dict[str, int] | None = None
