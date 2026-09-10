"""Deprecated: use :mod:`src.food_additives.build_database` instead."""

from src.food_additives.build_database import *  # noqa: F401,F403
from src.food_additives.build_database import build_database, has_data, main

__all__ = ["build_database", "has_data", "main"]
