"""Income transactions repository."""

from .income_repository import IncomeRepository
from .provide import provide as provide_income_repository

__all__ = ["IncomeRepository", "provide_income_repository"]
