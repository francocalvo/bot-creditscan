"""Get incomes usecase."""

from app.domains.income_transactions.usecases.get_incomes.usecase import (
    GetIncomesUseCase,
)
from app.domains.income_transactions.usecases.get_incomes.usecase import (
    provide as provide_get_incomes_usecase,
)

__all__ = ["GetIncomesUseCase", "provide_get_incomes_usecase"]
