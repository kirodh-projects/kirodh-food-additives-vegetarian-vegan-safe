"""Deprecated: use :mod:`src.species.build_database` instead."""

from src.species.build_database import *  # noqa: F401,F403
from src.species.build_database import build_species_database, download_backbone, main

__all__ = ["build_species_database", "download_backbone", "main"]
