"""Account service implementation."""

import uuid
from functools import lru_cache
from typing import Any

from app.domains.accounts.domain.models import (
    AccountCreate,
    AccountPublic,
    AccountsPublic,
)
from app.domains.accounts.domain.options import SearchOptions
from app.domains.accounts.repository import provide_account_repository
from app.domains.accounts.repository.account_repository import (
    AccountRepository,
)


class AccountService:
    """Service for accounts."""

    def __init__(self, account_repository: AccountRepository):
        """Initialize the service with a repository."""
        self.account_repository = account_repository

    def create_account(self, account_data: AccountCreate) -> AccountPublic:
        """Create a new account."""
        account = self.account_repository.create(account_data)
        return AccountPublic.model_validate(account)

    def get_account(self, account_id: uuid.UUID) -> AccountPublic:
        """Get an account by ID."""
        account = self.account_repository.get_by_id(account_id)
        return AccountPublic.model_validate(account)

    def list_accounts(
        self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None
    ) -> AccountsPublic:
        """List accounts with pagination and filtering."""
        accounts = self.account_repository.list(skip=skip, limit=limit, filters=filters)
        count: int = self.account_repository.count(filters=filters)  # type: ignore[]

        return AccountsPublic(
            data=[AccountPublic.model_validate(account) for account in accounts],
            count=count,  # type: ignore[]
            pagination={"skip": skip, "limit": limit},
        )

    def update_account(
        self, account_id: uuid.UUID, account_data: dict[str, Any]
    ) -> AccountPublic:
        """Update an account."""
        account = self.account_repository.update(account_id, account_data)
        return AccountPublic.model_validate(account)

    def delete_account(self, account_id: uuid.UUID) -> None:
        """Delete an account."""
        self.account_repository.delete(account_id)

    def search_accounts(self, options: SearchOptions) -> AccountsPublic:
        """Search accounts with advanced filtering.

        Args:
            options: Search options including filters, pagination, and sorting

        Returns:
            AccountsPublic: Paginated and filtered accounts data
        """
        # Use the repository's search method
        accounts, count = self.account_repository.search(options)

        # Convert to domain models
        return AccountsPublic(
            data=[AccountPublic.model_validate(account) for account in accounts],
            count=count,
            pagination={
                "skip": options.pagination.skip,
                "limit": options.pagination.limit,
            },
        )


@lru_cache
def provide() -> AccountService:
    """Provide an instance of AccountService.

    Returns:
        AccountService: An instance of AccountService with a repository.
    """
    return AccountService(provide_account_repository())
