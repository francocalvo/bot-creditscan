"""Get income summary usecase."""

from app.domains.income_transactions.usecases.get_income_summary.usecase import (
    GetIncomeSummaryUseCase,
)
from app.domains.income_transactions.usecases.get_income_summary.usecase import (
    provide as provide_get_income_summary_use_case,
)

__all__ = ["GetIncomeSummaryUseCase", "provide_get_income_summary_use_case"]
