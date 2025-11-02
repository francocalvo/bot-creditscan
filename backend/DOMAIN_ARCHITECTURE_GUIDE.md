# Domain-Driven Architecture Implementation Guide

This guide explains how to implement a new domain in the application. Use this as a step-by-step checklist when adding new models.

## Example: Implementing `card_statement` Domain

### Step 1: Create Domain Directory Structure

```bash
mkdir -p app/domains/card_statements/domain
mkdir -p app/domains/card_statements/repository
mkdir -p app/domains/card_statements/service
mkdir -p app/domains/card_statements/usecases
```

**Why these folders?**
- `domain/` - Contains the core business entities and rules
- `repository/` - Handles database operations (CRUD)
- `service/` - Business logic layer that orchestrates repository operations
- `usecases/` - Specific application features/workflows

---

### Step 2: Define Domain Models (`domain/models.py`)

Create `app/domains/card_statements/domain/models.py`:

```python
"""Card statement domain models."""

import uuid
from datetime import date

from sqlmodel import Field, SQLModel


# Base model with shared properties
class CardStatementBase(SQLModel):
    """Base model for card statements."""
    card_id: uuid.UUID = Field(foreign_key="card.id")
    statement_date: date
    due_date: date
    minimum_payment: float
    total_amount: float
    is_paid: bool = False


# For creating new records
class CardStatementCreate(CardStatementBase):
    """Model for creating card statement."""
    pass


# Database table model
class CardStatement(CardStatementBase, table=True):
    """Database model for card statements."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


# Public API response model
class CardStatementPublic(CardStatementBase):
    """Public model for card statements."""
    id: uuid.UUID


# For updates (all fields optional)
class CardStatementUpdate(SQLModel):
    """Model for updating card statement."""
    statement_date: date | None = None
    due_date: date | None = None
    minimum_payment: float | None = None
    total_amount: float | None = None
    is_paid: bool | None = None


# For paginated lists
class CardStatementsPublic(SQLModel):
    """Response model for paginated card statements."""
    data: list[CardStatementPublic]
    count: int
```

**Why these models?**
- `Base` - Shared fields for all models (DRY principle)
- `Create` - Input validation for creation
- `Update` - Optional fields for partial updates
- `Public` - Safe data exposure (no sensitive fields)
- Database model (`table=True`) - SQLModel ORM mapping

---

### Step 3: Define Domain Errors (`domain/errors.py`)

Create `app/domains/card_statements/domain/errors.py`:

```python
"""Card statement domain errors."""


class CardStatementError(Exception):
    """Base exception for card statement errors."""
    pass


class CardStatementNotFoundError(CardStatementError):
    """Raised when a card statement is not found."""
    pass


class InvalidCardStatementDataError(CardStatementError):
    """Raised when card statement data is invalid."""
    pass
```

**Why domain errors?**
- Clear error hierarchy
- Domain-specific error messages
- Easy to catch and convert to HTTP exceptions at API layer

---

### Step 4: Define Search Options (`domain/options.py`)

Create `app/domains/card_statements/domain/options.py`:

```python
"""Search options for card statements domain."""

import uuid
from datetime import date
from enum import Enum

from app.constants import DEFAULT_PAGINATION_LIMIT


class SortOrder(Enum):
    """Enumeration for sorting order."""
    ASC = "asc"
    DESC = "desc"


class SearchFilters:
    """Options for searching card statements."""
    
    card_id: uuid.UUID | None = None
    is_paid: bool | None = None
    from_date: date | None = None
    to_date: date | None = None

    def __init__(
        self,
        card_id: uuid.UUID | None = None,
        is_paid: bool | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
    ):
        self.card_id = card_id
        self.is_paid = is_paid
        self.from_date = from_date
        self.to_date = to_date


class SearchPagination:
    """Options for paginating search results."""
    
    skip: int = 0
    limit: int = 50

    def __init__(self, skip: int = 0, limit: int = DEFAULT_PAGINATION_LIMIT):
        self.skip = skip
        self.limit = limit if limit > 0 else DEFAULT_PAGINATION_LIMIT


class SearchSorting:
    """Options for sorting search results."""
    
    field: str = "statement_date"
    order: SortOrder = SortOrder.DESC

    def __init__(self, field: str = "statement_date", order: SortOrder = SortOrder.DESC):
        self.field = field
        self.order = order


class SearchOptions:
    """Options for searching card statements."""
    
    filters: SearchFilters
    pagination: SearchPagination
    sorting: SearchSorting

    def __init__(self):
        self.filters = SearchFilters()
        self.pagination = SearchPagination()
        self.sorting = SearchSorting()

    def with_filters(self, filters: SearchFilters) -> "SearchOptions":
        """Set filters and return self for method chaining."""
        self.filters = filters
        return self

    def with_pagination(self, pagination: SearchPagination) -> "SearchOptions":
        """Set pagination and return self for method chaining."""
        self.pagination = pagination
        return self

    def with_sorting(self, sorting: SearchSorting) -> "SearchOptions":
        """Set sorting and return self for method chaining."""
        self.sorting = sorting
        return self
```

