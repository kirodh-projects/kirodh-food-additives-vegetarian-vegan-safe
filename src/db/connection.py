"""SQLite connection management."""

import os
import sqlite3
from contextlib import contextmanager

from dotenv import load_dotenv

from src.db.schema import create_tables

load_dotenv()

DEFAULT_DB_PATH = "./databases/food_additives.db"


def get_db_path() -> str:
    """Get database file path from environment."""
    return os.getenv("DB_PATH", DEFAULT_DB_PATH)


@contextmanager
def get_connection(db_path: str | None = None):
    """Context manager for SQLite connections.

    Enables WAL mode and foreign keys for performance and integrity.
    """
    path = db_path or get_db_path()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
    finally:
        conn.close()


def ensure_database(db_path: str | None = None) -> str:
    """Ensure the database exists with the correct schema. Returns the path."""
    path = db_path or get_db_path()
    with get_connection(path) as conn:
        create_tables(conn)
    return path
