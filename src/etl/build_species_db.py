"""Download and build the species taxonomy database from GBIF Backbone Taxonomy.

Downloads the GBIF Backbone (~490MB compressed), filters to species and
subspecies rank records, resolves hierarchy IDs to names, and inserts
into SQLite databases split at ~45MB each.

Two-pass processing:
  Pass 1: Build an in-memory lookup of taxon_id -> name for higher taxa
  Pass 2: Insert species/subspecies with resolved kingdom/phylum/class/order/family/genus names

Usage:
    python -m src.etl.build_species_db [--force] [--db-dir DIR]
"""

import argparse
import csv
import gzip
import logging
import os
from pathlib import Path

import requests

from src.db.species_connection import (
    ensure_species_db,
    get_db_file_size_mb,
    get_next_species_db_path,
    get_species_connection,
    get_species_db_dir,
    list_species_db_files,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

GBIF_BACKBONE_URL = "https://hosted-datasets.gbif.org/datasets/backbone/current/simple.txt.gz"
DOWNLOAD_FILENAME = "gbif_backbone_simple.txt.gz"
MAX_DB_SIZE_MB = 45
BATCH_SIZE = 10_000
SPECIES_RANKS = {"SPECIES", "SUBSPECIES", "VARIETY", "FORM"}
HIGHER_RANKS = {"KINGDOM", "PHYLUM", "CLASS", "ORDER", "FAMILY", "GENUS",
                "SUBKINGDOM", "SUBPHYLUM", "SUBCLASS", "SUBORDER", "SUBFAMILY",
                "SUPERFAMILY", "INFRAORDER", "INFRACLASS", "SUPERORDER", "SUPERCLASS",
                "TRIBE", "SUBTRIBE", "SECTION", "SUBSECTION"}

# Actual GBIF backbone column layout (30 columns, no header)
COL_TAXON_ID = 0
COL_PARENT_ID = 1
COL_ACCEPTED_ID = 2  # \N if accepted
COL_IS_SYNONYM = 3   # t/f
COL_STATUS = 4        # ACCEPTED, SYNONYM, DOUBTFUL, etc.
COL_RANK = 5          # KINGDOM, SPECIES, etc.
# [6]: issues, [7]: datasetKey, [8]: constituentKey, [9]: sourceID
COL_KINGDOM_ID = 10
COL_PHYLUM_ID = 11
COL_CLASS_ID = 12
COL_ORDER_ID = 13
COL_FAMILY_ID = 14
COL_GENUS_ID = 15
# [16]: speciesKey, [17]: nameKey
COL_SCIENTIFIC_NAME = 18
COL_CANONICAL_NAME = 19
COL_GENERIC_NAME = 20
COL_SPECIFIC_EPITHET = 21
COL_INFRASPECIFIC_EPITHET = 22
# [23]: ?
COL_AUTHORSHIP = 24
# [25]: year, [26]: basionymAuthorship, [27]: ?, [28]: publishedIn, [29]: issues
MIN_COLS = 20


def download_backbone(download_dir: str, force: bool = False) -> str:
    """Download the GBIF backbone. Returns path to file."""
    dest = Path(download_dir) / DOWNLOAD_FILENAME
    if dest.exists() and not force:
        logger.info("Backbone file already exists: %s (%.0f MB)", dest, dest.stat().st_size / 1e6)
        return str(dest)

    logger.info("Downloading GBIF Backbone Taxonomy from %s ...", GBIF_BACKBONE_URL)
    Path(download_dir).mkdir(parents=True, exist_ok=True)

    with requests.get(GBIF_BACKBONE_URL, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        downloaded = 0
        with open(str(dest), "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    print(f"\r  {downloaded/1e6:.0f}/{total/1e6:.0f} MB ({downloaded/total*100:.0f}%)", end="", flush=True)
        print()

    logger.info("Download complete: %s", dest)
    return str(dest)


def build_species_database(
    db_dir: str | None = None,
    download_dir: str | None = None,
    force_rebuild: bool = False,
) -> int:
    """Build species databases from the GBIF backbone."""
    db_dir = db_dir or get_species_db_dir()
    download_dir = download_dir or db_dir

    existing = list_species_db_files(db_dir)
    if existing and not force_rebuild:
        total = sum(_count_in_file(f) for f in existing)
        if total > 0:
            logger.info("Species databases already exist with %d records. Use --force to rebuild.", total)
            return 0

    if force_rebuild:
        for f in existing:
            os.remove(f)

    gz_path = download_backbone(download_dir, force=force_rebuild)

    # --- Pass 1: Build hierarchy lookup ---
    logger.info("Pass 1: Building hierarchy name lookup...")
    id_to_name = _build_hierarchy_lookup(gz_path)
    logger.info("  Loaded %d higher taxa names", len(id_to_name))

    # --- Pass 2: Insert species records ---
    logger.info("Pass 2: Inserting species records...")
    total = _insert_species(gz_path, db_dir, id_to_name)
    logger.info("Done. %d species records inserted.", total)

    # --- Pass 3: Populate trait scores ---
    logger.info("Pass 3: Populating trait scores (mobility, warm-blood, size)...")
    from src.etl.species_traits import migrate_species_traits
    migrate_species_traits(db_dir)

    return total


def _count_in_file(path: str) -> int:
    try:
        with get_species_connection(path) as conn:
            return conn.execute("SELECT COUNT(*) FROM species").fetchone()[0]
    except Exception:
        return 0


def _build_hierarchy_lookup(gz_path: str) -> dict[int, str]:
    """Pass 1: Read all higher-taxa rows and map taxon_id -> canonical_name."""
    lookup: dict[int, str] = {}

    with gzip.open(gz_path, "rt", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        for row in reader:
            if len(row) < MIN_COLS:
                continue

            rank = row[COL_RANK].strip().upper()
            if rank not in HIGHER_RANKS:
                continue

            try:
                tid = int(row[COL_TAXON_ID].strip())
            except (ValueError, IndexError):
                continue

            name = row[COL_CANONICAL_NAME].strip() if row[COL_CANONICAL_NAME].strip() != "\\N" else ""
            if not name:
                name = row[COL_SCIENTIFIC_NAME].strip()
            if name and name != "\\N":
                lookup[tid] = name

    return lookup


def _resolve_id(lookup: dict[int, str], raw_id: str) -> str:
    """Resolve a hierarchy ID column to a name."""
    raw = raw_id.strip()
    if not raw or raw == "\\N":
        return ""
    try:
        return lookup.get(int(raw), "")
    except ValueError:
        return ""


def _insert_species(
    gz_path: str,
    db_dir: str,
    id_to_name: dict[int, str],
) -> int:
    """Pass 2: Stream species records and insert into split DB files."""
    current_db_path = get_next_species_db_path(db_dir)
    ensure_species_db(current_db_path)
    conn = _open_db(current_db_path)

    batch: list[tuple] = []
    total_inserted = 0
    line_num = 0

    with gzip.open(gz_path, "rt", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)

        for row in reader:
            line_num += 1
            if len(row) < MIN_COLS:
                continue

            rank = row[COL_RANK].strip().upper()
            if rank not in SPECIES_RANKS:
                continue

            try:
                taxon_id = int(row[COL_TAXON_ID].strip())
            except ValueError:
                taxon_id = None

            accepted_raw = row[COL_ACCEPTED_ID].strip() if len(row) > COL_ACCEPTED_ID else "\\N"
            try:
                accepted_id = int(accepted_raw) if accepted_raw != "\\N" else None
            except ValueError:
                accepted_id = None

            sci_name = _clean(row, COL_SCIENTIFIC_NAME)
            canonical = _clean(row, COL_CANONICAL_NAME)
            authorship = _clean(row, COL_AUTHORSHIP) if len(row) > COL_AUTHORSHIP else ""

            kingdom = _resolve_id(id_to_name, row[COL_KINGDOM_ID])
            phylum = _resolve_id(id_to_name, row[COL_PHYLUM_ID])
            class_name = _resolve_id(id_to_name, row[COL_CLASS_ID])
            order_name = _resolve_id(id_to_name, row[COL_ORDER_ID])
            family = _resolve_id(id_to_name, row[COL_FAMILY_ID])
            genus = _resolve_id(id_to_name, row[COL_GENUS_ID])

            # Fallback: use generic name column for genus if lookup failed
            if not genus:
                genus = _clean(row, COL_GENERIC_NAME)

            status = _clean(row, COL_STATUS)
            specific = _clean(row, COL_SPECIFIC_EPITHET)
            infraspecific = _clean(row, COL_INFRASPECIFIC_EPITHET) if len(row) > COL_INFRASPECIFIC_EPITHET else ""

            record = (
                taxon_id, sci_name, canonical, authorship,
                kingdom, phylum, class_name, order_name, family, genus,
                specific, infraspecific, rank.lower(), status.lower(),
                accepted_id, "GBIF",
            )
            batch.append(record)

            if len(batch) >= BATCH_SIZE:
                _insert_batch(conn, batch)
                total_inserted += len(batch)
                batch.clear()

                conn.commit()
                size_mb = get_db_file_size_mb(current_db_path)
                if size_mb >= MAX_DB_SIZE_MB:
                    _finalize_db(conn, current_db_path)
                    current_db_path = get_next_species_db_path(db_dir)
                    ensure_species_db(current_db_path)
                    conn = _open_db(current_db_path)
                    logger.info("  New DB file: %s (total so far: %d)", current_db_path, total_inserted)

                if total_inserted % 500_000 == 0:
                    logger.info("  Inserted %d records...", total_inserted)

    if batch:
        _insert_batch(conn, batch)
        total_inserted += len(batch)

    _finalize_db(conn, current_db_path)
    return total_inserted


def _clean(row: list[str], idx: int) -> str:
    """Get a cleaned string value from a row, treating \\N as empty."""
    try:
        val = row[idx].strip()
        return "" if val == "\\N" else val
    except IndexError:
        return ""


INSERT_SQL = """
INSERT INTO species (
    taxon_id, scientific_name, canonical_name, authorship,
    kingdom, phylum, class_name, order_name, family, genus,
    specific_epithet, infraspecific_epithet, taxon_rank,
    taxonomic_status, accepted_taxon_id, source
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


def _open_db(path: str):
    import sqlite3
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=OFF")
    conn.execute("PRAGMA cache_size=-64000")
    conn.execute("PRAGMA temp_store=MEMORY")
    return conn


def _insert_batch(conn, batch: list[tuple]) -> None:
    conn.executemany(INSERT_SQL, batch)


def _finalize_db(conn, path: str) -> None:
    conn.commit()
    conn.close()
    logger.info("  Finalized %s: %.1f MB", path, get_db_file_size_mb(path))


def main():
    parser = argparse.ArgumentParser(description="Build species taxonomy database from GBIF")
    parser.add_argument("--force", action="store_true", help="Force re-download and rebuild")
    parser.add_argument("--db-dir", type=str, default=None, help="Directory for DB files")
    args = parser.parse_args()

    count = build_species_database(db_dir=args.db_dir, force_rebuild=args.force)
    print(f"Done. {count} species records processed.")


if __name__ == "__main__":
    main()
