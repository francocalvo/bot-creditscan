"""Usecase for retrieving account transactions."""

from datetime import date, datetime

from app.constants import DEFAULT_START_DATE
from app.domains.accounts.domain.models import (
    AccountTransactionsPublic,
    AccountTransactionSummary,
)
from app.domains.expenses_transactions.domain import options as expense_opts
from app.domains.expenses_transactions.service import (
    ExpenseService,
    provide_expense_service,
)
from app.domains.income_transactions.domain import options as income_opts
from app.domains.income_transactions.service import (
    IncomeService,
    provide_income_service,
)


class GetAccountTransactionsUseCase:
    """Usecase for retrieving account transactions (both income and expense)."""

    def __init__(
        self,
        expense_service: ExpenseService,
        income_service: IncomeService,
    ) -> None:
        """Initialize the usecase with expense and income services.

        Args:
            expense_service: Service for handling expense transactions
            income_service: Service for handling income transactions
        """
        self.expense_service = expense_service
        self.income_service = income_service

    def execute(
        self,
        account_name: str,
        from_date: date | None = None,
        to_date: date | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> AccountTransactionsPublic:
        """Execute the usecase to retrieve account transactions.

        Args:
            account_name: Name of the account to filter transactions
            from_date: Start date for filtering (defaults to DEFAULT_START_DATE if None)
            to_date: End date for filtering (defaults to current date if None)
            skip: Number of records to skip
            limit: Number of records to return

        Returns:
            AccountTransactionsPublic: Combined transactions data with expenses and income
        """
        # Use default dates if not provided
        effective_from_date: date = from_date or DEFAULT_START_DATE
        effective_to_date: date = to_date or datetime.now().date()

        # Create search options for expenses with account filter
        expense_filters = expense_opts.SearchFilters(
            from_date=effective_from_date,
            to_date=effective_to_date,
            account=account_name,  # Filter by account at database level
        )
        expense_pagination = expense_opts.SearchPagination(
            skip=skip,
            limit=limit,
        )
        expense_options = (
            expense_opts.SearchOptions()
            .with_filters(expense_filters)
            .with_pagination(expense_pagination)
        )

        # Get filtered expenses directly from database
        expenses = self.expense_service.search_expenses(expense_options)

        # Calculate totals for expenses
        expense_total_ars = sum(expense.amount_ars for expense in expenses.data)
        expense_total_usd = sum(expense.amount_usd for expense in expenses.data)
        expense_total_cars = sum(expense.amount_cars for expense in expenses.data)

        # Create search options for incomes with account filter
        income_filters = income_opts.SearchFilters(
            from_date=effective_from_date,
            to_date=effective_to_date,
            account=account_name,  # Filter by account at database level
        )
        income_pagination = income_opts.SearchPagination(
            skip=skip,
            limit=limit,
        )
        income_options = (
            income_opts.SearchOptions()
            .with_filters(income_filters)
            .with_pagination(income_pagination)
        )

        # Get filtered incomes directly from database
        incomes = self.income_service.search_incomes(income_options)

        # Calculate totals for incomes
        income_total_ars = sum(income.amount_ars for income in incomes.data)
        income_total_usd = sum(income.amount_usd for income in incomes.data)
        income_total_cars = sum(income.amount_cars for income in incomes.data)

        # Create summary objects
        expense_summary = AccountTransactionSummary(
            amount_ars=expense_total_ars,
            amount_usd=expense_total_usd,
            amount_cars=expense_total_cars,
            count=expenses.count,
        )

        income_summary = AccountTransactionSummary(
            amount_ars=income_total_ars,
            amount_usd=income_total_usd,
            amount_cars=income_total_cars,
            count=incomes.count,
        )

        return AccountTransactionsPublic(
            account_name=account_name,
            from_date=effective_from_date.isoformat(),
            to_date=effective_to_date.isoformat(),
            expenses=expenses.data,
            incomes=incomes.data,
            expenses_summary=expense_summary,
            incomes_summary=income_summary,
            total_transactions=expenses.count + incomes.count,
        )


def provide() -> GetAccountTransactionsUseCase:
    """Provide an instance of GetAccountTransactionsUseCase.

    Returns:
        GetAccountTransactionsUseCase: A new instance with the expense and income services
    """
    return GetAccountTransactionsUseCase(
        provide_expense_service(), provide_income_service()
    )
