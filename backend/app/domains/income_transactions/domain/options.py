from datetime import date
from enum import Enum

from app.constants import DEFAULT_PAGINATION_LIMIT


class SortOrder(Enum):
    """Enumeration for sorting order."""

    ASC = "asc"
    DESC = "desc"


class SearchFilters:
    """Options for searching income transactions."""

    from_date: date | None = None
    to_date: date | None = None
    origin: str | None = None
    account: str | None = None

    def __init__(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
        origin: str | None = None,
        account: str | None = None,
    ):
        self.from_date = from_date
        self.to_date = to_date
        self.origin = origin if origin else None
        self.account = account if account else None


class SearchPagination:
    """Options for paginating search results."""

    skip: int = 0
    limit: int = 50

    def __init__(self, skip: int = 0, limit: int = DEFAULT_PAGINATION_LIMIT):
        self.skip = skip
        self.limit = limit if limit > 0 else DEFAULT_PAGINATION_LIMIT


class SearchSorting:
    """Options for sorting search results."""

    sort_by: str | None = None
    sort_order: SortOrder | None = None

    def __init__(
        self,
        sort_by: str | None = None,
        sort_order: SortOrder | None = None,
    ):
        self.sort_by = sort_by
        self.sort_order = sort_order if sort_order else None


class SearchOptions:
    """Options for searching income transactions."""

    filters: SearchFilters
    pagination: SearchPagination
    sorting: SearchSorting

    def __init__(self):
        self.filters = SearchFilters()
        self.pagination = SearchPagination(skip=0, limit=DEFAULT_PAGINATION_LIMIT)
        self.sorting = SearchSorting()

    def with_filters(self, filters: SearchFilters) -> "SearchOptions":
        """Create a new search with specified filters."""
        self.filters = filters
        return self

    def with_pagination(self, pagination: SearchPagination) -> "SearchOptions":
        """Create a new search with specified pagination."""
        self.pagination = pagination
        return self

    def with_sorting(self, sorting: SearchSorting) -> "SearchOptions":
        """Create a new search with specified sorting options."""
        self.sorting = sorting
        return self
