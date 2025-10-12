"""Usecase for retrieving accounts with filtering and pagination."""

from uuid import UUID

from app.domains.accounts.domain import options as opts
from app.domains.accounts.domain.models import AccountsPublic
from app.domains.accounts.service import AccountService
from app.domains.accounts.service import provide as provide_account_service


class GetAccountsUseCase:
    """Usecase for retrieving accounts with filtering and pagination."""

    def __init__(self, account_service: AccountService) -> None:
        """Initialize the usecase with an account service.

        Args:
            account_service: Service for handling account operations
        """
        self.account_service = account_service

    def execute(
        self,
        name: str | None = None,
        type: str | None = None,
        currency: str | None = None,
        is_active: bool | None = None,
        parent_id: str | None = None,
        skip: int = 0,
        limit: int = 50,
        sort_by: str = "name",
        sort_order: str = "asc",
    ) -> AccountsPublic:
        """Execute the usecase to retrieve accounts with filtering and pagination.

        Args:
            name: Filter by account name
            type: Filter by account type
            currency: Filter by currency
            is_active: Filter by active status
            parent_id: Filter by parent account ID
            skip: Number of records to skip
            limit: Number of records to return
            sort_by: Field to sort by
            sort_order: Sort order (asc/desc)

        Returns:
            AccountsPublic: Paginated accounts data
        """
        # Build search filters
        search_filters = opts.SearchFilters(
            name=name,
            type=type,
            currency=currency,
            is_active=is_active,
            parent_id=UUID(parent_id) if parent_id else None,
        )

        # Build search pagination
        search_pagination = opts.SearchPagination(
            skip=skip,
            limit=limit,
        )

        # Build search sorting
        search_sorting = opts.SearchSorting(
            field=sort_by,
            order=opts.SortOrder(sort_order),
        )

        # Build search options
        search_options = (
            opts.SearchOptions()
            .with_filters(search_filters)
            .with_pagination(search_pagination)
            .with_sorting(search_sorting)
        )

        return self.account_service.search_accounts(search_options)


def provide() -> GetAccountsUseCase:
    """Provide an instance of GetAccountsUseCase.

    Returns:
        GetAccountsUseCase: A new instance with the account service
    """
    return GetAccountsUseCase(provide_account_service())
