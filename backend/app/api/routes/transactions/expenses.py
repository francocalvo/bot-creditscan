"""Expense-related routes."""

from datetime import date

from fastapi import APIRouter, Query

from app.domains.expenses_transactions.domain.models import (
    ExpensesPublic,
    ExpenseSummaryPublic,
)
from app.domains.expenses_transactions.usecases import (
    provide_expense_summary_usecase,
    provide_get_expenses_usecase,
)

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/", response_model=ExpensesPublic)
def get_expenses(
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    category: str | None = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
) -> ExpensesPublic:
    """Retrieve expenses with filtering and pagination."""
    # Delegate to the usecase
    usecase = provide_get_expenses_usecase()
    return usecase.execute(
        from_date=from_date,
        to_date=to_date,
        category=category,
        skip=skip,
        limit=limit,
    )


@router.get("/summary")
def get_expense_summary(
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    group_by: str = Query(
        "category", description="Group by 'category', 'subcategory', or 'month'"
    ),
) -> ExpenseSummaryPublic:
    """Get expense summaries grouped by category or month."""
    # Delegate to the usecase
    usecase = provide_expense_summary_usecase()
    return usecase.execute(
        from_date=from_date,
        to_date=to_date,
        group_by=group_by,
    )
