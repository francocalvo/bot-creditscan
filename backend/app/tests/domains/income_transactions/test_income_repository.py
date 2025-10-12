"""Unit tests for the income repository."""

import uuid
from datetime import datetime

import pytest
from sqlmodel import Session

from app.domains.income_transactions.domain.models import Income, IncomeCreate, SearchOptions
from app.domains.income_transactions.domain.errors import IncomeNotFoundError
from app.domains.income_transactions.repository.income_repository import IncomeRepository


@pytest.fixture
def income_repository(db: Session):
    """Fixture for income repository with test database."""
    return IncomeRepository(db)


@pytest.fixture
def sample_income_data():
    """Fixture for sample income data."""
    return IncomeCreate(
        date=datetime.now().date().isoformat(),
        account="Main Account",
        payee="Employer",
        narration="Monthly salary",
        amount_ars=150000.0,
        amount_usd=500.0,
        amount_cars=150000.0,
        origin="Salary"
    )


def test_create_income(income_repository, sample_income_data):
    """Test creating an income transaction."""
    # Act
    income = income_repository.create(sample_income_data)
    
    # Assert
    assert income.id is not None
    assert income.date == sample_income_data.date
    assert income.account == sample_income_data.account
    assert income.payee == sample_income_data.payee
    assert income.narration == sample_income_data.narration
    assert income.amount_ars == sample_income_data.amount_ars
    assert income.amount_usd == sample_income_data.amount_usd
    assert income.amount_cars == sample_income_data.amount_cars
    assert income.origin == sample_income_data.origin


def test_get_by_id(income_repository, sample_income_data):
    """Test getting an income transaction by ID."""
    # Arrange
    created_income = income_repository.create(sample_income_data)
    
    # Act
    income = income_repository.get_by_id(created_income.id)
    
    # Assert
    assert income.id == created_income.id
    assert income.date == sample_income_data.date
    assert income.account == sample_income_data.account


def test_get_by_id_not_found(income_repository):
    """Test getting a non-existent income transaction."""
    # Arrange
    non_existent_id = uuid.uuid4()
    
    # Act & Assert
    with pytest.raises(IncomeNotFoundError):
        income_repository.get_by_id(non_existent_id)


def test_list_incomes(income_repository, sample_income_data):
    """Test listing income transactions."""
    # Arrange
    income_repository.create(sample_income_data)
    
    # Act
    incomes = income_repository.list()
    
    # Assert
    assert len(incomes) >= 1
    assert isinstance(incomes[0], Income)


def test_list_incomes_with_filters(income_repository, sample_income_data):
    """Test listing income transactions with filters."""
    # Arrange
    income = income_repository.create(sample_income_data)
    
    # Act
    incomes = income_repository.list(filters={"origin": income.origin})
    
    # Assert
    assert len(incomes) >= 1
    assert all(i.origin == income.origin for i in incomes)


def test_count_incomes(income_repository, sample_income_data):
    """Test counting income transactions."""
    # Arrange
    initial_count = income_repository.count()
    income_repository.create(sample_income_data)
    
    # Act
    new_count = income_repository.count()
    
    # Assert
    assert new_count >= initial_count + 1


def test_count_incomes_with_filters(income_repository, sample_income_data):
    """Test counting income transactions with filters."""
    # Arrange
    income = income_repository.create(sample_income_data)
    
    # Act
    count = income_repository.count(filters={"origin": income.origin})
    
    # Assert
    assert count >= 1


def test_update_income(income_repository, sample_income_data):
    """Test updating an income transaction."""
    # Arrange
    income = income_repository.create(sample_income_data)
    update_data = {"narration": "Updated narration", "amount_ars": 200000.0}
    
    # Act
    updated_income = income_repository.update(income.id, update_data)
    
    # Assert
    assert updated_income.id == income.id
    assert updated_income.narration == update_data["narration"]
    assert updated_income.amount_ars == update_data["amount_ars"]
    assert updated_income.origin == income.origin  # Unchanged field


def test_delete_income(income_repository, sample_income_data):
    """Test deleting an income transaction."""
    # Arrange
    income = income_repository.create(sample_income_data)
    
    # Act
    income_repository.delete(income.id)
    
    # Assert
    with pytest.raises(IncomeNotFoundError):
        income_repository.get_by_id(income.id)


def test_search_incomes(income_repository, sample_income_data):
    """Test searching income transactions with SearchOptions."""
    # Arrange
    income = income_repository.create(sample_income_data)
    from_date = datetime.strptime(income.date, "%Y-%m-%d").date()
    to_date = from_date.replace(day=from_date.day + 1)
    
    options = SearchOptions(
        from_date=from_date.isoformat(),
        to_date=to_date.isoformat(),
        origin=income.origin,
        skip=0,
        limit=10
    )
    
    # Act
    incomes, count = income_repository.search(options)
    
    # Assert
    assert len(incomes) >= 1
    assert count >= 1
    assert all(i.origin == income.origin for i in incomes)
    assert all(datetime.strptime(i.date, "%Y-%m-%d").date() >= from_date for i in incomes)
    assert all(datetime.strptime(i.date, "%Y-%m-%d").date() < to_date for i in incomes)


def test_search_incomes_with_partial_options(income_repository, sample_income_data):
    """Test searching income transactions with partial SearchOptions."""
    # Arrange
    income = income_repository.create(sample_income_data)
    
    # Only specify origin filter
    options = SearchOptions(
        origin=income.origin,
        skip=0,
        limit=10
    )
    
    # Act
    incomes, count = income_repository.search(options)
    
    # Assert
    assert len(incomes) >= 1
    assert count >= 1
    assert all(i.origin == income.origin for i in incomes)
