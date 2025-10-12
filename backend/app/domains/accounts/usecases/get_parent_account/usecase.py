"""Usecase for retrieving parent account."""

import uuid

from app.domains.accounts.domain.models import AccountPublic
from app.domains.accounts.service import AccountService, provide as provide_account_service


class GetParentAccountUseCase:
    """Usecase for retrieving parent account."""

    def __init__(self, account_service: AccountService) -> None:
        """Initialize the usecase with an account service.

        Args:
            account_service: Service for handling account operations
        """
        self.account_service = account_service

    def execute(self, account_id: uuid.UUID) -> AccountPublic | None:
        """Execute the usecase to retrieve parent account.

        Args:
            account_id: ID of the child account

        Returns:
            AccountPublic: Parent account if exists, None otherwise
        """
        account = self.account_service.get_account(account_id)
        
        if account.parent_id is None:
            return None
            
        return self.account_service.get_account(account.parent_id)


def provide() -> GetParentAccountUseCase:
    """Provide an instance of GetParentAccountUseCase.

    Returns:
        GetParentAccountUseCase: A new instance with the account service
    """
    return GetParentAccountUseCase(provide_account_service())
