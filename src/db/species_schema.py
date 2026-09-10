"""Deprecated: use :mod:`src.species.schema` instead."""

from src.species.schema import *  # noqa: F401,F403
from src.species.schema import create_species_tables

__all__ = ["create_species_tables"]
