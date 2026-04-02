"""Parsers for each raw data source. Each returns a list of uniform dicts."""

import csv
import json
import sqlite3
from pathlib import Path

import pandas as pd

from src.etl.normalizers import normalize_e_code


def parse_additives_csv(filepath: str | Path) -> list[dict]:
    """Parse additive_databases/additives.csv (primary source, 562 unique E-codes).

    Returns list of dicts with keys matching the target schema.
    """
    df = pd.read_csv(filepath, encoding="utf-8")
    df.columns = df.columns.str.strip().str.lower()

    records = []
    for _, row in df.iterrows():
        e_code = str(row.get("e_code", "")).strip()
        if not e_code:
            continue

        records.append({
            "e_number": normalize_e_code(e_code),
            "common_name": str(row.get("title", "")).strip(),
            "description": str(row.get("info", "")).strip(),
            "category_raw": str(row.get("e_type", "")).strip(),
            "halal_status_raw": str(row.get("halal_status", "")).strip(),
            "source": "additives.csv",
        })

    return records


def parse_e_index_csv(filepath: str | Path) -> list[dict]:
    """Parse food-additive/e/index.csv (511 E-numbers with names and type)."""
    df = pd.read_csv(filepath, encoding="utf-8")
    df.columns = df.columns.str.strip().str.lower()

    records = []
    for _, row in df.iterrows():
        code = str(row.get("code", "")).strip()
        if not code:
            continue

        status = str(row.get("status", "")).strip().lower()
        records.append({
            "e_number": normalize_e_code(code),
            "common_name": str(row.get("names", "")).strip(),
            "category_raw": str(row.get("type", "")).strip(),
            "approval_eu": 1 if "e" in status else 0,
            "approval_codex": 1 if "u" in status else 0,
            "source": "e/index.csv",
        })

    return records


def parse_ins_index_csv(filepath: str | Path) -> list[dict]:
    """Parse food-additive/ins/index.csv (437 INS numbers)."""
    df = pd.read_csv(filepath, encoding="utf-8")
    df.columns = df.columns.str.strip().str.lower()

    records = []
    for _, row in df.iterrows():
        code = str(row.get("code", "")).strip()
        if not code:
            continue

        status = str(row.get("status", "")).strip().lower()
        records.append({
            "ins_code": code,
            "common_name": str(row.get("names", "")).strip(),
            "category_raw": str(row.get("type", "")).strip(),
            "approval_eu": 1 if "e" in status else 0,
            "approval_codex": 1 if "a" in status or "u" in status else 0,
            "source": "ins/index.csv",
        })

    return records


def parse_e_assets_csvs(assets_dir: str | Path) -> list[dict]:
    """Parse food-additive/e/assets/e100.csv through e1000.csv.

    These contain approval status text useful for EU/US/banned flags.
    """
    assets_path = Path(assets_dir)
    records = []

    for csv_file in sorted(assets_path.glob("e*.csv")):
        if csv_file.name == "classification.csv":
            continue

        try:
            df = pd.read_csv(csv_file, encoding="utf-8")
        except Exception:
            continue

        df.columns = df.columns.str.strip().str.lower()

        # Column names vary: "code", "name(s)", "colour"/"purpose", "status"
        code_col = "code" if "code" in df.columns else None
        name_col = next((c for c in df.columns if "name" in c), None)
        status_col = "status" if "status" in df.columns else None
        purpose_col = next(
            (c for c in df.columns if c in ("purpose", "colour", "color")), None
        )

        if not code_col:
            continue

        for _, row in df.iterrows():
            code = str(row.get(code_col, "")).strip()
            if not code:
                continue

            status_text = str(row.get(status_col, "")).strip() if status_col else ""
            status_lower = status_text.lower()

            records.append({
                "e_number": normalize_e_code(code),
                "common_name": str(row.get(name_col, "")).strip() if name_col else "",
                "category_raw": str(row.get(purpose_col, "")).strip() if purpose_col else "",
                "status_text": status_text,
                "approval_eu": 1 if "approved in the eu" in status_lower else 0,
                "approval_us": 1 if "approved in the us" in status_lower else 0,
                "is_banned_anywhere": 1 if "banned" in status_lower else 0,
                "source": f"e/assets/{csv_file.name}",
            })

    return records


def parse_classification_csv(filepath: str | Path) -> dict[tuple[int, int], dict[str, str]]:
    """Parse classification.csv to get range -> (category, subcategory) mapping.

    Returns dict keyed by (range_start, range_end) -> {"category": ..., "subcategory": ...}
    """
    mapping = {}

    with open(filepath, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header

        for row in reader:
            if len(row) < 2:
                continue

            main_desc = row[0].strip()
            subrange = row[1].strip()
            sub_desc = row[2].strip() if len(row) > 2 else ""

            # Extract main category from text like "100-199 (full list) Colours"
            import re
            cat_match = re.search(r"\)\s*(.+)$", main_desc)
            category = cat_match.group(1).strip() if cat_match else main_desc

            # Parse subrange like "100-109" or "100–109"
            range_match = re.match(r"(\d+)\s*[-–]\s*(\d+)", subrange)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                mapping[(start, end)] = {
                    "category": category,
                    "subcategory": sub_desc,
                }

    return mapping


def parse_merged_csv(filepath: str | Path) -> list[dict]:
    """Parse final_INS_and_E_merged.csv (used mainly for E-to-INS mapping)."""
    df = pd.read_csv(filepath, encoding="utf-8")
    df.columns = df.columns.str.strip().str.lower()

    records = []
    for _, row in df.iterrows():
        code = str(row.get("code", "")).strip()
        if not code:
            continue

        status = str(row.get("status", "")).strip().lower()
        records.append({
            "ins_code": code,
            "common_name": str(row.get("names", "")).strip(),
            "category_raw": str(row.get("type", "")).strip(),
            "approval_codex": 1 if "a" in status else 0,
            "approval_eu": 1 if "e" in status else 0,
            "source": "final_INS_and_E_merged.csv",
        })

    return records


def parse_sqlite_db(filepath: str | Path) -> list[dict]:
    """Parse E-Number-Database/SQL database/E_Number.db for validation."""
    conn = sqlite3.connect(str(filepath))
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.execute("SELECT * FROM additives")
        records = []
        for row in cursor:
            e_code = row["e_code"].strip()
            records.append({
                "e_number": normalize_e_code(e_code),
                "common_name": row["title"].strip(),
                "description": row["info"].strip(),
                "category_raw": row["e_type"].strip(),
                "halal_status_raw": row["halal_status"].strip(),
                "source": "E_Number.db",
            })
        return records
    finally:
        conn.close()