**Why search options?**
- Encapsulates complex query parameters
- Type-safe filtering
- Reusable across different queries
- Method chaining for clean API

---

### Step 5: Create Domain __init__.py

Create `app/domains/card_statements/domain/__init__.py`:

```python
"""Card statement domain models."""

from .errors import (
    CardStatementError,
    CardStatementNotFoundError,
    InvalidCardStatementDataError,
)
from .models import (
    CardStatement,
    CardStatementBase,
    CardStatementCreate,
    CardStatementPublic,
    CardStatementsPublic,
    CardStatementUpdate,
)

__all__ = [
    "CardStatement",
    "CardStatementBase",
    "CardStatementCreate",
    "CardStatementError",
    "CardStatementNotFoundError",
    "CardStatementPublic",
    "CardStatementsPublic",
    "CardStatementUpdate",
    "InvalidCardStatementDataError",
]
```

---

### Step 6: Create Repository (`repository/card_statement_repository.py`)

Create `app/domains/card_statements/repository/card_statement_repository.py`:

```python
"""Card statement repository implementation."""

import uuid
from functools import lru_cache
from typing import Any

from sqlmodel import Session, func, select

from app.domains.card_statements.domain.errors import CardStatementNotFoundError
from app.domains.card_statements.domain.models import (
    CardStatement,
    CardStatementCreate,
    CardStatementUpdate,
)
from app.pkgs.database import get_db_session


class CardStatementRepository:
    """Repository for card statements."""

    def __init__(self, db_session: Session):
        """Initialize the repository with a database session."""
        self.db_session = db_session

    def create(self, statement_data: CardStatementCreate) -> CardStatement:
        """Create a new card statement."""
        statement = CardStatement.model_validate(statement_data)
        self.db_session.add(statement)
        self.db_session.commit()
        self.db_session.refresh(statement)
        return statement

    def get_by_id(self, statement_id: uuid.UUID) -> CardStatement:
        """Get a card statement by ID."""
        statement = self.db_session.get(CardStatement, statement_id)
        if not statement:
            raise CardStatementNotFoundError(
                f"Card statement with ID {statement_id} not found"
            )
        return statement

    def list(
        self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None
    ) -> list[CardStatement]:
        """List card statements with pagination and filtering."""
        query = select(CardStatement)

        if filters:
            for field, value in filters.items():
                if hasattr(CardStatement, field):
                    query = query.where(getattr(CardStatement, field) == value)

        result = self.db_session.exec(query.offset(skip).limit(limit))
        return list(result)

    def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count card statements with optional filtering."""
        query = select(CardStatement)

        if filters:
            for field, value in filters.items():
                if hasattr(CardStatement, field):
                    query = query.where(getattr(CardStatement, field) == value)

        count_q = (
            query.with_only_columns(func.count())
            .order_by(None)
            .select_from(query.get_final_froms()[0])
        )

        result = self.db_session.exec(count_q)
        for count in result:
            return count  # type: ignore
        return 0

    def update(
        self, statement_id: uuid.UUID, statement_data: CardStatementUpdate
    ) -> CardStatement:
        """Update a card statement."""
        statement = self.get_by_id(statement_id)
        
        update_dict = statement_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(statement, field, value)

        self.db_session.add(statement)
        self.db_session.commit()
        self.db_session.refresh(statement)
        return statement

    def delete(self, statement_id: uuid.UUID) -> None:
        """Delete a card statement."""
        statement = self.get_by_id(statement_id)
        self.db_session.delete(statement)
        self.db_session.commit()


@lru_cache
def provide() -> CardStatementRepository:
    """Provide an instance of CardStatementRepository."""
    return CardStatementRepository(get_db_session())
```

**Why repository?**
- Single responsibility: database operations only
- Testable (can mock database)
- Caching with `@lru_cache`
- Domain error handling

Create `app/domains/card_statements/repository/__init__.py`:

