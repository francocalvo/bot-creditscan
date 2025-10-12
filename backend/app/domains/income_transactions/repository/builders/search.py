from typing import TypeVar

from sqlmodel.sql.expression import SelectOfScalar

from app.domains.income_transactions.domain import options as opts
from app.domains.income_transactions.domain.models import (
    Income,
)

_T = TypeVar("_T")


def build_options(
    query: SelectOfScalar[_T],
    search_options: opts.SearchOptions,
) -> SelectOfScalar[_T]:
    """Build a dictionary of search options."""

    query = build_filtered_search(query, search_options.filters)

    return query


def build_filtered_search(
    query: SelectOfScalar[_T],
    search_filters: opts.SearchFilters,
) -> SelectOfScalar[_T]:
    """Build a filtered search query based on search options."""

    if search_filters.from_date:
        query = query.where(Income.date >= search_filters.from_date)

    if search_filters.to_date:
        query = query.where(Income.date < search_filters.to_date)

    if search_filters.origin:
        query = query.where(Income.origin == search_filters.origin)

    if search_filters.account:
        # Use regex to match the account and all its children
        # Pattern: account name + any child accounts (account:child1:child2, etc.)
        account_pattern = f"{search_filters.account}%"
        query = query.where(Income.account.like(account_pattern))

    return query


def build_sorted_search(
    query: SelectOfScalar[_T],
    search_sorting: opts.SearchSorting,
) -> SelectOfScalar[_T]:
    """Build an ordered search query based on search options."""

    if search_sorting.sort_by:
        if search_sorting.sort_order == opts.SortOrder.ASC:
            query = query.order_by(getattr(Income, search_sorting.sort_by).asc())
        elif search_sorting.sort_order == opts.SortOrder.DESC:
            query = query.order_by(getattr(Income, search_sorting.sort_by).desc())

    return query


def build_paginated_search(
    query: SelectOfScalar[_T],
    search_pagination: opts.SearchPagination,
) -> SelectOfScalar[_T]:
    """Build a paginated search query based on search options."""

    query = query.offset(search_pagination.skip)
    query = query.limit(search_pagination.limit)

    return query
