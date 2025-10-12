"""Tests for the GetAccountBalanceUseCase."""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.domains.accounts.domain.models import Account
from app.domains.accounts.usecases.get_account_balance import GetAccountBalanceUseCase


@pytest.fixture
def mock_account_repository():
    """Create a mock account repository."""
    repository = MagicMock()
    
    # Mock account
    account = Account(
        id=uuid.uuid4(),
        name="Test Account",
        type="checking",
        currency="ARS",
        description="Test account",
        is_active=True
    )
    
    repository.get_by_id.return_value = account
    return repository


@pytest.fixture
def mock_income_repository():
    """Create a mock income repository."""
    repository = MagicMock()
    
    # Mock income transactions
    income1 = MagicMock(amount_ars=100.0, amount_usd=1.0, amount_cars=100.0)
    income2 = MagicMock(amount_ars=200.0, amount_usd=2.0, amount_cars=200.0)
    
    repository.list.return_value = [income1, income2]
    return repository


@pytest.fixture
def mock_expense_repository():
    """Create a mock expense repository."""
    repository = MagicMock()
    
    # Mock expense transactions
    expense1 = MagicMock(amount_ars=50.0, amount_usd=0.5, amount_cars=50.0)
    expense2 = MagicMock(amount_ars=75.0, amount_usd=0.75, amount_cars=75.0)
    
    repository.list.return_value = [expense1, expense2]
    return repository


def test_get_account_balance(mock_account_repository, mock_income_repository, mock_expense_repository):
    """Test getting an account's balance."""
    # Arrange
    account_id = uuid.uuid4()
    use_case = GetAccountBalanceUseCase(
        mock_account_repository,
        mock_income_repository,
        mock_expense_repository
    )
    
    # Act
    result = use_case.execute(account_id)
    
    # Assert
    mock_account_repository.get_by_id.assert_called_once_with(account_id)
    mock_income_repository.list.assert_called_once_with(filters={"account": str(account_id)})
    mock_expense_repository.list.assert_called_once_with(filters={"account": str(account_id)})
    
    assert result["account_id"] == account_id
    assert result["account_name"] == mock_account_repository.get_by_id.return_value.name
    assert result["balance_ars"] == 175.0  # 300 - 125
    assert result["balance_usd"] == 1.75  # 3 - 1.25
    assert result["balance_cars"] == 175.0  # 300 - 125
