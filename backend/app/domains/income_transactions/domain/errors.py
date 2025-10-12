"""Income transactions domain errors."""


class IncomeTransactionError(Exception):
    """Base exception for income transaction errors."""

    pass


class IncomeNotFoundError(IncomeTransactionError):
    """Raised when an income transaction is not found."""

    pass


class InvalidIncomeDataError(IncomeTransactionError):
    """Raised when income transaction data is invalid."""

    pass
