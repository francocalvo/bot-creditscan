"""Account domain errors."""


class AccountError(Exception):
    """Base exception for account errors."""

    pass


class AccountNotFoundError(AccountError):
    """Raised when an account is not found."""

    pass


class InvalidAccountDataError(AccountError):
    """Raised when account data is invalid."""

    pass
