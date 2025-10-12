"""Get expenses summary usecase - Python aggregation implementation."""

from collections import defaultdict
from datetime import date, datetime
from enum import Enum

from app.domains.expenses_transactions.domain import options as opts
from app.domains.expenses_transactions.domain.models import (
    ExpensePublic,
    ExpensesPublic,
    ExpenseSummary,
    ExpenseSummaryPublic,
)
from app.domains.expenses_transactions.service import (
    ExpenseService,
    provide_expense_service,
)


class GroupBy(Enum):
    """Enumeration for grouping options."""

    CATEGORY = "category"
    SUBCATEGORY = "subcategory"
    MONTH = "month"


class GetExpenseSummaryUseCase:
    """Usecase for retrieving expenses summaries grouped by origin or month."""

    def __init__(self, expenses_service: ExpenseService) -> None:
        """Initialize the usecase with an expenses service.

        Args:
            expenses_service: Service for handling expenses transactions
        """
        self.expenses_service = expenses_service

    def execute(
        self,
        from_date: date,
        to_date: date | None = None,
        group_by: str | GroupBy = GroupBy.CATEGORY,
    ) -> ExpenseSummaryPublic:
        """
        Execute the usecase to get expenses summaries grouped by origin or month.

        Args:
            from_date: Start date for filtering
            to_date: End date for filtering (defaults to current date if None)
            group_by: Field to group results by ('origin' or 'month')

        Returns:
            SummaryResponse: Dictionary containing summary data and period information

        Raises:
            ValueError: If the group_by value is invalid
        """
        # Normalize group_by parameter
        normalized_group_by: GroupBy
        if isinstance(group_by, str):
            group_by_str = group_by.upper()
            if group_by_str not in GroupBy.__members__:
                raise ValueError(f"Invalid group_by value: {group_by}")
            normalized_group_by = GroupBy[group_by_str]
        else:
            normalized_group_by = group_by

        # Determine effective end date
        effective_to_date: date = to_date or datetime.now().date()

        search_filters = opts.SearchFilters(
            from_date=from_date,
            to_date=effective_to_date,
        )

        search_pagination = opts.SearchPagination(
            skip=0,
            limit=10000,
        )

        search_options = (
            opts.SearchOptions()
            .with_filters(search_filters)
            .with_pagination(search_pagination)
        )

        # Fetch expensess using the service
        expensess: ExpensesPublic = self.expenses_service.search_expenses(
            search_options
        )

        # Perform aggregation
        data: list[ExpenseSummary] = self._aggregate_expenses(
            expensess, normalized_group_by
        )

        # Return the formatted response
        return {
            "data": data,
            "from_date": from_date.isoformat(),
            "to_date": effective_to_date.isoformat(),
        }

    def _aggregate_expenses(
        self,
        expenses: ExpensesPublic,
        group_by: GroupBy = GroupBy.CATEGORY,
    ) -> list[ExpenseSummary]:
        """Aggregate expenses data in Python.

        Args:
            expensess: List of expenses transactions to aggregate
            group_by: Field to group results by (origin or month)

        Returns:
            List of AmountsSummary objects with aggregated amounts
        """
        # Initialize aggregation dictionary with default values
        aggregated: dict[str, dict[str, float]] = defaultdict(
            lambda: {"amount_ars": 0.0, "amount_usd": 0.0, "amount_cars": 0.0}
        )

        # Process each expenses record
        expense: ExpensePublic
        for expense in expenses.data:
            # Determine the group key based on group_by
            group_key: str
            if group_by == GroupBy.CATEGORY:
                group_key = expense.category
            elif group_by == GroupBy.SUBCATEGORY:
                group_key = f"{expense.category}.{expense.subcategory}"
            else:  # GroupBy.MONTH
                # Format date as YYYY-MM-01 for month grouping
                group_key = f"{expense.date.year}-{expense.date.month:02d}-01"

            # Aggregate amounts
            aggregated[group_key]["amount_ars"] += expense.amount_ars
            aggregated[group_key]["amount_usd"] += expense.amount_usd
            aggregated[group_key]["amount_cars"] += expense.amount_cars

        # Convert to list of AmountsSummary
        result: list[ExpenseSummary] = [
            ExpenseSummary(group=key, **amounts) for key, amounts in aggregated.items()
        ]

        return result


def provide() -> GetExpenseSummaryUseCase:
    """Provide an instance of GetExpenseSummaryUseCase.

    Returns:
        GetExpenseSummaryUseCase: A new instance with the expenses service
    """
    return GetExpenseSummaryUseCase(provide_expense_service())
