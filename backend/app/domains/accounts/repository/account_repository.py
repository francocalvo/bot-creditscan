"""Account repository implementation."""

import builtins
import uuid
from collections.abc import Generator
from functools import lru_cache
from typing import Any

from sqlmodel import Session, func, select
from sqlmodel.sql.expression import SelectOfScalar

from app.domains.accounts.domain.errors import AccountNotFoundError
from app.domains.accounts.domain.models import Account, AccountCreate
from app.domains.accounts.domain.options import SearchOptions
from app.domains.accounts.repository.builders.search import build_options
from app.pkgs.database import get_db_session


class AccountRepository:
    """Repository for accounts."""

    def __init__(self, db_session: Session):
        """Initialize the repository with a database session."""
        self.db_session = db_session

    def create(self, account_data: AccountCreate) -> Account:
        """Create a new account."""
        account = Account.model_validate(account_data)
        self.db_session.add(account)
        self.db_session.commit()
        self.db_session.refresh(account)
        return account

    def get_by_id(self, account_id: uuid.UUID) -> Account:
        """Get an account by ID."""
        account = self.db_session.get(Account, account_id)
        if not account:
            raise AccountNotFoundError(f"Account with ID {account_id} not found")
        return account

    def list(
        self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None
    ) -> list[Account]:
        """List accounts with pagination and filtering."""
        query = select(Account)

        if filters:
            for field, value in filters.items():
                if hasattr(Account, field):
                    query = query.where(getattr(Account, field) == value)

        result = self.db_session.exec(query.offset(skip).limit(limit))
        return list(result)

    def count(self, options: SearchOptions | None = None) -> int:
        """Count accounts with optional filtering."""
        query: SelectOfScalar[Account] = select(Account)

        if options:
            query: SelectOfScalar[Account] = build_options(query, options)

        count_q = (
            query.with_only_columns(func.count())
            .order_by(None)
            .select_from(query.get_final_froms()[0])
        )

        iterator: Generator[int, None, None] = self.db_session.exec(count_q)  # type: ignore
        for count in iterator:  # type: ignore
            return count  # type: ignore
        return 0

    def update(self, account_id: uuid.UUID, account_data: dict[str, Any]) -> Account:
        """Update an account."""
        account = self.get_by_id(account_id)

        for field, value in account_data.items():
            if hasattr(account, field):
                setattr(account, field, value)

        self.db_session.add(account)
        self.db_session.commit()
        self.db_session.refresh(account)
        return account

    def delete(self, account_id: uuid.UUID) -> None:
        """Delete an account."""
        account = self.get_by_id(account_id)
        self.db_session.delete(account)
        self.db_session.commit()

    def search(self, options: SearchOptions) -> tuple[builtins.list[Account], int]:
        """Search accounts with advanced filtering using SQLModel.

        Args:
            options: Search options including filters, pagination, and sorting

        Returns:
            A tuple containing the list of matching accounts and the total count
        """
        query = build_options(select(Account), options)
        count = self.count(options)

        result = self.db_session.exec(query)
        accounts = list(result)

        return accounts, count


@lru_cache
def provide() -> AccountRepository:
    """Provide an instance of AccountRepository.

    Returns:
        AccountRepository: An instance of AccountRepository with a database session.
    """
    return AccountRepository(get_db_session())
