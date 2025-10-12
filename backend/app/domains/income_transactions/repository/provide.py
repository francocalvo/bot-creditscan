from app.domains.income_transactions.repository.income_repository import (
    IncomeRepository,
)
from app.pkgs.database.provider import get_db_session


def provide() -> IncomeRepository:
    """Provide an instance of IncomeRepository.

    Returns:
        IncomeRepository: The singleton instance of IncomeRepository with a database session.
    """
    # No need for lru_cache as the class itself is a singleton
    return IncomeRepository(get_db_session())
