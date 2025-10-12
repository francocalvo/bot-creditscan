"""Aggregation routes for financial analytics."""

from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Query
from sqlmodel import func, select

from app.api.deps import SessionDep
from app.domains.expenses_transactions.domain.models import Expense
from app.domains.income_transactions.domain.models import Income

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/combined")
def get_combined_metrics(
    session: SessionDep,
    from_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    to_date: date | None = Query(None, description="End date (YYYY-MM-DD)"),
    currencies: list[str] = Query(
        ["USD"], description="Currencies to include in response"
    ),
) -> dict[str, Any]:
    """Get combined income and expense metrics for a period.
    """
    to_date = to_date or datetime.now().date()

    # Get totals for all currencies
    income_query = select(
        func.sum(Income.amount_ars).label("income_ars"),
        func.sum(Income.amount_usd).label("income_usd"),
        func.sum(Income.amount_cars).label("income_cars"),
    ).where(Income.date >= from_date.isoformat(), Income.date < to_date.isoformat())
    income_totals = session.exec(income_query).one()

    expense_query = select(
        func.sum(Expense.amount_ars).label("expenses_ars"),
        func.sum(Expense.amount_usd).label("expenses_usd"),
        func.sum(Expense.amount_cars).label("expenses_cars"),
    ).where(Expense.date >= from_date.isoformat(), Expense.date < to_date.isoformat())
    expense_totals = session.exec(expense_query).one()

    # Calculate metrics for each currency
    metrics = {}
    for curr in currencies:
        curr_lower = curr.lower()
        income = float(getattr(income_totals, f"income_{curr_lower}") or 0)
        expenses = float(getattr(expense_totals, f"expenses_{curr_lower}") or 0)
        balance = income - expenses

        metrics[f"income_{curr_lower}"] = income
        metrics[f"expenses_{curr_lower}"] = expenses
        metrics[f"balance_{curr_lower}"] = balance

    # Add expense/income ratio
    base_curr = currencies[0].lower()
    base_income = metrics[f"income_{base_curr}"]
    metrics["ratio"] = (
        metrics[f"expenses_{base_curr}"] / base_income if base_income else 0
    )

    return {
        "metrics": metrics,
        "period": {"from": from_date.isoformat(), "to": to_date.isoformat()},
    }
