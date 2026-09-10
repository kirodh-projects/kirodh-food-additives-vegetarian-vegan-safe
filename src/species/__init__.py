"""Species taxonomy domain package.

Everything related to the GBIF Backbone Taxonomy lives here:

- Database layer: :mod:`src.species.schema`,
  :mod:`src.species.connection`, :mod:`src.species.queries`
- ETL pipeline: :mod:`src.species.build_database`
- Trait heuristics: :mod:`src.species.traits`
- UI: :mod:`src.species.ui.species_page`

The database is split across many ``species_*.db`` SQLite files
(~45 MB each) plus a ``species_stats_cache.json`` cache.

Usage:
    python -m src.species.build_database [--force] [--db-dir DIR]
"""

from src.species.connection import (
    ensure_species_db,
    get_species_connection,
    get_species_db_dir,
    list_species_db_files,
)

__all__ = [
    "ensure_species_db",
    "get_species_connection",
    "get_species_db_dir",
    "list_species_db_files",
]