```python
"""Card statement repository."""

from .card_statement_repository import CardStatementRepository
from .card_statement_repository import provide as provide_card_statement_repository

__all__ = ["CardStatementRepository", "provide_card_statement_repository"]
```

---

### Step 7: Create Service (`service/card_statement_service.py`)

Create `app/domains/card_statements/service/card_statement_service.py`:

```python
"""Card statement service implementation."""

import uuid
from functools import lru_cache
from typing import Any

from app.domains.card_statements.domain.models import (
    CardStatementCreate,
    CardStatementPublic,
    CardStatementsPublic,
    CardStatementUpdate,
)
from app.domains.card_statements.repository import provide_card_statement_repository
from app.domains.card_statements.repository.card_statement_repository import (
    CardStatementRepository,
)


class CardStatementService:
    """Service for card statements."""

    def __init__(self, repository: CardStatementRepository):
        """Initialize the service with a repository."""
        self.repository = repository

    def create_statement(self, statement_data: CardStatementCreate) -> CardStatementPublic:
        """Create a new card statement."""
        statement = self.repository.create(statement_data)
        return CardStatementPublic.model_validate(statement)

    def get_statement(self, statement_id: uuid.UUID) -> CardStatementPublic:
        """Get a card statement by ID."""
        statement = self.repository.get_by_id(statement_id)
        return CardStatementPublic.model_validate(statement)

    def list_statements(
        self, skip: int = 0, limit: int = 100, filters: dict[str, Any] | None = None
    ) -> CardStatementsPublic:
        """List card statements with pagination and filtering."""
        statements = self.repository.list(skip=skip, limit=limit, filters=filters)
        count = self.repository.count(filters=filters)

        return CardStatementsPublic(
            data=[CardStatementPublic.model_validate(s) for s in statements],
            count=count,
        )

    def update_statement(
        self, statement_id: uuid.UUID, statement_data: CardStatementUpdate
    ) -> CardStatementPublic:
        """Update a card statement."""
        statement = self.repository.update(statement_id, statement_data)
        return CardStatementPublic.model_validate(statement)

    def delete_statement(self, statement_id: uuid.UUID) -> None:
        """Delete a card statement."""
        self.repository.delete(statement_id)


@lru_cache
def provide() -> CardStatementService:
    """Provide an instance of CardStatementService."""
    return CardStatementService(provide_card_statement_repository())
```

**Why service layer?**
- Business logic orchestration
- Converts between domain and public models
- Can combine multiple repository calls
- Additional validation/business rules

Create `app/domains/card_statements/service/__init__.py`:

```python
"""Card statement service."""

from .card_statement_service import CardStatementService
from .card_statement_service import provide as provide_card_statement_service

__all__ = ["CardStatementService", "provide_card_statement_service"]
```

---

### Step 8: Create Use Cases (`usecases/`)

For each feature, create a usecase. Example for listing:

Create `app/domains/card_statements/usecases/list_statements/__init__.py`:
```python
"""List card statements usecase."""

from .usecase import ListCardStatementsUseCase, provide

__all__ = ["ListCardStatementsUseCase", "provide"]
```

Create `app/domains/card_statements/usecases/list_statements/usecase.py`:

```python
"""Usecase for listing card statements."""

from app.domains.card_statements.domain.models import CardStatementsPublic
from app.domains.card_statements.service import CardStatementService
from app.domains.card_statements.service import provide as provide_service


class ListCardStatementsUseCase:
    """Usecase for listing card statements with pagination."""

    def __init__(self, service: CardStatementService) -> None:
        """Initialize the usecase with a service."""
        self.service = service

    def execute(
        self, skip: int = 0, limit: int = 100, card_id: str | None = None
    ) -> CardStatementsPublic:
        """Execute the usecase to list card statements.
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            card_id: Optional filter by card ID
            
        Returns:
            CardStatementsPublic: Paginated statements data
        """
        filters = {}
        if card_id:
            filters["card_id"] = card_id
            
        return self.service.list_statements(skip=skip, limit=limit, filters=filters)


def provide() -> ListCardStatementsUseCase:
    """Provide an instance of ListCardStatementsUseCase."""
    return ListCardStatementsUseCase(provide_service())
```

**Why use cases?**
- One use case = one feature/workflow
- Clear application entry points
- Easy to test business logic
- Coordinates between services

Repeat for other operations:
- `create_statement/`
- `update_statement/`
- `delete_statement/`
- `mark_statement_paid/` (custom business logic)

