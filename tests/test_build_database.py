"""Integration tests for the full ETL pipeline."""

import os
import tempfile

import pytest

from src.db.connection import get_connection
from src.etl.build_database import build_database, has_data


@pytest.fixture
def temp_db():
    """Create a temporary database file."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    os.unlink(path)


class TestBuildDatabase:
    def test_full_build_creates_database(self, temp_db):
        data_dir = os.path.join(
            os.path.dirname(__file__), "..", "additive_databases"
        )
        if not os.path.exists(data_dir):
            pytest.skip("additive_databases directory not found")

        count = build_database(db_path=temp_db, data_dir=data_dir)
        assert count > 0

        with get_connection(temp_db) as conn:
            total = conn.execute("SELECT COUNT(*) FROM additives").fetchone()[0]
            assert total > 100  # Should have at least 100 records

    def test_build_is_idempotent(self, temp_db):
        data_dir = os.path.join(
            os.path.dirname(__file__), "..", "additive_databases"
        )
        if not os.path.exists(data_dir):
            pytest.skip("additive_databases directory not found")

        count1 = build_database(db_path=temp_db, data_dir=data_dir)
        assert count1 > 0

        # Second run should skip
        count2 = build_database(db_path=temp_db, data_dir=data_dir)
        assert count2 == 0

    def test_force_rebuild(self, temp_db):
        data_dir = os.path.join(
            os.path.dirname(__file__), "..", "additive_databases"
        )
        if not os.path.exists(data_dir):
            pytest.skip("additive_databases directory not found")

        count1 = build_database(db_path=temp_db, data_dir=data_dir)
        count2 = build_database(db_path=temp_db, data_dir=data_dir, force_rebuild=True)
        assert count2 > 0

    def test_has_data_empty(self, temp_db):
        from src.db.connection import ensure_database
        ensure_database(temp_db)
        assert has_data(temp_db) is False

    def test_has_data_populated(self, temp_db):
        data_dir = os.path.join(
            os.path.dirname(__file__), "..", "additive_databases"
        )
        if not os.path.exists(data_dir):
            pytest.skip("additive_databases directory not found")

        build_database(db_path=temp_db, data_dir=data_dir)
        assert has_data(temp_db) is True
