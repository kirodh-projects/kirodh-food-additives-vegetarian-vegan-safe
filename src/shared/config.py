"""Central application configuration.

Single place for environment variables and default paths.
Domain modules re-export these helpers for backward compatibility,
but new code should import from here:

    from src.shared.config import get_db_path, get_data_dir, get_species_db_dir
"""

import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_DB_PATH = "./databases/food_additives.db"
DEFAULT_DATA_DIR = "./additive_databases"
DEFAULT_SPECIES_DB_DIR = "./databases"


def get_db_path() -> str:
    """Path to the food additives SQLite database."""
    return os.getenv("DB_PATH", DEFAULT_DB_PATH)


def get_data_dir() -> str:
    """Path to the raw additive data sources directory."""
    return os.getenv("DATA_DIR", DEFAULT_DATA_DIR)


def get_species_db_dir() -> str:
    """Directory for species taxonomy DB files."""
    return os.getenv("SPECIES_DB_DIR", DEFAULT_SPECIES_DB_DIR)
