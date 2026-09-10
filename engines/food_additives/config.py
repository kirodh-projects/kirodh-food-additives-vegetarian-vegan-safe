"""Local config for the food-additives engine (no cross-engine imports).

Vendored so this engine is self-contained: copy the
``engines/food_additives/`` folder anywhere and it keeps working.
"""

import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_DB_PATH = "./databases/food_additives.db"
DEFAULT_DATA_DIR = "./additive_databases"


def get_db_path() -> str:
    """Path to the food additives SQLite database."""
    return os.getenv("DB_PATH", DEFAULT_DB_PATH)


def get_data_dir() -> str:
    """Path to the raw additive data sources directory."""
    return os.getenv("DATA_DIR", DEFAULT_DATA_DIR)
