"""Tests for the GetAccountChildrenUseCase."""

import uuid
from unittest.mock import MagicMock, patch

import pytest

from app.domains.accounts.domain.models import Account, AccountPublic
from app.domains.accounts.usecases.get_account_children import GetAccountChildrenUseCase


@pytest.fixture
def mock_account_repository():
    """Create a mock account repository."""
    repository = MagicMock()
    
    # Mock parent account
    parent_account = Account(
        id=uuid.uuid4(),
        name="Parent Account",
        type="checking",
        currency="ARS",
        description="Parent account",
        is_active=True
    )
    
    # Mock child accounts
    child_account1 = Account(
        id=uuid.uuid4(),
        name="Child Account 1",
        type="savings",
        currency="ARS",
        description="Child account 1",
        is_active=True,
        parent_id=parent_account.id
    )
    
    child_account2 = Account(
        id=uuid.uuid4(),
        name="Child Account 2",
        type="investment",
        currency="USD",
        description="Child account 2",
        is_active=True,
        parent_id=parent_account.id
    )
    
    repository.get_by_id.return_value = parent_account
    repository.list.return_value = [child_account1, child_account2]
    return repository


def test_get_account_children(mock_account_repository):
    """Test getting all children of an account."""
    # Arrange
    account_id = uuid.uuid4()
    use_case = GetAccountChildrenUseCase(mock_account_repository)
    
    # Act
    result = use_case.execute(account_id)
    
    # Assert
    mock_account_repository.get_by_id.assert_called_once_with(account_id)
    mock_account_repository.list.assert_called_once_with(filters={"parent_id": account_id})
    
    assert len(result) == 2
    assert isinstance(result[0], AccountPublic)
    assert isinstance(result[1], AccountPublic)
    assert result[0].name == "Child Account 1"
    assert result[1].name == "Child Account 2"
