"""Deprecated: use :mod:`src.food_additives.classifiers` instead."""

from src.food_additives.classifiers import *  # noqa: F401,F403
from src.food_additives.classifiers import (
    classify_all,
    classify_origin,
    classify_safety,
    classify_vegan,
    classify_vegetarian,
)

__all__ = [
    "classify_vegan",
    "classify_vegetarian",
    "classify_safety",
    "classify_origin",
    "classify_all",
]
