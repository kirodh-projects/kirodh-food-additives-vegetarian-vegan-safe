"""Deprecated: use :mod:`src.species.traits` instead."""

from src.species.traits import *  # noqa: F401,F403
from src.species.traits import (
    build_trait_update_sql,
    compute_gunas,
    compute_mobility,
    compute_size,
    compute_warm_blood,
    migrate_species_traits,
)

__all__ = [
    "compute_mobility",
    "compute_warm_blood",
    "compute_size",
    "compute_gunas",
    "build_trait_update_sql",
    "migrate_species_traits",
]
