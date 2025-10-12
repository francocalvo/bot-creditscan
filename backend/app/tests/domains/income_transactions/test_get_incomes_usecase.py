"""Unit tests for the get incomes usecase."""

import uuid
from datetime import date, datetime
from unittest.mock import Mock, patch

import pytest

from app.domains.income_transactions.domain.models import Income, IncomePublic, IncomesPublic, SearchOptions
from app.domains.income_transactions.usecases import provide as provide_get_incomes_usecase


@pytest.fixture
def mock_income_repository():
    """Fixture for mocked income repository."""
    mock_repo = Mock()
    mock_repo.db_session = Mock()
    return mock_repo


@pytest.fixture
def mock_income_service():
    """Fixture for mocked income service."""
    mock_service = Mock()
    return mock_service


@pytest.fixture
def get_incomes_usecase(mock_income_service):
    """Fixture for get incomes usecase with mocked service."""
    from app.domains.income_transactions.usecases.get_incomes.usecase import GetIncomesUseCase
    return GetIncomesUseCase(mock_income_service)


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
def sample_income_public(sample_income):
    """Fixture for sample income public."""
    return IncomePublic(
        id=sample_income.id,
        date=sample_income.date,
        account=sample_income.account,
        payee=sample_income.payee,
        narration=sample_income.narration,
        amount_ars=sample_income.amount_ars,
        amount_usd=sample_income.amount_usd,
        amount_cars=sample_income.amount_cars,
        origin=sample_income.origin
    )


def test_execute_usecase(get_incomes_usecase, mock_income_service, sample_income_public):
    """Test executing the get incomes usecase with the new search flow."""
    # Arrange
    from_date = date(2023, 1, 1)
    to_date = date(2023, 12, 31)
    origin = "Salary"
    currencies = ["ARS"]
    skip = 0
    limit = 10
    
    # Expected result from service
    expected_result = IncomesPublic(
        data=[sample_income_public],
        count=1,
        pagination={"skip": skip, "limit": limit, "total_pages": 1}
    )
    
    # Mock the service's search_incomes method
    mock_income_service.search_incomes.return_value = expected_result
    
    # Act
    result = get_incomes_usecase.execute(
        from_date=from_date,
        to_date=to_date,
        origin=origin,
        currencies=currencies,
        skip=skip,
        limit=limit
    )
    
    # Assert
    # Verify the search options were created correctly
    mock_income_service.search_incomes.assert_called_once()
    search_options = mock_income_service.search_incomes.call_args[0][0]
    assert isinstance(search_options, SearchOptions)
    assert search_options.from_date == from_date.isoformat()
    assert search_options.to_date == to_date.isoformat()
    assert search_options.origin == origin
    assert search_options.skip == skip
    assert search_options.limit == limit
    
    # Verify the result structure
    assert isinstance(result, IncomesPublic)
    assert len(result.data) == 1
    assert isinstance(result.data[0], IncomePublic)
    assert result.count == 1
    assert result.pagination["skip"] == skip
    assert result.pagination["limit"] == limit


def test_execute_usecase_default_params(get_incomes_usecase, mock_income_service, sample_income_public):
    """Test executing the get incomes usecase with default parameters."""
    # Arrange
    from_date = date(2023, 1, 1)
    
    # Expected result with default pagination
    expected_result = IncomesPublic(
        data=[sample_income_public],
        count=1,
        pagination={"skip": 0, "limit": 50, "total_pages": 1}
    )
    
    # Mock the service's search_incomes method
    mock_income_service.search_incomes.return_value = expected_result
    
    # Act
    result = get_incomes_usecase.execute(from_date=from_date)
    
    # Assert
    # Verify search options with default values
    mock_income_service.search_incomes.assert_called_once()
    search_options = mock_income_service.search_incomes.call_args[0][0]
    assert isinstance(search_options, SearchOptions)
    assert search_options.from_date == from_date.isoformat()
    assert search_options.to_date is None
    assert search_options.origin is None
    assert search_options.skip == 0
    assert search_options.limit == 50
    
    # Verify result
    assert isinstance(result, IncomesPublic)
    assert len(result.data) == 1
    assert result.pagination["skip"] == 0
    assert result.pagination["limit"] == 50


def test_execute_usecase_currency_filtering(get_incomes_usecase, mock_income_service, sample_income, sample_income_public):
    """Test executing the get incomes usecase with currency filtering."""
    # Arrange
    from_date = date(2023, 1, 1)
    currencies = ["USD"]
    
    # Create a modified income public with only USD currency
    usd_income = IncomePublic(
        id=sample_income.id,
        date=sample_income.date,
        account=sample_income.account,
        payee=sample_income.payee,
        narration=sample_income.narration,
        amount_ars=0.0,  # Include all required fields
        amount_usd=sample_income.amount_usd,
        amount_cars=0.0,  # Include all required fields
        origin=sample_income.origin
    )
    
    # Expected result with currency filtering
    expected_result = IncomesPublic(
        data=[usd_income],
        count=1,
        pagination={"skip": 0, "limit": 50, "total_pages": 1}
    )
    
    # Mock the service's search_incomes method
    mock_income_service.search_incomes.return_value = expected_result
    
    # Act
    result = get_incomes_usecase.execute(
        from_date=from_date,
        currencies=currencies
    )
    
    # Assert
    # Verify search options
    mock_income_service.search_incomes.assert_called_once()
    search_options = mock_income_service.search_incomes.call_args[0][0]
    assert isinstance(search_options, SearchOptions)
    assert search_options.from_date == from_date.isoformat()
    
    # Verify result with currency filtering
    assert isinstance(result, IncomesPublic)
    assert len(result.data) == 1
    
    # Check that USD amount is included in the response
    income_dict = result.data[0].model_dump()
    assert income_dict["amount_usd"] == sample_income.amount_usd
    assert income_dict["amount_ars"] == 0.0  # Should be zero for USD currency filter
