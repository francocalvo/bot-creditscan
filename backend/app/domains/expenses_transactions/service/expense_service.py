"""Expense transactions service implementation."""

import uuid

from app.domains.expenses_transactions.domain.models import (
    Expense,
    ExpensePublic,
    ExpensesPublic,
)
from app.domains.expenses_transactions.domain.options import SearchOptions
from app.domains.expenses_transactions.repository import provide_expense_repository
from app.domains.expenses_transactions.repository.expense_repository import (
    ExpenseRepository,
)


class ExpenseService:
    """Service for expense transactions.

    Implemented as a singleton to ensure only one instance exists.
    """

    def __init__(self, expense_repository: ExpenseRepository):
        """Initialize the service with a repository.

        This will only run once for the singleton instance.
        """
        self.expense_repository = expense_repository

    def get_expense(self, expense_id: uuid.UUID) -> Expense:
        """Get an expense transaction by ID."""
        expense = self.expense_repository.get_by_id(expense_id)
        return Expense.model_validate(expense)

    def list_expenses(self, skip: int = 0, limit: int = 100) -> ExpensesPublic:
        """List expense transactions with pagination and filtering."""
        expenses = self.expense_repository.list(skip=skip, limit=limit)
        count = self.expense_repository.count()

        return ExpensesPublic(
            data=[ExpensePublic.model_validate(expense) for expense in expenses],
            count=count,
            pagination={"skip": skip, "limit": limit},
        )

    def search_expenses(self, options: SearchOptions) -> ExpensesPublic:
        """Search expense transactions with advanced filtering.

        Args:
            options: Search options including date range, category, subcategory, tags, and pagination

        Returns:
            ExpensesPublic: Paginated and filtered expenses data
        """
        # Use the repository's search method
        expenses, count = self.expense_repository.search(options)

        # Convert to domain models
        return ExpensesPublic(
            data=[ExpensePublic.model_validate(expense) for expense in expenses],
            count=count,
            pagination={
                "skip": options.pagination.skip,
                "limit": options.pagination.limit,
            },
        )


def provide() -> ExpenseService:
    """Provide an instance of ExpenseService.

    Returns:
        ExpenseService: The singleton instance of ExpenseService with a repository.
    """
    # No need for lru_cache as the class itself is a singleton
    return ExpenseService(provide_expense_repository())
