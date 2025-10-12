"""Unit tests for the income service."""

import uuid
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from app.domains.income_transactions.domain.models import Income, IncomeCreate, IncomePublic, IncomesPublic, SearchOptions
from app.domains.income_transactions.domain.errors import IncomeNotFoundError
from app.domains.income_transactions.service.income_service import IncomeService


@pytest.fixture
def mock_income_repository():
    """Fixture for mocked income repository."""
    mock_repo = Mock()
    return mock_repo


@pytest.fixture
def income_service(mock_income_repository):
    """Fixture for income service with mocked repository."""
    return IncomeService(mock_income_repository)


@pytest.fixture
def sample_income():
    """Fixture for sample income."""
    return Income(
        id=uuid.uuid4(),
        date=datetime.now().date().isoformat(),
        account="Main Account",
        payee="Employer",
        narration="Monthly salary",
        amount_ars=150000.0,
        amount_usd=500.0,
        amount_cars=150000.0,
        origin="Salary"
    )


@pytest.fixture
def sample_income_create():
    """Fixture for sample income create data."""
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


def test_create_income(income_service, mock_income_repository, sample_income, sample_income_create):
    """Test creating an income transaction."""
    # Arrange
    mock_income_repository.create.return_value = sample_income
    
    # Act
    result = income_service.create_income(sample_income_create)
    
    # Assert
    mock_income_repository.create.assert_called_once_with(sample_income_create)
    assert isinstance(result, IncomePublic)
    assert result.id == sample_income.id
    assert result.date == sample_income.date
    assert result.account == sample_income.account
    assert result.origin == sample_income.origin


def test_get_income(income_service, mock_income_repository, sample_income):
    """Test getting an income transaction."""
    # Arrange
    income_id = sample_income.id
    mock_income_repository.get_by_id.return_value = sample_income
    
    # Act
    result = income_service.get_income(income_id)
    
    # Assert
    mock_income_repository.get_by_id.assert_called_once_with(income_id)
    assert isinstance(result, IncomePublic)
    assert result.id == sample_income.id


def test_get_income_not_found(income_service, mock_income_repository):
    """Test getting a non-existent income transaction."""
    # Arrange
    income_id = uuid.uuid4()
    mock_income_repository.get_by_id.side_effect = IncomeNotFoundError(f"Income transaction with ID {income_id} not found")
    
    # Act & Assert
    with pytest.raises(IncomeNotFoundError):
        income_service.get_income(income_id)


def test_list_incomes(income_service, mock_income_repository, sample_income):
    """Test listing income transactions."""
    # Arrange
    skip = 0
    limit = 10
    mock_income_repository.list.return_value = [sample_income]
    mock_income_repository.count.return_value = 1
    
    # Act
    result = income_service.list_incomes(skip=skip, limit=limit)
    
    # Assert
    mock_income_repository.list.assert_called_once_with(skip=skip, limit=limit, filters=None)
    mock_income_repository.count.assert_called_once_with(filters=None)
    assert isinstance(result, IncomesPublic)
    assert len(result.data) == 1
    assert result.count == 1
    assert result.pagination["skip"] == skip
    assert result.pagination["limit"] == limit


def test_list_incomes_with_filters(income_service, mock_income_repository, sample_income):
    """Test listing income transactions with filters."""
    # Arrange
    skip = 0
    limit = 10
    filters = {"origin": "Salary"}
    mock_income_repository.list.return_value = [sample_income]
    mock_income_repository.count.return_value = 1
    
    # Act
    result = income_service.list_incomes(skip=skip, limit=limit, filters=filters)
    
    # Assert
    mock_income_repository.list.assert_called_once_with(skip=skip, limit=limit, filters=filters)
    mock_income_repository.count.assert_called_once_with(filters=filters)
    assert isinstance(result, IncomesPublic)
    assert len(result.data) == 1


def test_update_income(income_service, mock_income_repository, sample_income):
    """Test updating an income transaction."""
    # Arrange
    income_id = sample_income.id
    update_data = {"narration": "Updated narration", "amount_ars": 200000.0}
    mock_income_repository.update.return_value = sample_income
    
    # Act
    result = income_service.update_income(income_id, update_data)
    
    # Assert
    mock_income_repository.update.assert_called_once_with(income_id, update_data)
    assert isinstance(result, IncomePublic)
    assert result.id == sample_income.id


def test_delete_income(income_service, mock_income_repository):
    """Test deleting an income transaction."""
    # Arrange
    income_id = uuid.uuid4()
    
    # Act
    income_service.delete_income(income_id)
    
    # Assert
    mock_income_repository.delete.assert_called_once_with(income_id)


def test_search_incomes(income_service, mock_income_repository, sample_income):
    """Test searching income transactions with SearchOptions."""
    # Arrange
    from_date = datetime.now().date()
    to_date = from_date.replace(day=from_date.day + 1)
    origin = "Salary"
    skip = 0
    limit = 10
    
    options = SearchOptions(
        from_date=from_date.isoformat(),
        to_date=to_date.isoformat(),
        origin=origin,
        skip=skip,
        limit=limit
    )
    
    # Mock repository search return
    mock_income_repository.search.return_value = ([sample_income], 1)
    
    # Act
    result = income_service.search_incomes(options)
    
    # Assert
    mock_income_repository.search.assert_called_once_with(options)
    assert isinstance(result, IncomesPublic)
    assert len(result.data) == 1
    assert result.count == 1
    assert result.pagination["skip"] == skip
    assert result.pagination["limit"] == limit
    assert result.pagination["total_pages"] == 1


def test_search_incomes_empty_result(income_service, mock_income_repository):
    """Test searching income transactions with no results."""
    # Arrange
    options = SearchOptions(
        from_date=datetime.now().date().isoformat(),
        skip=0,
        limit=10
    )
    
    # Mock repository search return empty list
    mock_income_repository.search.return_value = ([], 0)
    
    # Act
    result = income_service.search_incomes(options)
    
    # Assert
    mock_income_repository.search.assert_called_once_with(options)
    assert isinstance(result, IncomesPublic)
    assert len(result.data) == 0
    assert result.count == 0
