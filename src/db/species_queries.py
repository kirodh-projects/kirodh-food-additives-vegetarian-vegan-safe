"""Deprecated: use :mod:`src.species.queries` instead."""

from src.species.queries import *  # noqa: F401,F403
from src.species.queries import (
    browse_species,
    build_stats_cache,
    get_species_distinct_values,
    get_species_stats,
    get_species_total_count,
    get_trait_distribution,
    search_species,
)

__all__ = [
    "search_species",
    "browse_species",
    "get_species_total_count",
    "get_species_stats",
    "get_trait_distribution",
    "get_species_distinct_values",
    "build_stats_cache",
]
