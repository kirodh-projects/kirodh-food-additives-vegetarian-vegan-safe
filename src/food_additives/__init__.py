"""Food additives domain package.

Everything related to E-numbers / INS food additives lives here:

- Database layer: :mod:`src.food_additives.schema`,
  :mod:`src.food_additives.connection`, :mod:`src.food_additives.queries`
- ETL pipeline: :mod:`src.food_additives.build_database`,
  :mod:`src.food_additives.parsers`, :mod:`src.food_additives.normalizers`,
  :mod:`src.food_additives.classifiers`, :mod:`src.food_additives.e_ins_mapper`,
  :mod:`src.food_additives.web_scraper`
- Classification data: :mod:`src.food_additives.constants`,
  :mod:`src.food_additives.text_analysis`
- Maintenance: :mod:`src.food_additives.duplicates`
- UI: :mod:`src.food_additives.ui`

Usage:
    python -m src.food_additives.build_database [--force]
    python -m src.food_additives.duplicates [--db-path PATH]
"""

from src.food_additives.connection import ensure_database, get_connection, get_db_path

__all__ = ["ensure_database", "get_connection", "get_db_path"]
