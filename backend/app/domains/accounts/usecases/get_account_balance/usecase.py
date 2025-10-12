"""Usecase for calculating account balance."""

from datetime import date, datetime

from app.constants import DEFAULT_START_DATE
from app.domains.accounts.domain.models import (
    AccountBalanceDetails,
    AccountBalancePublic,
    AccountBalanceSummary,
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


class GetAccountBalanceUseCase:
    """Usecase for calculating account balance."""

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
        as_of_date: date | None = None,
    ) -> AccountBalancePublic:
        """Execute the usecase to calculate account balance.

        Args:
            account_name: Name of the account to calculate balance for
            as_of_date: Date to calculate balance as of (defaults to current date)

        Returns:
            AccountBalancePublic: Account balance information
        """
        # Determine effective date
        effective_date: date = as_of_date or datetime.now().date()

        # Create search options for expenses with account filter
        expense_filters = expense_opts.SearchFilters(
            from_date=DEFAULT_START_DATE,
            to_date=effective_date,
            account=account_name,  # Filter by account at database level
        )
        expense_options = (
            expense_opts.SearchOptions()
            .with_filters(expense_filters)
            .with_pagination(expense_opts.SearchPagination(skip=0, limit=10000))
        )

        # Get filtered expenses directly from database
        expenses = self.expense_service.search_expenses(expense_options)

        expense_total_ars = sum(expense.amount_ars for expense in expenses.data)
        expense_total_usd = sum(expense.amount_usd for expense in expenses.data)
        expense_total_cars = sum(expense.amount_cars for expense in expenses.data)

        # Create search options for incomes with account filter
        income_filters = income_opts.SearchFilters(
            from_date=DEFAULT_START_DATE,
            to_date=effective_date,
            account=account_name,  # Filter by account at database level
        )
        income_options = (
            income_opts.SearchOptions()
            .with_filters(income_filters)
            .with_pagination(income_opts.SearchPagination(skip=0, limit=10000))
        )

        # Get filtered incomes directly from database
        incomes = self.income_service.search_incomes(income_options)

        income_total_ars = sum(income.amount_ars for income in incomes.data)
        income_total_usd = sum(income.amount_usd for income in incomes.data)
        income_total_cars = sum(income.amount_cars for income in incomes.data)

        # Calculate balance (Income - Expenses)
        balance_ars = income_total_ars - expense_total_ars
        balance_usd = income_total_usd - expense_total_usd
        balance_cars = income_total_cars - expense_total_cars

        # Create summary objects
        balance_summary = AccountBalanceSummary(
            amount_ars=balance_ars,
            amount_usd=balance_usd,
            amount_cars=balance_cars,
        )

        income_summary = AccountTransactionSummary(
            amount_ars=income_total_ars,
            amount_usd=income_total_usd,
            amount_cars=income_total_cars,
            count=incomes.count,
        )

        expense_summary = AccountTransactionSummary(
            amount_ars=expense_total_ars,
            amount_usd=expense_total_usd,
            amount_cars=expense_total_cars,
            count=expenses.count,
        )

        balance_details = AccountBalanceDetails(
            income=income_summary,
            expenses=expense_summary,
        )

        # Return proper model
        return AccountBalancePublic(
            account_name=account_name,
            as_of_date=effective_date.isoformat(),
            balance=balance_summary,
            totals=balance_details,
            transaction_count=incomes.count + expenses.count,
        )


def provide() -> GetAccountBalanceUseCase:
    """Provide an instance of GetAccountBalanceUseCase.

    Returns:
        GetAccountBalanceUseCase: A new instance with the expense and income services
    """
    return GetAccountBalanceUseCase(provide_expense_service(), provide_income_service())
