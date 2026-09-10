"""Deprecated: use :mod:`src.food_additives.schema` instead."""

from src.food_additives.schema import *  # noqa: F401,F403
from src.food_additives.schema import create_tables

__all__ = ["create_tables"]
