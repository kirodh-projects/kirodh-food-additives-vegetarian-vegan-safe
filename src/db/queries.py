"""Deprecated: use :mod:`src.food_additives.queries` instead."""

from src.food_additives.queries import *  # noqa: F401,F403
from src.food_additives.queries import (
    check_duplicates,
    get_all_additives,
    get_analytics_summary,
    get_category_vegan_breakdown,
    get_dangerous_additives,
    get_distinct_values,
    get_total_count,
    search_by_code,
    search_by_name,
)

__all__ = [
    "search_by_code",
    "search_by_name",
    "get_all_additives",
    "get_total_count",
    "get_analytics_summary",
    "get_dangerous_additives",
    "get_category_vegan_breakdown",
    "check_duplicates",
    "get_distinct_values",
]
