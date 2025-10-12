from typing import TypeVar

from sqlmodel.sql.expression import SelectOfScalar

from app.domains.expenses_transactions.domain import options as opts
from app.domains.expenses_transactions.domain.models import (
    Expense,
)

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

    if search_filters.from_date:
        query = query.where(Expense.date >= search_filters.from_date)

    if search_filters.to_date:
        query = query.where(Expense.date < search_filters.to_date)

    if search_filters.category:
        query = query.where(Expense.category == search_filters.category)

    if search_filters.subcategory:
        query = query.where(Expense.subcategory == search_filters.subcategory)

    if search_filters.tags:
        query = query.where(Expense.tags == search_filters.tags)

    if search_filters.account:
        # Use regex to match the account and all its children
        # Pattern: account name + any child accounts (account:child1:child2, etc.)
        account_pattern = f"{search_filters.account}%"
        query = query.where(Expense.account.like(account_pattern))

    return query


def build_sorted_search(
    query: SelectOfScalar[_T],
    search_sorting: opts.SearchSorting,
) -> SelectOfScalar[_T]:
    """Build an ordered search query based on search options."""

    if search_sorting.sort_by:
        if search_sorting.sort_order == opts.SortOrder.ASC:
            query = query.order_by(getattr(Expense, search_sorting.sort_by).asc())
        elif search_sorting.sort_order == opts.SortOrder.DESC:
            query = query.order_by(getattr(Expense, search_sorting.sort_by).desc())

    return query


def build_paginated_search(
    query: SelectOfScalar[_T],
    search_pagination: opts.SearchPagination,
) -> SelectOfScalar[_T]:
    """Build a paginated search query based on search options."""

    query = query.offset(search_pagination.skip)
    query = query.limit(search_pagination.limit)

    return query
