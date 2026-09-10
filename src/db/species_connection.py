"""Deprecated: use :mod:`src.species.connection` instead."""

from src.species.connection import *  # noqa: F401,F403
from src.species.connection import (
    ensure_species_db,
    get_db_file_size_mb,
    get_next_species_db_path,
    get_species_connection,
    get_species_db_dir,
    get_stats_cache_path,
    list_species_db_files,
)

__all__ = [
    "ensure_species_db",
    "get_db_file_size_mb",
    "get_next_species_db_path",
    "get_species_connection",
    "get_species_db_dir",
    "get_stats_cache_path",
    "list_species_db_files",
]
