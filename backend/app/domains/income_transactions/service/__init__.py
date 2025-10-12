"""Income transactions service."""

from .income_service import IncomeService
from .income_service import provide as provide_income_service

__all__ = ["IncomeService", "provide_income_service"]
