"""Usecase for retrieving children accounts."""

import uuid

from app.domains.accounts.domain import options as opts
from app.domains.accounts.domain.models import AccountsPublic
from app.domains.accounts.service import AccountService
from app.domains.accounts.service import provide as provide_account_service


class GetChildrenAccountsUseCase:
    """Usecase for retrieving children accounts."""

    def __init__(self, account_service: AccountService) -> None:
        """Initialize the usecase with an account service.

        Args:
            account_service: Service for handling account operations
        """
        self.account_service = account_service

    def execute(
        self,
        parent_account_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> AccountsPublic:
        """Execute the usecase to retrieve children accounts.

        Args:
            parent_account_id: ID of the parent account
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            AccountsPublic: Paginated children accounts data
        """
        search_filters = opts.SearchFilters(
            parent_id=parent_account_id,
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

        return self.account_service.search_accounts(search_options)


def provide() -> GetChildrenAccountsUseCase:
    """Provide an instance of GetChildrenAccountsUseCase.

    Returns:
        GetChildrenAccountsUseCase: A new instance with the account service
    """
    return GetChildrenAccountsUseCase(provide_account_service())
