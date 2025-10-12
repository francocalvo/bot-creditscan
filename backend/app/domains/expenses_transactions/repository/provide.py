"""Provide an instance of ExpenseRepository."""

from functools import lru_cache

from app.domains.expenses_transactions.repository.expense_repository import (
    ExpenseRepository,
)
from app.pkgs.database import get_db_session


@lru_cache
def provide_expense_repository() -> ExpenseRepository:
    """Provide an instance of ExpenseRepository.

    Returns:
        ExpenseRepository: The singleton instance of ExpenseRepository with a database session.
    """
    return ExpenseRepository(get_db_session())
