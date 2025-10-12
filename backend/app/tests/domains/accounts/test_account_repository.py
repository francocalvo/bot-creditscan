"""Unit tests for the account repository."""

import uuid

import pytest
from sqlmodel import Session

from app.domains.accounts.domain.errors import AccountNotFoundError
from app.domains.accounts.domain.models import Account, AccountCreate
from app.domains.accounts.repository.account_repository import AccountRepository


@pytest.fixture
def account_repository(db: Session):
    """Fixture for account repository with test database."""
    return AccountRepository(db)


@pytest.fixture
def sample_account_data():
    """Fixture for sample account data."""
    return AccountCreate(
        name="Savings Account",
        type="savings",
        currency="ARS",
        description="Personal savings account",
        is_active=True,
    )


def test_create_account(account_repository, sample_account_data):
    """Test creating an account."""
    # Act
    account = account_repository.create(sample_account_data)

    # Assert
    assert account.id is not None
    assert account.name == sample_account_data.name
    assert account.type == sample_account_data.type
    assert account.currency == sample_account_data.currency
    assert account.description == sample_account_data.description
    assert account.is_active == sample_account_data.is_active


def test_get_by_id(account_repository, sample_account_data):
    """Test getting an account by ID."""
    # Arrange
    created_account = account_repository.create(sample_account_data)

    # Act
    account = account_repository.get_by_id(created_account.id)

    # Assert
    assert account.id == created_account.id
    assert account.name == sample_account_data.name
    assert account.type == sample_account_data.type


def test_get_by_id_not_found(account_repository):
    """Test getting a non-existent account."""
    # Arrange
    non_existent_id = uuid.uuid4()

    # Act & Assert
    with pytest.raises(AccountNotFoundError):
        account_repository.get_by_id(non_existent_id)


def test_list_accounts(account_repository, sample_account_data):
    """Test listing accounts."""
    # Arrange
    account_repository.create(sample_account_data)

    # Act
    accounts = account_repository.list()

    # Assert
    assert len(accounts) >= 1
    assert isinstance(accounts[0], Account)


def test_list_accounts_with_filters(account_repository, sample_account_data):
    """Test listing accounts with filters."""
    # Arrange
    account = account_repository.create(sample_account_data)

    # Act
    accounts = account_repository.list(filters={"type": account.type})

    # Assert
    assert len(accounts) >= 1
    assert all(a.type == account.type for a in accounts)


def test_count_accounts(account_repository, sample_account_data):
    """Test counting accounts."""
    # Arrange
    initial_count = account_repository.count()
    account_repository.create(sample_account_data)

    # Act
    new_count = account_repository.count()

    # Assert
    assert new_count >= initial_count + 1


def test_count_accounts_with_filters(account_repository, sample_account_data):
    """Test counting accounts with filters."""
    # Arrange
    account = account_repository.create(sample_account_data)

    # Act
    count = account_repository.count(filters={"currency": account.currency})

    # Assert
    assert count >= 1


def test_update_account(account_repository, sample_account_data):
    """Test updating an account."""
    # Arrange
    account = account_repository.create(sample_account_data)
    update_data = {"name": "Updated Account Name", "is_active": False}

    # Act
    updated_account = account_repository.update(account.id, update_data)

    # Assert
    assert updated_account.id == account.id
    assert updated_account.name == update_data["name"]
    assert updated_account.is_active == update_data["is_active"]
    assert updated_account.type == account.type  # Unchanged field


def test_delete_account(account_repository, sample_account_data):
    """Test deleting an account."""
    # Arrange
    account = account_repository.create(sample_account_data)

    # Act
    account_repository.delete(account.id)

    # Assert
    with pytest.raises(AccountNotFoundError):
        account_repository.get_by_id(account.id)
