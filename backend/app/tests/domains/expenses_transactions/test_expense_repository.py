"""Unit tests for the expense repository."""

import uuid
from datetime import datetime

import pytest
from sqlmodel import Session

from app.domains.expenses_transactions.domain.errors import ExpenseNotFoundError
from app.domains.expenses_transactions.domain.models import Expense, ExpenseCreate
from app.domains.expenses_transactions.repository.expense_repository import (
    ExpenseRepository,
)


@pytest.fixture
def expense_repository(db: Session) -> ExpenseRepository:
    """Fixture for expense repository."""
    return ExpenseRepository(db)


@pytest.fixture
def sample_expense_data() -> ExpenseCreate:
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
        tags="weekly,essentials",
    )


def test_create_expense(
    expense_repository: ExpenseRepository, sample_expense_data: ExpenseCreate
):
    """Test creating an expense."""
    # Act
    expense = expense_repository.create(sample_expense_data)

    # Assert
    assert expense.id is not None
    assert expense.date == sample_expense_data.date
    assert expense.account == sample_expense_data.account
    assert expense.payee == sample_expense_data.payee
    assert expense.narration == sample_expense_data.narration
    assert expense.amount_ars == sample_expense_data.amount_ars
    assert expense.amount_usd == sample_expense_data.amount_usd
    assert expense.amount_cars == sample_expense_data.amount_cars
    assert expense.category == sample_expense_data.category
    assert expense.subcategory == sample_expense_data.subcategory
    assert expense.tags == sample_expense_data.tags


def test_get_by_id(
    expense_repository: ExpenseRepository, sample_expense_data: ExpenseCreate
):
    """Test getting an expense by ID."""
    # Arrange
    created_expense = expense_repository.create(sample_expense_data)

    # Act
    expense = expense_repository.get_by_id(created_expense.id)

    # Assert
    assert expense.id == created_expense.id
    assert expense.date == created_expense.date
    assert expense.category == created_expense.category


def test_get_by_id_not_found(expense_repository: ExpenseRepository):
    """Test getting an expense by ID that doesn't exist."""
    # Arrange
    non_existent_id = uuid.uuid4()

    # Act & Assert
    with pytest.raises(ExpenseNotFoundError):
        expense_repository.get_by_id(non_existent_id)


def test_list_expenses(
    expense_repository: ExpenseRepository, sample_expense_data: ExpenseCreate
):
    """Test listing expenses."""
    # Arrange
    expense_repository.create(sample_expense_data)

    # Act
    expenses = expense_repository.list()

    # Assert
    assert len(expenses) >= 1
    assert isinstance(expenses[0], Expense)


def test_list_expenses_with_filters(
    expense_repository: ExpenseRepository, sample_expense_data: ExpenseCreate
):
    """Test listing expenses with filters."""
    # Arrange
    expense = expense_repository.create(sample_expense_data)

    # Act
    expenses = expense_repository.list(filters={"category": expense.category})

    # Assert
    assert len(expenses) >= 1
    assert all(e.category == expense.category for e in expenses)


def test_count_expenses(
    expense_repository: ExpenseRepository, sample_expense_data: ExpenseCreate
):
    """Test counting expenses."""
    # Arrange
    expense_repository.create(sample_expense_data)

    # Act
    count = expense_repository.count()

    # Assert
    assert count >= 1


def test_count_expenses_with_filters(
    expense_repository: ExpenseRepository, sample_expense_data: ExpenseCreate
):
    """Test counting expenses with filters."""
    # Arrange
    expense = expense_repository.create(sample_expense_data)

    # Act
    count = expense_repository.count(filters={"category": expense.category})

    # Assert
    assert count >= 1


def test_update_expense(
    expense_repository: ExpenseRepository, sample_expense_data: ExpenseCreate
):
    """Test updating an expense."""
    # Arrange
    expense = expense_repository.create(sample_expense_data)
    update_data = {"narration": "Updated narration", "amount_ars": 6000.0}

    # Act
    updated_expense = expense_repository.update(expense.id, update_data)

    # Assert
    assert updated_expense.id == expense.id
    assert updated_expense.narration == "Updated narration"
    assert updated_expense.amount_ars == 6000.0
    assert updated_expense.category == expense.category  # Unchanged field


def test_delete_expense(
    expense_repository: ExpenseRepository, sample_expense_data: ExpenseCreate
):
    """Test deleting an expense."""
    # Arrange
    expense = expense_repository.create(sample_expense_data)

    # Act
    expense_repository.delete(expense.id)

    # Assert
    with pytest.raises(ExpenseNotFoundError):
        expense_repository.get_by_id(expense.id)
