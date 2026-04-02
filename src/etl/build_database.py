"""Main ETL pipeline: merge all data sources into a single SQLite database.

Usage:
    python -m src.etl.build_database [--force] [--db-path PATH] [--data-dir DIR]
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

from src.db.connection import ensure_database, get_connection, get_db_path
from src.etl.classifiers import classify_all
from src.etl.e_ins_mapper import build_e_to_ins_map
from src.etl.normalizers import (
    deduplicate_records,
    normalize_category,
    normalize_e_code,
    normalize_halal_status,
)
from src.etl.parsers import (
    parse_additives_csv,
    parse_classification_csv,
    parse_e_assets_csvs,
    parse_e_index_csv,
    parse_ins_index_csv,
    parse_merged_csv,
)
from src.etl.web_scraper import scrape_supplementary_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

DEFAULT_DATA_DIR = "./additive_databases"


def _get_data_dir() -> str:
    import os
    return os.getenv("DATA_DIR", DEFAULT_DATA_DIR)


def has_data(db_path: str) -> bool:
    """Check if the database already has additive data."""
    try:
        with get_connection(db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM additives")
            count = cursor.fetchone()[0]
            return count > 0
    except Exception:
        return False


def build_database(
    db_path: str | None = None,
    data_dir: str | None = None,
    force_rebuild: bool = False,
) -> int:
    """Main ETL entry point. Returns number of records inserted.

    Idempotent: skips if data already exists unless force_rebuild=True.
    """
    db_path = db_path or get_db_path()
    data_dir = data_dir or _get_data_dir()
    data_root = Path(data_dir)

    logger.info("Database path: %s", db_path)
    logger.info("Data directory: %s", data_root)

    # Ensure schema exists
    ensure_database(db_path)

    # Check for existing data
    if not force_rebuild and has_data(db_path):
        logger.info("Database already contains data. Use --force to rebuild.")
        return 0

    if force_rebuild:
        with get_connection(db_path) as conn:
            conn.execute("DELETE FROM source_records")
            conn.execute("DELETE FROM additives")
            conn.commit()
        logger.info("Cleared existing data for rebuild.")

    # --- Step 1: Parse all sources ---
    logger.info("Parsing data sources...")

    primary_records = []
    additives_csv_path = data_root / "additives.csv"
    if additives_csv_path.exists():
        primary_records = parse_additives_csv(additives_csv_path)
        logger.info("  additives.csv: %d records", len(primary_records))

    # Also try the E-Number-Database CSV as fallback
    alt_csv_path = data_root / "E-Number-Database" / "CSV" / "additives.csv"
    if not primary_records and alt_csv_path.exists():
        primary_records = parse_additives_csv(alt_csv_path)
        logger.info("  E-Number-Database/CSV/additives.csv: %d records", len(primary_records))

    e_index_records = []
    e_index_path = data_root / "food-additive" / "e" / "index.csv"
    if e_index_path.exists():
        e_index_records = parse_e_index_csv(e_index_path)
        logger.info("  e/index.csv: %d records", len(e_index_records))

    ins_index_records = []
    ins_index_path = data_root / "food-additive" / "ins" / "index.csv"
    if ins_index_path.exists():
        ins_index_records = parse_ins_index_csv(ins_index_path)
        logger.info("  ins/index.csv: %d records", len(ins_index_records))

    assets_records = []
    assets_dir = data_root / "food-additive" / "e" / "assets"
    if assets_dir.exists():
        assets_records = parse_e_assets_csvs(assets_dir)
        logger.info("  e/assets/*.csv: %d records", len(assets_records))

    merged_records = []
    merged_path = data_root / "final_INS_and_E_merged.csv"
    if merged_path.exists():
        merged_records = parse_merged_csv(merged_path)
        logger.info("  final_INS_and_E_merged.csv: %d records", len(merged_records))

    classification_map = {}
    classification_path = data_root / "food-additive" / "e" / "assets" / "classification.csv"
    if classification_path.exists():
        classification_map = parse_classification_csv(classification_path)
        logger.info("  classification.csv: %d range entries", len(classification_map))

    # --- Step 2: Build E-to-INS mapping ---
    logger.info("Building E-to-INS mapping...")
    e_to_ins = build_e_to_ins_map(e_index_records, ins_index_records, merged_records)
    logger.info("  Mapped %d E-numbers to INS codes", len(e_to_ins))

    # --- Step 3: Scrape supplementary web data ---
    logger.info("Loading supplementary web data...")
    web_data = scrape_supplementary_data(cache_dir=data_root)
    logger.info("  Supplementary data: %d entries", len(web_data))

    # --- Step 4: Build enrichment indexes ---
    e_index_by_code: dict[str, dict] = {}
    for rec in e_index_records:
        e_num = rec.get("e_number", "")
        if e_num:
            e_index_by_code[e_num] = rec

    assets_by_code: dict[str, dict] = {}
    for rec in assets_records:
        e_num = rec.get("e_number", "")
        if e_num:
            assets_by_code[e_num] = rec

    # --- Step 5: Merge and enrich records ---
    logger.info("Merging and enriching records...")
    merged_additives = _merge_all_sources(
        primary_records=primary_records,
        e_index_by_code=e_index_by_code,
        assets_by_code=assets_by_code,
        e_to_ins=e_to_ins,
        classification_map=classification_map,
        web_data=web_data,
    )

    # Add E-numbers from secondary sources that aren't in primary
    _add_secondary_only(merged_additives, e_index_records, e_to_ins, classification_map, web_data)

    # Deduplicate
    final_records = deduplicate_records(list(merged_additives.values()))
    logger.info("  Final unique records: %d", len(final_records))

    # --- Step 6: Insert into database ---
    logger.info("Inserting into database...")
    inserted = _insert_records(db_path, final_records)
    logger.info("Inserted %d records into database.", inserted)

    return inserted


def _merge_all_sources(
    primary_records: list[dict],
    e_index_by_code: dict[str, dict],
    assets_by_code: dict[str, dict],
    e_to_ins: dict[str, str],
    classification_map: dict[tuple[int, int], dict[str, str]],
    web_data: dict[str, dict[str, str]],
) -> dict[str, dict]:
    """Merge primary records with enrichment from secondary sources."""
    merged: dict[str, dict] = {}

    for rec in primary_records:
        e_num = rec["e_number"]
        description = rec.get("description", "") or ""
        common_name = rec.get("common_name", "") or ""

        # Enrich with e/index.csv data
        e_idx = e_index_by_code.get(e_num, {})
        alt_name = e_idx.get("common_name", "")
        alternative_names = alt_name if alt_name and alt_name != common_name else ""

        # Enrich with assets data
        asset = assets_by_code.get(e_num, {})
        approval_eu = asset.get("approval_eu", e_idx.get("approval_eu", 0))
        approval_us = asset.get("approval_us", 0)
        approval_codex = e_idx.get("approval_codex", 0)
        is_banned = asset.get("is_banned_anywhere", 0)

        # Get subcategory from classification map
        subcategory = _get_subcategory(e_num, classification_map)

        # Run classifiers
        classifications = classify_all(e_num, description, web_data)

        # Halal from primary source
        halal = normalize_halal_status(rec.get("halal_status_raw", ""))

        merged[e_num] = {
            "e_number": e_num,
            "ins_number": e_to_ins.get(e_num),
            "chemical_name": _extract_chemical_name(common_name),
            "common_name": common_name,
            "alternative_names": alternative_names,
            "category": normalize_category(rec.get("category_raw", "")),
            "subcategory": subcategory,
            "description": description,
            "halal_status": halal,
            "vegan_status": classifications["vegan_status"],
            "vegetarian_status": classifications["vegetarian_status"],
            "safety_level": classifications["safety_level"],
            "origin": classifications["origin"],
            "adi": classifications["adi"],
            "approval_eu": approval_eu,
            "approval_us": approval_us,
            "approval_codex": approval_codex,
            "is_banned_anywhere": is_banned,
            "source_files": ",".join(
                filter(None, [
                    rec.get("source"),
                    e_idx.get("source"),
                    asset.get("source"),
                ])
            ),
        }

    return merged


def _add_secondary_only(
    merged: dict[str, dict],
    e_index_records: list[dict],
    e_to_ins: dict[str, str],
    classification_map: dict,
    web_data: dict,
) -> None:
    """Add E-numbers found only in secondary sources."""
    for rec in e_index_records:
        e_num = rec.get("e_number", "")
        if not e_num or e_num in merged:
            continue

        common_name = rec.get("common_name", "")
        subcategory = _get_subcategory(e_num, classification_map)
        classifications = classify_all(e_num, "", web_data)

        merged[e_num] = {
            "e_number": e_num,
            "ins_number": e_to_ins.get(e_num),
            "chemical_name": _extract_chemical_name(common_name),
            "common_name": common_name,
            "alternative_names": "",
            "category": normalize_category(rec.get("category_raw", "")),
            "subcategory": subcategory,
            "description": "",
            "halal_status": "Unknown",
            "vegan_status": classifications["vegan_status"],
            "vegetarian_status": classifications["vegetarian_status"],
            "safety_level": classifications["safety_level"],
            "origin": classifications["origin"],
            "adi": classifications["adi"],
            "approval_eu": rec.get("approval_eu", 0),
            "approval_us": 0,
            "approval_codex": rec.get("approval_codex", 0),
            "is_banned_anywhere": 0,
            "source_files": rec.get("source", ""),
        }


def _get_subcategory(
    e_number: str,
    classification_map: dict[tuple[int, int], dict[str, str]],
) -> str:
    """Look up subcategory from classification range map."""
    match = re.match(r"E(\d+)", e_number)
    if not match:
        return ""

    num = int(match.group(1))
    for (start, end), info in classification_map.items():
        if start <= num <= end:
            return info.get("subcategory", "")

    return ""


def _extract_chemical_name(common_name: str) -> str:
    """Extract chemical/scientific name from common name if present.

    Looks for parenthetical names like 'Curcumin (from turmeric)'.
    """
    if not common_name:
        return ""

    # If name contains '/' it often has chemical/common split
    if " / " in common_name:
        return common_name.split(" / ")[0].strip()

    return ""


def _insert_records(db_path: str, records: list[dict]) -> int:
    """Insert records into the database. Skips existing e_numbers."""
    insert_sql = """
    INSERT OR IGNORE INTO additives (
        e_number, ins_number, chemical_name, common_name,
        alternative_names, category, subcategory, description,
        halal_status, vegan_status, vegetarian_status, safety_level,
        origin, adi, approval_eu, approval_us, approval_codex,
        is_banned_anywhere, source_files
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    )
    """

    source_sql = """
    INSERT INTO source_records (additive_id, source_file, raw_code, raw_data)
    VALUES (?, ?, ?, ?)
    """

    inserted = 0
    with get_connection(db_path) as conn:
        for rec in records:
            try:
                conn.execute(insert_sql, (
                    rec["e_number"],
                    rec.get("ins_number"),
                    rec.get("chemical_name", ""),
                    rec["common_name"],
                    rec.get("alternative_names", ""),
                    rec.get("category", "Unknown"),
                    rec.get("subcategory", ""),
                    rec.get("description", ""),
                    rec.get("halal_status", "Unknown"),
                    rec.get("vegan_status", "Unknown"),
                    rec.get("vegetarian_status", "Unknown"),
                    rec.get("safety_level", "Unknown"),
                    rec.get("origin", "Unknown"),
                    rec.get("adi"),
                    rec.get("approval_eu", 0),
                    rec.get("approval_us", 0),
                    rec.get("approval_codex", 0),
                    rec.get("is_banned_anywhere", 0),
                    rec.get("source_files", ""),
                ))

                # Get the inserted row ID for source records
                row_id = conn.execute(
                    "SELECT id FROM additives WHERE e_number = ?",
                    (rec["e_number"],),
                ).fetchone()

                if row_id:
                    conn.execute(source_sql, (
                        row_id[0],
                        rec.get("source_files", ""),
                        rec["e_number"],
                        json.dumps({
                            k: v for k, v in rec.items()
                            if k != "description"  # Skip large text in audit
                        }, default=str),
                    ))

                inserted += 1
            except Exception as e:
                logger.warning("Failed to insert %s: %s", rec.get("e_number"), e)

        conn.commit()

    return inserted


def main():
    parser = argparse.ArgumentParser(description="Build the food additives database")
    parser.add_argument(
        "--force", action="store_true",
        help="Force rebuild even if data already exists",
    )
    parser.add_argument(
        "--db-path", type=str, default=None,
        help="Path to the SQLite database file",
    )
    parser.add_argument(
        "--data-dir", type=str, default=None,
        help="Path to the additive_databases directory",
    )
    args = parser.parse_args()

    count = build_database(
        db_path=args.db_path,
        data_dir=args.data_dir,
        force_rebuild=args.force,
    )
    print(f"Done. {count} records processed.")


if __name__ == "__main__":
    main()
