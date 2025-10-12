"""Expense transactions repository module."""

from app.domains.expenses_transactions.repository.provide import (
    provide_expense_repository,
)

__all__ = ["provide_expense_repository", "ExpenseRepository"]

from .expense_repository import ExpenseRepository
