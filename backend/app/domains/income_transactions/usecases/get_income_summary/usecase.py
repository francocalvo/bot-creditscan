"""Get income summary usecase - Python aggregation implementation."""

from collections import defaultdict
from datetime import date, datetime
from enum import Enum

from app.domains.income_transactions.domain import options as opts
from app.domains.income_transactions.domain.models import (
    Incomes,
    IncomeSummary,
    IncomeSummaryResponse,
)
from app.domains.income_transactions.service import (
    IncomeService,
    provide_income_service,
)


class GroupBy(Enum):
    """Enumeration for grouping options."""

    ORIGIN = "origin"
    MONTH = "month"


class GetIncomeSummaryUseCase:
    """Usecase for retrieving income summaries grouped by origin or month."""

    def __init__(self, income_service: IncomeService) -> None:
        """Initialize the usecase with an income service.

        Args:
            income_service: Service for handling income transactions
        """
        self.income_service = income_service

    def execute(
        self,
        from_date: date,
        to_date: date | None = None,
        group_by: str | GroupBy = GroupBy.ORIGIN,
    ) -> IncomeSummaryResponse:
        """
        Execute the usecase to get income summaries grouped by origin or month.

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

        # Fetch incomes using the service
        incomes: Incomes = self.income_service.search_incomes(search_options)

        # Perform aggregation
        data: list[IncomeSummary] = self._aggregate_incomes(
            incomes, normalized_group_by
        )

        # Return the formatted response
        return {
            "data": data,
            "from_date": from_date.isoformat(),
            "to": effective_to_date.isoformat(),
        }

    def _aggregate_incomes(
        self,
        incomes: Incomes,
        group_by: GroupBy = GroupBy.ORIGIN,
    ) -> list[IncomeSummary]:
        """Aggregate income data in Python.

        Args:
            incomes: List of income transactions to aggregate
            group_by: Field to group results by (origin or month)

        Returns:
            List of AmountsSummary objects with aggregated amounts
        """
        # Initialize aggregation dictionary with default values
        aggregated: dict[str, dict[str, float]] = defaultdict(
            lambda: {"amount_ars": 0.0, "amount_usd": 0.0, "amount_cars": 0.0}
        )

        # Process each income record
        for income in incomes.data:
            # Determine the group key based on group_by
            group_key: str
            if group_by == GroupBy.ORIGIN:
                group_key = income.origin
            else:  # GroupBy.MONTH
                # Format date as YYYY-MM-01 for month grouping
                group_key = f"{income.date.year}-{income.date.month:02d}-01"

            # Aggregate amounts
            aggregated[group_key]["amount_ars"] += income.amount_ars
            aggregated[group_key]["amount_usd"] += income.amount_usd
            aggregated[group_key]["amount_cars"] += income.amount_cars

        # Convert to list of AmountsSummary
        result: list[IncomeSummary] = [
            IncomeSummary(group=key, **amounts) for key, amounts in aggregated.items()
        ]

        return result


def provide() -> GetIncomeSummaryUseCase:
    """Provide an instance of GetIncomeSummaryUseCase.

    Returns:
        GetIncomeSummaryUseCase: A new instance with the income service
    """
    return GetIncomeSummaryUseCase(provide_income_service())
