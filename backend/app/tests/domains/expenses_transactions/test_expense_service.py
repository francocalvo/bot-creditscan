"""Unit tests for the expense service."""

import uuid
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from app.domains.expenses_transactions.domain.models import ExpenseCreate, Expense, ExpensePublic, ExpensesPublic
from app.domains.expenses_transactions.domain.errors import ExpenseNotFoundError
from app.domains.expenses_transactions.service.expense_service import ExpenseService


@pytest.fixture
def mock_expense_repository():
    """Fixture for mocked expense repository."""
    return Mock()


@pytest.fixture
def expense_service(mock_expense_repository):
    """Fixture for expense service with mocked repository."""
    return ExpenseService(mock_expense_repository)


@pytest.fixture
def sample_expense_data():
    """Fixture for sample expense data."""
    return ExpenseCreate(
        date=datetime.now().date().isoformat(),
        account="Main Account",
        payee="Grocery Store",
        narration="Weekly groceries",
        amount_ars=5000.0,
        amount_usd=10.0,
        amount_cars=5000.0,
        category="Food",
        subcategory="Groceries",
        tags="weekly,essentials"
    )


@pytest.fixture
def sample_expense(sample_expense_data):
    """Fixture for sample expense."""
    expense = Expense.model_validate(sample_expense_data)
    expense.id = uuid.uuid4()
    return expense


def test_create_expense(expense_service, mock_expense_repository, sample_expense_data, sample_expense):
    """Test creating an expense."""
    # Arrange
    mock_expense_repository.create.return_value = sample_expense
    
    # Act
    result = expense_service.create_expense(sample_expense_data)
    
    # Assert
    mock_expense_repository.create.assert_called_once_with(sample_expense_data)
    assert isinstance(result, ExpensePublic)
    assert result.id == sample_expense.id
    assert result.date == sample_expense.date
    assert result.category == sample_expense.category


def test_get_expense(expense_service, mock_expense_repository, sample_expense):
    """Test getting an expense by ID."""
    # Arrange
    expense_id = sample_expense.id
    mock_expense_repository.get_by_id.return_value = sample_expense
    
    # Act
    result = expense_service.get_expense(expense_id)
    
    # Assert
    mock_expense_repository.get_by_id.assert_called_once_with(expense_id)
    assert isinstance(result, ExpensePublic)
    assert result.id == sample_expense.id


def test_get_expense_not_found(expense_service, mock_expense_repository):
    """Test getting an expense that doesn't exist."""
    # Arrange
    expense_id = uuid.uuid4()
    mock_expense_repository.get_by_id.side_effect = ExpenseNotFoundError(f"Expense with ID {expense_id} not found")
    
    # Act & Assert
    with pytest.raises(ExpenseNotFoundError):
        expense_service.get_expense(expense_id)


def test_list_expenses(expense_service, mock_expense_repository, sample_expense):
    """Test listing expenses."""
    # Arrange
    mock_expense_repository.list.return_value = [sample_expense]
    mock_expense_repository.count.return_value = 1
    
    # Act
    result = expense_service.list_expenses()
    
    # Assert
    mock_expense_repository.list.assert_called_once()
    mock_expense_repository.count.assert_called_once()
    assert isinstance(result, ExpensesPublic)
    assert len(result.data) == 1
    assert result.count == 1
    assert isinstance(result.data[0], ExpensePublic)


def test_list_expenses_with_filters(expense_service, mock_expense_repository, sample_expense):
    """Test listing expenses with filters."""
    # Arrange
    filters = {"category": "Food"}
    mock_expense_repository.list.return_value = [sample_expense]
    mock_expense_repository.count.return_value = 1
    
    # Act
    result = expense_service.list_expenses(filters=filters)
    
    # Assert
    mock_expense_repository.list.assert_called_once_with(skip=0, limit=100, filters=filters)
    mock_expense_repository.count.assert_called_once_with(filters=filters)
    assert isinstance(result, ExpensesPublic)
    assert len(result.data) == 1


def test_update_expense(expense_service, mock_expense_repository, sample_expense):
    """Test updating an expense."""
    # Arrange
    expense_id = sample_expense.id
    update_data = {"narration": "Updated narration"}
    updated_expense = sample_expense
    updated_expense.narration = "Updated narration"
    mock_expense_repository.update.return_value = updated_expense
    
    # Act
    result = expense_service.update_expense(expense_id, update_data)
    
    # Assert
    mock_expense_repository.update.assert_called_once_with(expense_id, update_data)
    assert isinstance(result, ExpensePublic)
    assert result.narration == "Updated narration"


def test_delete_expense(expense_service, mock_expense_repository):
    """Test deleting an expense."""
    # Arrange
    expense_id = uuid.uuid4()
    
    # Act
    expense_service.delete_expense(expense_id)
    
    # Assert
    mock_expense_repository.delete.assert_called_once_with(expense_id)
