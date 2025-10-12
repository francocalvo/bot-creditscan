"""Unit tests for the account service."""

import uuid
from unittest.mock import Mock

import pytest

from app.domains.accounts.domain.models import Account, AccountCreate, AccountPublic, AccountsPublic
from app.domains.accounts.domain.errors import AccountNotFoundError
from app.domains.accounts.service.account_service import AccountService


@pytest.fixture
def mock_account_repository():
    """Fixture for mocked account repository."""
    mock_repo = Mock()
    return mock_repo


@pytest.fixture
def account_service(mock_account_repository):
    """Fixture for account service with mocked repository."""
    return AccountService(mock_account_repository)


@pytest.fixture
def sample_account():
    """Fixture for sample account."""
    return Account(
        id=uuid.uuid4(),
        name="Savings Account",
        type="savings",
        currency="ARS",
        description="Personal savings account",
        is_active=True
    )


@pytest.fixture
def sample_account_create():
    """Fixture for sample account create data."""
    return AccountCreate(
        name="Savings Account",
        type="savings",
        currency="ARS",
        description="Personal savings account",
        is_active=True
    )


def test_create_account(account_service, mock_account_repository, sample_account, sample_account_create):
    """Test creating an account."""
    # Arrange
    mock_account_repository.create.return_value = sample_account
    
    # Act
    result = account_service.create_account(sample_account_create)
    
    # Assert
    mock_account_repository.create.assert_called_once_with(sample_account_create)
    assert isinstance(result, AccountPublic)
    assert result.id == sample_account.id
    assert result.name == sample_account.name
    assert result.type == sample_account.type
    assert result.currency == sample_account.currency


def test_get_account(account_service, mock_account_repository, sample_account):
    """Test getting an account."""
    # Arrange
    account_id = sample_account.id
    mock_account_repository.get_by_id.return_value = sample_account
    
    # Act
    result = account_service.get_account(account_id)
    
    # Assert
    mock_account_repository.get_by_id.assert_called_once_with(account_id)
    assert isinstance(result, AccountPublic)
    assert result.id == sample_account.id


def test_get_account_not_found(account_service, mock_account_repository):
    """Test getting a non-existent account."""
    # Arrange
    account_id = uuid.uuid4()
    mock_account_repository.get_by_id.side_effect = AccountNotFoundError(f"Account with ID {account_id} not found")
    
    # Act & Assert
    with pytest.raises(AccountNotFoundError):
        account_service.get_account(account_id)


def test_list_accounts(account_service, mock_account_repository, sample_account):
    """Test listing accounts."""
    # Arrange
    skip = 0
    limit = 10
    mock_account_repository.list.return_value = [sample_account]
    mock_account_repository.count.return_value = 1
    
    # Act
    result = account_service.list_accounts(skip=skip, limit=limit)
    
    # Assert
    mock_account_repository.list.assert_called_once_with(skip=skip, limit=limit, filters=None)
    mock_account_repository.count.assert_called_once_with(filters=None)
    assert isinstance(result, AccountsPublic)
    assert len(result.data) == 1
    assert result.count == 1
    assert result.pagination["skip"] == skip
    assert result.pagination["limit"] == limit


def test_list_accounts_with_filters(account_service, mock_account_repository, sample_account):
    """Test listing accounts with filters."""
    # Arrange
    skip = 0
    limit = 10
    filters = {"type": "savings"}
    mock_account_repository.list.return_value = [sample_account]
    mock_account_repository.count.return_value = 1
    
    # Act
    result = account_service.list_accounts(skip=skip, limit=limit, filters=filters)
    
    # Assert
    mock_account_repository.list.assert_called_once_with(skip=skip, limit=limit, filters=filters)
    mock_account_repository.count.assert_called_once_with(filters=filters)
    assert isinstance(result, AccountsPublic)
    assert len(result.data) == 1


def test_update_account(account_service, mock_account_repository, sample_account):
    """Test updating an account."""
    # Arrange
    account_id = sample_account.id
    update_data = {"name": "Updated Account Name", "is_active": False}
    mock_account_repository.update.return_value = sample_account
    
    # Act
    result = account_service.update_account(account_id, update_data)
    
    # Assert
    mock_account_repository.update.assert_called_once_with(account_id, update_data)
    assert isinstance(result, AccountPublic)
    assert result.id == sample_account.id


def test_delete_account(account_service, mock_account_repository):
    """Test deleting an account."""
    # Arrange
    account_id = uuid.uuid4()
    
    # Act
    account_service.delete_account(account_id)
    
    # Assert
    mock_account_repository.delete.assert_called_once_with(account_id)
