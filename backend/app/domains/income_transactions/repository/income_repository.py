"""Income transactions repository implementation."""

import builtins
import uuid
from collections.abc import Generator
from typing import Any

from sqlmodel import Session, func, select
from sqlmodel.sql.expression import SelectOfScalar

from app.domains.income_transactions.domain.errors import IncomeNotFoundError
from app.domains.income_transactions.domain.models import (
    Income,
    IncomeCreate,
)
from app.domains.income_transactions.domain.options import SearchOptions
from app.domains.income_transactions.repository.builders.search import (
    build_options,
)


class IncomeRepository:
    """Repository for income transactions.

    Implemented as a singleton to ensure only one instance exists.
    """

    def __init__(self, db_session: Session) -> None:
        """Initialize the repository with a database session.

        This will only run once for the singleton instance.
        """
        self.db_session = db_session

    def create(self, income_data: IncomeCreate) -> Income:
        """Create a new income transaction."""
        income = Income.model_validate(income_data)
        self.db_session.add(income)
        self.db_session.commit()
        self.db_session.refresh(income)
        return income

    def get_by_id(self, income_id: uuid.UUID) -> Income:
        """Get an income transaction by ID."""
        income = self.db_session.get(Income, income_id)
        if not income:
            raise IncomeNotFoundError(
                f"Income transaction with ID {income_id} not found"
            )
        return income

    def list(
        self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None
    ) -> list[Income]:
        """List income transactions with pagination and filtering."""
        query = select(Income)

        if filters:
            for field, value in filters.items():
                if hasattr(Income, field):
                    query = query.where(getattr(Income, field) == value)

        result = self.db_session.exec(query.offset(skip).limit(limit))
        return list(result)

    def count(self, options: SearchOptions | None = None) -> int:
        """Count income transactions with optional filtering."""
        query: SelectOfScalar[Income] = select(Income)

        if options:
            query: SelectOfScalar[Income] = build_options(query, options)

        count_q = (
            query.with_only_columns(func.count())
            .order_by(None)
            .select_from(query.get_final_froms()[0])
        )

        iterator: Generator[int, None, None] = self.db_session.exec(count_q)  # type: ignore
        for count in iterator:  # type: ignore
            return count  # type: ignore
        return 0

    def update(self, income_id: uuid.UUID, income_data: dict[str, Any]) -> Income:
        """Update an income transaction."""
        income = self.get_by_id(income_id)

        for field, value in income_data.items():
            if hasattr(income, field):
                setattr(income, field, value)

        self.db_session.add(income)
        self.db_session.commit()
        self.db_session.refresh(income)
        return income

    def delete(self, income_id: uuid.UUID) -> None:
        """Delete an income transaction."""
        income = self.get_by_id(income_id)
        self.db_session.delete(income)
        self.db_session.commit()

    def search(self, options: SearchOptions) -> tuple[builtins.list[Income], int]:
        """Search income transactions with advanced filtering using SQLModel.

        Args:
            options: Search options including date range, origin, and pagination

        Returns:
            A tuple containing the list of matching incomes and the total count
        """
        query = build_options(select(Income), options)
        count = self.count(options)

        result = self.db_session.exec(query)
        incomes = list(result)

        return incomes, count
