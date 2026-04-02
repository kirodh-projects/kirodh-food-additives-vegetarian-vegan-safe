"""Database query functions for the food additives app.

All read operations go through this module. The UI layer should
only import from here, never construct SQL directly.
"""

from src.db.connection import get_connection


def search_by_code(db_path: str, code: str) -> dict | None:
    """Search for an additive by E-number or INS number.

    Handles inputs like: '100', 'E100', 'e100', 'INS 100', 'INS100'.
    """
    clean = code.strip().upper().replace("INS ", "").replace("INS", "")

    # Try as E-number
    e_code = clean if clean.startswith("E") else f"E{clean}"

    with get_connection(db_path) as conn:
        # Search by E-number (case-insensitive)
        row = conn.execute(
            "SELECT * FROM additives WHERE UPPER(e_number) = ?",
            (e_code.upper(),),
        ).fetchone()

        if row:
            return dict(row)

        # Search by INS number
        row = conn.execute(
            "SELECT * FROM additives WHERE LOWER(ins_number) = ?",
            (clean.lower().lstrip("e"),),
        ).fetchone()

        if row:
            return dict(row)

    return None


def search_by_name(db_path: str, name: str) -> list[dict]:
    """Search additives by name (partial match)."""
    pattern = f"%{name.strip()}%"

    with get_connection(db_path) as conn:
        rows = conn.execute(
            """SELECT * FROM additives
            WHERE common_name LIKE ? OR chemical_name LIKE ? OR alternative_names LIKE ?
            ORDER BY e_number
            LIMIT 50""",
            (pattern, pattern, pattern),
        ).fetchall()

    return [dict(r) for r in rows]


def get_all_additives(
    db_path: str,
    filters: dict | None = None,
    sort_by: str = "e_number",
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """Retrieve additives with optional filters and pagination."""
    allowed_sort = {
        "e_number", "common_name", "category", "safety_level",
        "vegan_status", "vegetarian_status", "halal_status",
    }
    if sort_by not in allowed_sort:
        sort_by = "e_number"

    conditions = []
    params = []

    if filters:
        for field in ["category", "vegan_status", "vegetarian_status",
                       "halal_status", "safety_level", "origin"]:
            if field in filters and filters[field]:
                values = filters[field]
                if isinstance(values, str):
                    values = [values]
                placeholders = ",".join("?" * len(values))
                conditions.append(f"{field} IN ({placeholders})")
                params.extend(values)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"SELECT * FROM additives {where} ORDER BY {sort_by} LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_connection(db_path) as conn:
        rows = conn.execute(query, params).fetchall()

    return [dict(r) for r in rows]


def get_total_count(db_path: str, filters: dict | None = None) -> int:
    """Get total count of additives matching filters."""
    conditions = []
    params = []

    if filters:
        for field in ["category", "vegan_status", "vegetarian_status",
                       "halal_status", "safety_level", "origin"]:
            if field in filters and filters[field]:
                values = filters[field]
                if isinstance(values, str):
                    values = [values]
                placeholders = ",".join("?" * len(values))
                conditions.append(f"{field} IN ({placeholders})")
                params.extend(values)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    query = f"SELECT COUNT(*) FROM additives {where}"

    with get_connection(db_path) as conn:
        return conn.execute(query, params).fetchone()[0]


def get_analytics_summary(db_path: str) -> dict:
    """Return aggregate statistics for the analytics dashboard."""
    with get_connection(db_path) as conn:
        total = conn.execute("SELECT COUNT(*) FROM additives").fetchone()[0]

        summary = {"total": total}

        for field in ["vegan_status", "vegetarian_status", "halal_status",
                       "safety_level", "origin", "category"]:
            rows = conn.execute(
                f"SELECT {field}, COUNT(*) as cnt FROM additives GROUP BY {field} ORDER BY cnt DESC"
            ).fetchall()
            summary[field] = {row[0]: row[1] for row in rows}

        # Approval stats
        summary["approval_eu"] = conn.execute(
            "SELECT COUNT(*) FROM additives WHERE approval_eu = 1"
        ).fetchone()[0]
        summary["approval_us"] = conn.execute(
            "SELECT COUNT(*) FROM additives WHERE approval_us = 1"
        ).fetchone()[0]
        summary["approval_codex"] = conn.execute(
            "SELECT COUNT(*) FROM additives WHERE approval_codex = 1"
        ).fetchone()[0]
        summary["banned_count"] = conn.execute(
            "SELECT COUNT(*) FROM additives WHERE is_banned_anywhere = 1"
        ).fetchone()[0]

    return summary


def get_dangerous_additives(db_path: str) -> list[dict]:
    """Get additives with safety level 'Avoid' or 'Banned'."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """SELECT * FROM additives
            WHERE safety_level IN ('Avoid', 'Banned')
            ORDER BY safety_level DESC, e_number"""
        ).fetchall()

    return [dict(r) for r in rows]


def get_category_vegan_breakdown(db_path: str) -> list[dict]:
    """Get count of vegan status per category for stacked bar chart."""
    with get_connection(db_path) as conn:
        rows = conn.execute(
            """SELECT category, vegan_status, COUNT(*) as cnt
            FROM additives
            GROUP BY category, vegan_status
            ORDER BY category, vegan_status"""
        ).fetchall()

    return [dict(r) for r in rows]


def check_duplicates(db_path: str) -> dict:
    """Check for various types of duplicates in the database."""
    results = {
        "exact_e_number_dupes": [],
        "ins_multi_mapping": [],
        "similar_names": [],
    }

    with get_connection(db_path) as conn:
        # Exact E-number duplicates (should be 0 due to UNIQUE constraint)
        rows = conn.execute(
            """SELECT e_number, COUNT(*) as cnt
            FROM additives GROUP BY e_number HAVING cnt > 1"""
        ).fetchall()
        results["exact_e_number_dupes"] = [dict(r) for r in rows]

        # Same INS number mapped to multiple E-numbers
        rows = conn.execute(
            """SELECT ins_number, COUNT(*) as cnt, GROUP_CONCAT(e_number) as e_numbers
            FROM additives
            WHERE ins_number IS NOT NULL AND ins_number != ''
            GROUP BY ins_number HAVING cnt > 1"""
        ).fetchall()
        results["ins_multi_mapping"] = [dict(r) for r in rows]

    return results


def get_distinct_values(db_path: str, field: str) -> list[str]:
    """Get distinct values for a field (for filter dropdowns)."""
    allowed = {
        "category", "vegan_status", "vegetarian_status",
        "halal_status", "safety_level", "origin",
    }
    if field not in allowed:
        return []

    with get_connection(db_path) as conn:
        rows = conn.execute(
            f"SELECT DISTINCT {field} FROM additives WHERE {field} IS NOT NULL ORDER BY {field}"
        ).fetchall()

    return [row[0] for row in rows]
