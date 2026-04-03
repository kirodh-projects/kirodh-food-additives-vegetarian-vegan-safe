"""Connection management for the multi-file species database."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv

from src.db.species_schema import create_species_tables

load_dotenv()

DEFAULT_SPECIES_DB_DIR = "./databases"
SPECIES_DB_PREFIX = "species_"
STATS_CACHE_FILE = "species_stats_cache.json"


def get_species_db_dir() -> str:
    return os.getenv("SPECIES_DB_DIR", DEFAULT_SPECIES_DB_DIR)


def list_species_db_files(db_dir: str | None = None) -> list[str]:
    """List all species DB files in order."""
    d = Path(db_dir or get_species_db_dir())
    if not d.exists():
        return []
    files = sorted(d.glob(f"{SPECIES_DB_PREFIX}*.db"))
    return [str(f) for f in files]


def get_next_species_db_path(db_dir: str | None = None) -> str:
    """Get the path for the next species DB file to create."""
    d = Path(db_dir or get_species_db_dir())
    d.mkdir(parents=True, exist_ok=True)
    existing = list_species_db_files(str(d))
    next_num = len(existing) + 1
    return str(d / f"{SPECIES_DB_PREFIX}{next_num:03d}.db")


def get_db_file_size_mb(path: str) -> float:
    """Get file size in MB."""
    try:
        return os.path.getsize(path) / (1024 * 1024)
    except OSError:
        return 0.0


@contextmanager
def get_species_connection(db_path: str):
    """Context manager for a single species DB connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    try:
        yield conn
    finally:
        conn.close()


def ensure_species_db(db_path: str) -> str:
    """Ensure a species DB file exists with the correct schema."""
    with get_species_connection(db_path) as conn:
        create_species_tables(conn)
    return db_path


def get_stats_cache_path(db_dir: str | None = None) -> str:
    """Path to the precomputed stats cache JSON file."""
    return str(Path(db_dir or get_species_db_dir()) / STATS_CACHE_FILE)
