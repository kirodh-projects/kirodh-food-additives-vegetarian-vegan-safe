"""Deprecated: use :mod:`src.food_additives.normalizers` instead."""

from src.food_additives.normalizers import *  # noqa: F401,F403
from src.food_additives.normalizers import (
    deduplicate_records,
    extract_numeric_base,
    normalize_category,
    normalize_e_code,
    normalize_halal_status,
    normalize_ins_code,
)

__all__ = [
    "normalize_e_code",
    "extract_numeric_base",
    "normalize_category",
    "normalize_halal_status",
    "normalize_ins_code",
    "deduplicate_records",
]
