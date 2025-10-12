"""Income-related routes."""

from datetime import date

from fastapi import APIRouter, Query

from app.domains.income_transactions.domain.models import Incomes, IncomeSummaryResponse
from app.domains.income_transactions.usecases import (
    provide_get_income_summary_use_case,
    provide_get_incomes_usecase,
)

router = APIRouter(prefix="/income", tags=["income"])


@router.get("/", response_model=Incomes)
def get_incomes(
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    origin: str | None = Query(None, description="Filter by origin"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
) -> Incomes:
    """Retrieve income entries with filtering and pagination."""
    # Delegate to the usecase
    usecase = provide_get_incomes_usecase()
    return usecase.execute(
        from_date=from_date,
        to_date=to_date,
        origin=origin,
        skip=skip,
        limit=limit,
    )


@router.get("/summary", response_model=IncomeSummaryResponse)
def get_income_summary(
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    group_by: str = Query("origin", description="Group by 'origin' or 'month'"),
) -> IncomeSummaryResponse:
    """Get income summaries grouped by origin or month."""
    # Delegate to the usecase
    usecase = provide_get_income_summary_use_case()
    return usecase.execute(
        from_date=from_date,
        to_date=to_date,
        group_by=group_by,
    )