Create `app/domains/card_statements/usecases/__init__.py`:

```python
"""Card statement usecases."""

from .list_statements import ListCardStatementsUseCase, provide as provide_list_statements
# Import other usecases...

__all__ = [
    "ListCardStatementsUseCase",
    "provide_list_statements",
    # Export other usecases...
]
```

---

### Step 9: Create Domain __init__.py

Create `app/domains/card_statements/__init__.py`:

```python
"""Card statements domain module."""

from .domain import (
    CardStatement,
    CardStatementCreate,
    CardStatementError,
    CardStatementNotFoundError,
    CardStatementPublic,
    CardStatementsPublic,
    CardStatementUpdate,
)
from .repository import CardStatementRepository, provide_card_statement_repository
from .service import CardStatementService, provide_card_statement_service

__all__ = [
    "CardStatement",
    "CardStatementCreate",
    "CardStatementError",
    "CardStatementNotFoundError",
    "CardStatementPublic",
    "CardStatementsPublic",
    "CardStatementUpdate",
    "CardStatementRepository",
    "CardStatementService",
    "provide_card_statement_repository",
    "provide_card_statement_service",
]
```

---

### Step 10: Create API Routes (`api/routes/card_statements/`)

Create directory:
```bash
mkdir -p app/api/routes/card_statements
```

Create `app/api/routes/card_statements/list_statements.py`:

```python
"""List card statements endpoint."""

from typing import Any

from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.domains.card_statements.domain.models import CardStatementsPublic
from app.domains.card_statements.usecases import provide_list_statements

router = APIRouter()


@router.get("/", response_model=CardStatementsPublic)
def list_card_statements(
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    card_id: str | None = None,
) -> Any:
    """Retrieve card statements."""
    usecase = provide_list_statements()
    return usecase.execute(skip=skip, limit=limit, card_id=card_id)
```

Create similar files for:
- `create_statement.py` - POST /
- `get_statement.py` - GET /{statement_id}
- `update_statement.py` - PATCH /{statement_id}
- `delete_statement.py` - DELETE /{statement_id}

Create `app/api/routes/card_statements/__init__.py`:

```python
"""Card statements routes module."""

from fastapi import APIRouter

from .list_statements import router as list_statements_router
# Import other routers...

router = APIRouter(prefix="/card-statements", tags=["card-statements"])

router.include_router(list_statements_router)
# Include other routers...

__all__ = ["router"]
```

---

### Step 11: Register in Main API Router

Update `app/api/main.py`:

```python
from fastapi import APIRouter

from app.api.routes import (
    accounts,
    analytics,
    items,
    login,
    private,
    transactions,
    utils,
)
from app.api.routes.card_statements import router as card_statements_router  # Add this
from app.api.routes.users import router as users_router
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users_router)
api_router.include_router(card_statements_router)  # Add this
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(transactions.expenses.router)
api_router.include_router(transactions.income.router)
api_router.include_router(accounts.router)
api_router.include_router(analytics.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
```

---

### Step 12: Update domains/__init__.py Documentation

Update `app/domains/__init__.py` to document the new domain:

```python
"""Domain-driven architecture for FindDash backend.

This module serves as a simple entry point to the domain-driven architecture.  
Users should import directly from the specific domain modules they need:

- app.domains.card_statements.domain: Card statement domain models and errors
- app.domains.card_statements.repository: Card statement repository
- app.domains.card_statements.service: Card statement service

...
"""
```

---

## Architecture Summary

```
Domain Layer (business logic, no external dependencies)
    ↓
Repository Layer (database operations)
    ↓
Service Layer (orchestration, business rules)
    ↓
Use Cases (application features)
    ↓
API Layer (HTTP, validation, error handling)
```

**Key Principles:**
1. **Dependency Flow**: Always inward (API → UseCase → Service → Repository → Domain)
2. **Single Responsibility**: Each file has one clear purpose
3. **Testability**: Each layer can be tested independently
4. **Consistency**: Same structure for all domains
5. **Provider Pattern**: Use `@lru_cache` providers for singleton instances

---

## Quick Checklist

- [ ] Create domain directory structure (4 folders)
- [ ] Define models in `domain/models.py`
- [ ] Define errors in `domain/errors.py`
- [ ] Define options in `domain/options.py`
- [ ] Create repository with CRUD operations
- [ ] Create service layer
- [ ] Create use cases for each feature
- [ ] Create API routes (one file per endpoint)
- [ ] Register routes in main router
- [ ] Update domain documentation
- [ ] Write tests for each layer

