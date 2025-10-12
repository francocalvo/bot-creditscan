"""Expense transactions repository implementation."""

import builtins
import uuid
from collections.abc import Generator
from typing import Any

from sqlmodel import Session, func, select
from sqlmodel.sql.expression import SelectOfScalar

from app.domains.expenses_transactions.domain.errors import ExpenseNotFoundError
from app.domains.expenses_transactions.domain.models import (
    Expense,
    ExpenseCreate,
    ExpensePublic,
)
from app.domains.expenses_transactions.domain.options import SearchOptions
from app.domains.expenses_transactions.repository.builders.search import (
    build_options,
)


class ExpenseRepository:
    """Repository for expense transactions."""

    def __init__(self, db_session: Session):
        """Initialize the repository with a database session."""
        self.db_session = db_session

    def create(self, expense_data: ExpenseCreate) -> Expense:
        """Create a new expense transaction."""
        expense = Expense.model_validate(expense_data)
        self.db_session.add(expense)
        self.db_session.commit()
        self.db_session.refresh(expense)
        return expense

    def get_by_id(self, expense_id: uuid.UUID) -> Expense:
        """Get an expense transaction by ID."""
        expense = self.db_session.get(Expense, expense_id)
        if not expense:
            raise ExpenseNotFoundError(
                f"Expense transaction with ID {expense_id} not found"
            )
        return expense

    def list(
        self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None
    ) -> list[ExpensePublic]:
        """List expense transactions with pagination and filtering."""
        query = select(ExpensePublic)

        if filters:
            for field, value in filters.items():
                if hasattr(Expense, field):
                    query = query.where(getattr(Expense, field) == value)

        result = self.db_session.exec(query.offset(skip).limit(limit))
        return list(result)

    def count(self, options: SearchOptions | None = None) -> int:
        """Count expense transactions with optional filtering."""
        query: SelectOfScalar[Expense] = select(Expense)

        if options:
            query: SelectOfScalar[Expense] = build_options(query, options)

        count_q = (
            query.with_only_columns(func.count())
            .order_by(None)
            .select_from(query.get_final_froms()[0])
        )

        iterator: Generator[int, None, None] = self.db_session.exec(count_q)  # type: ignore
        for count in iterator:  # type: ignore
            return count  # type: ignore
        return 0

    def search(self, options: SearchOptions) -> tuple[builtins.list[Expense], int]:
        """Search expense transactions with advanced filtering using SQLModel.

        Args:
            options: Search options including date range, category, subcategory, tags, and pagination

        Returns:
            A tuple containing the list of matching expenses and the total count
        """
        query = build_options(select(Expense), options)
        count = self.count(options)

        result = self.db_session.exec(query)
        expenses = list(result)

        return expenses, count
