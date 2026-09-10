"""Deprecated: use :mod:`src.food_additives.parsers` instead."""

from src.food_additives.parsers import *  # noqa: F401,F403
from src.food_additives.parsers import (
    parse_additives_csv,
    parse_classification_csv,
    parse_e_assets_csvs,
    parse_e_index_csv,
    parse_ins_index_csv,
    parse_merged_csv,
    parse_sqlite_db,
)

__all__ = [
    "parse_additives_csv",
    "parse_e_index_csv",
    "parse_ins_index_csv",
    "parse_e_assets_csvs",
    "parse_classification_csv",
    "parse_merged_csv",
    "parse_sqlite_db",
]
