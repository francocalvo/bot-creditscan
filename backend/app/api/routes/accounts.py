"""Account-related routes."""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Query

from app.domains.accounts.domain.models import (
    AccountBalancePublic,
    AccountPublic,
    AccountsPublic,
    AccountTransactionsPublic,
)
from app.domains.accounts.usecases import (
    provide_account_balance_usecase,
    provide_account_transactions_usecase,
    provide_children_accounts_usecase,
    provide_get_accounts_usecase,
    provide_parent_account_usecase,
)

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=AccountsPublic)
def get_accounts(
    name: str | None = Query(None, description="Filter by account name"),
    type: str | None = Query(None, description="Filter by account type"),
    currency: str | None = Query(None, description="Filter by currency"),
    is_active: bool | None = Query(None, description="Filter by active status"),
    parent_id: str | None = Query(None, description="Filter by parent account ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    sort_by: str = Query("name", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc/desc)"),
) -> AccountsPublic:
    """Get all accounts with filtering options."""
    usecase = provide_get_accounts_usecase()
    return usecase.execute(
        name=name,
        type=type,
        currency=currency,
        is_active=is_active,
        parent_id=parent_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/{account_id}/parent", response_model=AccountPublic | None)
def get_parent_account(
    account_id: UUID,
) -> AccountPublic | None:
    """Get parent account of a given account."""
    usecase = provide_parent_account_usecase()
    return usecase.execute(account_id=account_id)


@router.get("/{account_id}/children", response_model=AccountsPublic)
def get_children_accounts(
    account_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
) -> AccountsPublic:
    """Get all children accounts of a given account."""
    usecase = provide_children_accounts_usecase()
    return usecase.execute(parent_account_id=account_id, skip=skip, limit=limit)


@router.get("/{account_name}/transactions", response_model=AccountTransactionsPublic)
def get_account_transactions(
    account_name: str,
    from_date: date | None = Query(None, description="Start date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
) -> AccountTransactionsPublic:
    """Get all transactions for an account and its children.

    This endpoint supports hierarchical account filtering:
    - When providing an account name (e.g., "Assets:Cash"), the system will:
      - Match the exact account ("Assets:Cash")
      - Match all children ("Assets:Cash:Checking", "Assets:Cash:Savings", etc.)
    """
    usecase = provide_account_transactions_usecase()
    return usecase.execute(
        account_name=account_name,
        from_date=from_date,
        to_date=to_date,
        skip=skip,
        limit=limit,
    )


@router.get("/{account_name}/balance", response_model=AccountBalancePublic)
def get_account_balance(
    account_name: str,
    as_of_date: date | None = Query(
        None, description="Calculate balance as of this date (YYYY-MM-DD)"
    ),
) -> AccountBalancePublic:
    """Get balance for an account and its children.

    This endpoint supports hierarchical account filtering:
    - When providing an account name (e.g., "Assets:Cash"), the system will:
      - Match the exact account ("Assets:Cash")
      - Match all children ("Assets:Cash:Checking", "Assets:Cash:Savings", etc.)
    - Balance calculation includes all transactions from the beginning of time up to the as_of_date
    """
    usecase = provide_account_balance_usecase()
    return usecase.execute(
        account_name=account_name,
        as_of_date=as_of_date,
    )
