"""Domain-driven architecture for FindDash backend.

This module serves as a simple entry point to the domain-driven architecture.  
Users should import directly from the specific domain modules they need:

- app.domains.income_transactions.domain: Income domain models and errors
- app.domains.income_transactions.repository: Income repository
- app.domains.income_transactions.service: Income service

- app.domains.expenses_transactions.domain: Expense domain models and errors
- app.domains.expenses_transactions.repository: Expense repository
- app.domains.expenses_transactions.service: Expense service

- app.domains.accounts.domain: Account domain models and errors
- app.domains.accounts.repository: Account repository
- app.domains.accounts.service: Account service

Each repository and service module provides a `Provide()` function that returns
an idempotent instance with all dependencies resolved.
"""

# This file intentionally left mostly empty to encourage direct imports
# from the specific domain modules
