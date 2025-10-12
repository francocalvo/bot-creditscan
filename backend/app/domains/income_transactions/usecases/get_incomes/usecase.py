"""Usecase for retrieving incomes with filtering and pagination."""

from datetime import date, datetime

from app.domains.income_transactions.domain import options as opts
from app.domains.income_transactions.domain.models import Incomes
from app.domains.income_transactions.service import (
    IncomeService,
    provide_income_service,
)


class GetIncomesUseCase:
    """Usecase for retrieving incomes with filtering and pagination."""

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
        origin: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Incomes:
        """
        Execute the usecase to retrieve incomes with filtering and pagination.

        Args:
            from_date: Start date for filtering
            to_date: End date for filtering (defaults to current date if None)
            origin: Optional origin filter
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            Incomes: Paginated incomes data
        """
        # Determine effective end date
        effective_to_date: date = to_date or datetime.now().date()

        search_filters = opts.SearchFilters(
            from_date=from_date,
            to_date=effective_to_date,
            origin=origin,
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

        return self.income_service.search_incomes(search_options)


def provide() -> GetIncomesUseCase:
    """Provide an instance of GetIncomesUseCase.

    Returns:
        GetIncomesUseCase: A new instance with the income service
    """
    return GetIncomesUseCase(provide_income_service())
