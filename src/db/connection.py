"""Deprecated: use :mod:`src.food_additives.connection` instead."""

from src.food_additives.connection import *  # noqa: F401,F403
from src.food_additives.connection import (
    ensure_database,
    get_connection,
    get_db_path,
)

__all__ = ["ensure_database", "get_connection", "get_db_path"]
