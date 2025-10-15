"""Domain-driven architecture for FindDash backend.

This module serves as a simple entry point to the domain-driven architecture.
Users should import directly from the specific domain modules they need:

- app.domains.users.domain: User domain models and errors
- app.domains.users.repository: User repository
- app.domains.users.service: User service

- app.domains.card_statements.domain: Card statement domain models and errors
- app.domains.card_statements.repository: Card statement repository
- app.domains.card_statements.service: Card statement service

Each repository and service module provides a `Provide()` function that returns
an idempotent instance with all dependencies resolved.
"""

# This file intentionally left mostly empty to encourage direct imports
# from the specific domain modules
