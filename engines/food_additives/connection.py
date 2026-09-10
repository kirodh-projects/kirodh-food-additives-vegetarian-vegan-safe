"""SQLite connection management for the food additives database."""

import sqlite3
from contextlib import contextmanager

from .schema import create_tables
from .config import DEFAULT_DB_PATH, get_db_path

__all__ = ["DEFAULT_DB_PATH", "get_db_path", "get_connection", "ensure_database"]


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
