"""Usecase for retrieving expenses with filtering and pagination."""

from datetime import date, datetime

from app.domains.expenses_transactions.domain import options as opts
from app.domains.expenses_transactions.domain.models import ExpensesPublic
from app.domains.expenses_transactions.service import (
    ExpenseService,
    provide_expense_service,
)


class GetExpensesUseCase:
    """Usecase for retrieving expenses with filtering and pagination."""

    def __init__(self, expense_service: ExpenseService) -> None:
        """Initialize the usecase with an expense service.

        Args:
            expense_service: Service for handling expense transactions
        """
        self.expense_service = expense_service

    def execute(
        self,
        from_date: date,
        to_date: date | None = None,
        category: str | None = None,
        subcategory: str | None = None,
        tags: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> ExpensesPublic:
        """
        Execute the usecase to retrieve expenses with filtering and pagination.

        Args:
            from_date: Start date for filtering
            to_date: End date for filtering (defaults to current date if None)
            category: Optional category filter
            subcategory: Optional subcategory filter
            tags: Optional tags filter
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            ExpensesPublic: Paginated expenses data
        """
        # Determine effective end date
        effective_to_date: date = to_date or datetime.now().date()

        search_filters = opts.SearchFilters(
            from_date=from_date,
            to_date=effective_to_date,
            category=category,
            subcategory=subcategory,
            tags=tags,
        )

        search_pagination = opts.SearchPagination(
            skip=skip,
            limit=limit,
        )

        search_options = (
            opts.SearchOptions()
            .with_filters(search_filters)
            .with_pagination(search_pagination)
        )

        return self.expense_service.search_expenses(search_options)


def provide() -> GetExpensesUseCase:
    """Provide an instance of GetExpensesUseCase.

    Returns:
        GetExpensesUseCase: A new instance with the expense service
    """
    return GetExpensesUseCase(provide_expense_service())
