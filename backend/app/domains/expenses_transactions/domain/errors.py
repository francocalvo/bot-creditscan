"""Expense transactions domain errors."""


class ExpenseTransactionError(Exception):
    """Base exception for expense transaction errors."""

    pass


class ExpenseNotFoundError(ExpenseTransactionError):
    """Raised when an expense transaction is not found."""

    pass


class InvalidExpenseDataError(ExpenseTransactionError):
    """Raised when expense transaction data is invalid."""

    pass
