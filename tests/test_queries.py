"""Tests for database query functions."""

import sqlite3
from unittest.mock import patch

import pytest

from src.db.queries import (
    check_duplicates,
    get_all_additives,
    get_analytics_summary,
    get_total_count,
    search_by_code,
    search_by_name,
)


def _db_path_from_conn(conn):
    """Helper: mock get_connection to use the test connection."""
    return conn


class TestSearchByCode:
    def test_search_e_number(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            result = search_by_code(":memory:", "E100")
            assert result is not None
            assert result["e_number"] == "E100"

    def test_search_without_prefix(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            result = search_by_code(":memory:", "100")
            assert result is not None
            assert result["e_number"] == "E100"

    def test_search_case_insensitive(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            result = search_by_code(":memory:", "e100")
            assert result is not None

    def test_search_not_found(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            result = search_by_code(":memory:", "E9999")
            assert result is None

    def test_search_by_ins_number(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            result = search_by_code(":memory:", "INS 100")
            assert result is not None
            assert result["e_number"] == "E100"


class TestSearchByName:
    def test_search_partial_name(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            results = search_by_name(":memory:", "curcumin")
            assert len(results) >= 1
            assert results[0]["common_name"] == "Curcumin / Turmeric"


class TestGetAnalyticsSummary:
    def test_summary_counts(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            summary = get_analytics_summary(":memory:")
            assert summary["total"] == 10
            assert "vegan_status" in summary
            assert "safety_level" in summary
            assert isinstance(summary["vegan_status"], dict)


class TestGetAllAdditives:
    def test_no_filters(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            results = get_all_additives(":memory:")
            assert len(results) == 10

    def test_filter_by_vegan(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            results = get_all_additives(
                ":memory:", filters={"vegan_status": ["Yes"]}
            )
            assert all(r["vegan_status"] == "Yes" for r in results)

    def test_pagination(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            page1 = get_all_additives(":memory:", limit=5, offset=0)
            page2 = get_all_additives(":memory:", limit=5, offset=5)
            assert len(page1) == 5
            assert len(page2) == 5
            assert page1[0]["e_number"] != page2[0]["e_number"]


class TestGetTotalCount:
    def test_total_count(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            count = get_total_count(":memory:")
            assert count == 10

    def test_filtered_count(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            count = get_total_count(":memory:", filters={"safety_level": ["Banned"]})
            assert count == 1


class TestCheckDuplicates:
    def test_no_duplicates(self, populated_db):
        with patch("src.db.queries.get_connection") as mock_conn:
            mock_conn.return_value.__enter__ = lambda _: populated_db
            mock_conn.return_value.__exit__ = lambda *_: None

            results = check_duplicates(":memory:")
            assert len(results["exact_e_number_dupes"]) == 0
