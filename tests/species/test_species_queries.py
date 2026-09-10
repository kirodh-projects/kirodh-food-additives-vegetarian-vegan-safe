"""Tests for species queries across sharded SQLite files."""

import sqlite3

import pytest

from src.species import queries as species_queries
from src.species.connection import get_species_connection
from src.species.schema import create_species_tables


@pytest.fixture
def species_db_dir(tmp_path, monkeypatch):
    """Create two small species DB shards and point the module at them."""
    monkeypatch.setenv("SPECIES_DB_DIR", str(tmp_path))

    rows_file_1 = [
        (1, "Panthera leo", "Panthera leo", "(Linnaeus, 1758)",
         "Animalia", "Chordata", "Mammalia", "Carnivora", "Felidae", "Panthera",
         "leo", "", "species", "accepted", None, "GBIF"),
        (2, "Homo sapiens", "Homo sapiens", "Linnaeus, 1758",
         "Animalia", "Chordata", "Mammalia", "Primates", "Hominidae", "Homo",
         "sapiens", "", "species", "accepted", None, "GBIF"),
    ]
    rows_file_2 = [
        (3, "Quercus robur", "Quercus robur", "L.",
         "Plantae", "Tracheophyta", "Magnoliopsida", "Fagales", "Fagaceae", "Quercus",
         "robur", "", "species", "accepted", None, "GBIF"),
    ]

    for i, rows in enumerate([rows_file_1, rows_file_2], start=1):
        path = tmp_path / f"species_{i:03d}.db"
        conn = sqlite3.connect(str(path))
        create_species_tables(conn)
        conn.executemany(
            """INSERT INTO species (
                taxon_id, scientific_name, canonical_name, authorship,
                kingdom, phylum, class_name, order_name, family, genus,
                specific_epithet, infraspecific_epithet, taxon_rank,
                taxonomic_status, accepted_taxon_id, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            rows,
        )
        conn.commit()
        conn.close()

    return str(tmp_path)


class TestSearchSpecies:
    def test_search_by_genus(self, species_db_dir):
        results = species_queries.search_species("Panthera", db_dir=species_db_dir)
        assert len(results) == 1
        assert results[0]["canonical_name"] == "Panthera leo"

    def test_search_across_shards(self, species_db_dir):
        results = species_queries.search_species("a", db_dir=species_db_dir, limit=10)
        assert len(results) == 3

    def test_search_no_db(self, tmp_path, monkeypatch):
        empty = tmp_path / "empty"
        empty.mkdir()
        monkeypatch.setenv("SPECIES_DB_DIR", str(empty))
        assert species_queries.search_species("Panthera", db_dir=str(empty)) == []


class TestBrowseSpecies:
    def test_filter_by_kingdom(self, species_db_dir):
        results = species_queries.browse_species(
            db_dir=species_db_dir, filters={"kingdom": ["Plantae"]}
        )
        assert len(results) == 1
        assert results[0]["genus"] == "Quercus"

    def test_pagination_across_shards(self, species_db_dir):
        page1 = species_queries.browse_species(db_dir=species_db_dir, limit=2, offset=0)
        page2 = species_queries.browse_species(db_dir=species_db_dir, limit=2, offset=2)
        assert len(page1) == 2
        assert len(page2) == 1

    def test_total_count(self, species_db_dir):
        assert species_queries.get_species_total_count(db_dir=species_db_dir) == 3
        assert species_queries.get_species_total_count(
            db_dir=species_db_dir, filters={"kingdom": ["Animalia"]}
        ) == 2


class TestSpeciesConnection:
    def test_connection_context_manager(self, species_db_dir):
        db_file = f"{species_db_dir}/species_001.db"
        with get_species_connection(db_file) as conn:
            count = conn.execute("SELECT COUNT(*) FROM species").fetchone()[0]
        assert count == 2
