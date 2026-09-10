"""Deprecated: use :mod:`src.food_additives.text_analysis` instead."""

from src.food_additives.text_analysis import *  # noqa: F401,F403
from src.food_additives.text_analysis import (
    contains_animal_keyword,
    contains_phrase,
    extract_adi,
)

__all__ = ["contains_phrase", "contains_animal_keyword", "extract_adi"]
