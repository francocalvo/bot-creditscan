"""Search builder for accounts repository."""

from typing import TypeVar

from sqlmodel import col
from sqlmodel.sql.expression import SelectOfScalar

from app.domains.accounts.domain import options as opts
from app.domains.accounts.domain.models import Account

_T = TypeVar("_T")


def build_options(
    query: SelectOfScalar[_T],
    search_options: opts.SearchOptions,
) -> SelectOfScalar[_T]:
    """Build a dictionary of search options."""

    query = build_filtered_search(query, search_options.filters)
    query = build_sorted_search(query, search_options.sorting)
    query = build_paginated_search(query, search_options.pagination)

    return query


def build_filtered_search(
    query: SelectOfScalar[_T],
    search_filters: opts.SearchFilters,
) -> SelectOfScalar[_T]:
    """Build a filtered search query based on search options."""

    if search_filters.name:
        query = query.where(col(Account.name).contains(search_filters.name))

    if search_filters.type:
        query = query.where(Account.type == search_filters.type)

    if search_filters.currency:
        query = query.where(Account.currency == search_filters.currency)

    if search_filters.is_active is not None:
        query = query.where(Account.is_active == search_filters.is_active)

    if search_filters.parent_id is not None:
        query = query.where(Account.parent_id == search_filters.parent_id)

    return query


def build_sorted_search(
    query: SelectOfScalar[_T],
    search_sorting: opts.SearchSorting,
) -> SelectOfScalar[_T]:
    """Build a sorted search query based on search options."""

    if hasattr(Account, search_sorting.field):
        field = getattr(Account, search_sorting.field)
        if search_sorting.order == opts.SortOrder.DESC:
            query = query.order_by(field.desc())
        else:
            query = query.order_by(field.asc())

    return query


def build_paginated_search(
    query: SelectOfScalar[_T],
    search_pagination: opts.SearchPagination,
) -> SelectOfScalar[_T]:
    """Build a paginated search query based on search options."""

    query = query.offset(search_pagination.skip)
    query = query.limit(search_pagination.limit)

    return query
