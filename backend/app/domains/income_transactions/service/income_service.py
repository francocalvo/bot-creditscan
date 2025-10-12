"""Income transactions service implementation."""

import uuid

from app.domains.income_transactions.domain.models import (
    Income,
    Incomes,
)
from app.domains.income_transactions.domain.options import SearchOptions
from app.domains.income_transactions.repository import provide_income_repository
from app.domains.income_transactions.repository.income_repository import (
    IncomeRepository,
)


class IncomeService:
    """Service for income transactions.

    Implemented as a singleton to ensure only one instance exists.
    """

    def __init__(self, income_repository: IncomeRepository):
        """Initialize the service with a repository.

        This will only run once for the singleton instance.
        """
        self.income_repository = income_repository

    def get_income(self, income_id: uuid.UUID) -> Income:
        """Get an income transaction by ID."""
        income = self.income_repository.get_by_id(income_id)
        return Income.model_validate(income)

    def list_incomes(self, skip: int = 0, limit: int = 100) -> Incomes:
        """List income transactions with pagination and filtering."""
        incomes = self.income_repository.list(skip=skip, limit=limit)
        count = self.income_repository.count()

        return Incomes(
            data=[Income.model_validate(income) for income in incomes],
            count=count,
            pagination={"skip": skip, "limit": limit},
        )

    def search_incomes(self, options: SearchOptions) -> Incomes:
        """Search income transactions with advanced filtering.

        Args:
            options: Search options including date range, origin, and pagination

        Returns:
            Incomes: Paginated and filtered incomes data
        """
        # Use the repository's search method
        incomes, count = self.income_repository.search(options)

        # Convert to domain models
        return Incomes(
            data=[Income.model_validate(income) for income in incomes],
            count=count,
            pagination={
                "skip": options.pagination.skip,
                "limit": options.pagination.limit,
            },
        )


def provide() -> IncomeService:
    """Provide an instance of IncomeService.

    Returns:
        IncomeService: The singleton instance of IncomeService with a repository.
    """
    # No need for lru_cache as the class itself is a singleton
    return IncomeService(provide_income_repository())
