"""Query functions for the species database.

Searches across all species_*.db files and aggregates results.
Statistics and distribution data are cached to a JSON file for fast loading.
"""

import json
import logging
import os

from src.db.species_connection import (
    get_species_connection,
    get_stats_cache_path,
    list_species_db_files,
)

logger = logging.getLogger(__name__)


def search_species(
    query: str,
    db_dir: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """Search species by scientific name, canonical name, or common terms."""
    db_files = list_species_db_files(db_dir)
    if not db_files:
        return []

    pattern = f"%{query.strip()}%"
    results = []

    for db_path in db_files:
        if len(results) >= limit:
            break

        remaining = limit - len(results)
        with get_species_connection(db_path) as conn:
            rows = conn.execute(
                """SELECT * FROM species
                WHERE scientific_name LIKE ? OR canonical_name LIKE ?
                    OR genus LIKE ? OR family LIKE ?
                ORDER BY scientific_name
                LIMIT ?""",
                (pattern, pattern, pattern, pattern, remaining),
            ).fetchall()
            results.extend(dict(r) for r in rows)

    return results[:limit]


def browse_species(
    db_dir: str | None = None,
    filters: dict | None = None,
    sort_by: str = "scientific_name",
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    """Browse species with filters and pagination across all DB files."""
    db_files = list_species_db_files(db_dir)
    if not db_files:
        return []

    allowed_sort = {
        "scientific_name", "canonical_name", "kingdom", "phylum",
        "class_name", "order_name", "family", "genus", "taxon_rank",
    }
    if sort_by not in allowed_sort:
        sort_by = "scientific_name"

    conditions, params = _build_filter_sql(filters)
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    results = []
    skipped = 0

    for db_path in db_files:
        if len(results) >= limit:
            break

        with get_species_connection(db_path) as conn:
            count_row = conn.execute(
                f"SELECT COUNT(*) FROM species {where}", params
            ).fetchone()
            count_in_file = count_row[0]

            if skipped + count_in_file <= offset:
                skipped += count_in_file
                continue

            local_offset = max(0, offset - skipped)
            remaining = limit - len(results)

            rows = conn.execute(
                f"SELECT * FROM species {where} ORDER BY {sort_by} LIMIT ? OFFSET ?",
                params + [remaining, local_offset],
            ).fetchall()
            results.extend(dict(r) for r in rows)
            skipped += count_in_file

    return results[:limit]


def get_species_total_count(
    db_dir: str | None = None,
    filters: dict | None = None,
) -> int:
    """Get total count of species across all DB files."""
    # If no filters, use cached total
    if not filters:
        cache = _load_cache(db_dir)
        if cache and "stats" in cache:
            return cache["stats"].get("total", 0)

    db_files = list_species_db_files(db_dir)
    if not db_files:
        return 0

    conditions, params = _build_filter_sql(filters)
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    total = 0
    for db_path in db_files:
        with get_species_connection(db_path) as conn:
            row = conn.execute(
                f"SELECT COUNT(*) FROM species {where}", params
            ).fetchone()
            total += row[0]

    return total


def get_species_stats(db_dir: str | None = None) -> dict:
    """Get aggregate statistics. Returns from cache if available."""
    cache = _load_cache(db_dir)
    if cache and "stats" in cache:
        return cache["stats"]

    return _compute_stats(db_dir)


def get_trait_distribution(db_dir: str | None = None) -> list[dict]:
    """Get trait scores aggregated by (kingdom, class_name) for the ternary plot.

    Returns from cache if available, otherwise computes and caches.
    """
    cache = _load_cache(db_dir)
    if cache and "distribution" in cache:
        return cache["distribution"]

    return _compute_distribution(db_dir)


def get_species_distinct_values(
    field: str,
    db_dir: str | None = None,
) -> list[str]:
    """Get distinct values for a field across all DB files."""
    # Check cache for pre-computed distinct values
    cache = _load_cache(db_dir)
    if cache and "distinct" in cache and field in cache["distinct"]:
        return cache["distinct"][field]

    allowed = {"kingdom", "phylum", "class_name", "order_name", "family", "taxon_rank", "taxonomic_status"}
    if field not in allowed:
        return []

    db_files = list_species_db_files(db_dir)
    values: set[str] = set()

    for db_path in db_files:
        with get_species_connection(db_path) as conn:
            rows = conn.execute(
                f"SELECT DISTINCT {field} FROM species WHERE {field} IS NOT NULL AND {field} != '' ORDER BY {field}"
            ).fetchall()
            values.update(row[0] for row in rows)

    return sorted(values)


# ── Cache management ───────────────────────────────────────────────────

def _load_cache(db_dir: str | None = None) -> dict | None:
    """Load the precomputed stats cache if it exists."""
    path = get_stats_cache_path(db_dir)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def build_stats_cache(db_dir: str | None = None) -> None:
    """Compute all expensive aggregations and save to a JSON cache file.

    Call this after building or migrating the species database.
    """
    logger.info("Building species stats cache...")

    stats = _compute_stats(db_dir)
    distribution = _compute_distribution(db_dir)
    distinct = _compute_all_distinct(db_dir)

    cache = {
        "stats": stats,
        "distribution": distribution,
        "distinct": distinct,
    }

    path = get_stats_cache_path(db_dir)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cache, f)

    logger.info("Stats cache saved to %s", path)


# ── Computation functions (expensive, called once for caching) ─────────

def _compute_stats(db_dir: str | None = None) -> dict:
    """Compute aggregate statistics across all species DB files (single pass)."""
    db_files = list_species_db_files(db_dir)
    if not db_files:
        return {"total": 0}

    total = 0
    kingdom_counts: dict[str, int] = {}
    rank_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    family_counts: dict[str, int] = {}
    trait_by_kingdom: dict[str, dict[str, float]] = {}
    has_traits = False
    has_gunas = False
    trait_sums = {"mob": 0.0, "warm": 0.0, "size": 0.0, "pur": 0.0, "pas": 0.0, "ign": 0.0}
    trait_total_count = 0

    for db_path in db_files:
        with get_species_connection(db_path) as conn:
            total += conn.execute("SELECT COUNT(*) FROM species").fetchone()[0]

            for row in conn.execute(
                "SELECT kingdom, COUNT(*) FROM species GROUP BY kingdom"
            ):
                k = row[0] or "Unknown"
                kingdom_counts[k] = kingdom_counts.get(k, 0) + row[1]

            for row in conn.execute(
                "SELECT taxon_rank, COUNT(*) FROM species GROUP BY taxon_rank"
            ):
                k = row[0] or "Unknown"
                rank_counts[k] = rank_counts.get(k, 0) + row[1]

            for row in conn.execute(
                "SELECT taxonomic_status, COUNT(*) FROM species GROUP BY taxonomic_status"
            ):
                k = row[0] or "Unknown"
                status_counts[k] = status_counts.get(k, 0) + row[1]

            for row in conn.execute(
                "SELECT family, COUNT(*) FROM species GROUP BY family ORDER BY 2 DESC LIMIT 30"
            ):
                k = row[0] or "Unknown"
                family_counts[k] = family_counts.get(k, 0) + row[1]

            if not has_traits:
                cols = {r[1] for r in conn.execute("PRAGMA table_info(species)")}
                has_traits = "mobility_score" in cols
                has_gunas = "purity_score" in cols

            if has_traits:
                guna_cols = ", SUM(purity_score), SUM(passion_score), SUM(ignorance_score)" if has_gunas else ""
                for row in conn.execute(
                    f"""SELECT kingdom,
                        SUM(mobility_score), SUM(warm_blood_score), SUM(size_score),
                        COUNT(*){guna_cols}
                    FROM species GROUP BY kingdom"""
                ):
                    k = row[0] or "Unknown"
                    cnt = row[4]
                    s_mob, s_warm, s_size = row[1] or 0, row[2] or 0, row[3] or 0
                    s_pur = (row[5] or 0) if has_gunas else 0
                    s_pas = (row[6] or 0) if has_gunas else 0
                    s_ign = (row[7] or 0) if has_gunas else 0

                    if k not in trait_by_kingdom:
                        trait_by_kingdom[k] = {
                            "sum_mob": 0.0, "sum_warm": 0.0, "sum_size": 0.0,
                            "sum_pur": 0.0, "sum_pas": 0.0, "sum_ign": 0.0,
                            "count": 0,
                        }
                    entry = trait_by_kingdom[k]
                    entry["sum_mob"] += s_mob
                    entry["sum_warm"] += s_warm
                    entry["sum_size"] += s_size
                    entry["sum_pur"] += s_pur
                    entry["sum_pas"] += s_pas
                    entry["sum_ign"] += s_ign
                    entry["count"] += cnt

                    trait_sums["mob"] += s_mob
                    trait_sums["warm"] += s_warm
                    trait_sums["size"] += s_size
                    trait_sums["pur"] += s_pur
                    trait_sums["pas"] += s_pas
                    trait_sums["ign"] += s_ign
                    trait_total_count += cnt

    top_families = dict(sorted(family_counts.items(), key=lambda x: x[1], reverse=True)[:20])

    finalised_traits: dict[str, dict[str, float]] = {}
    for k, entry in trait_by_kingdom.items():
        cnt = entry["count"]
        if cnt > 0:
            finalised_traits[k] = {
                "mobility": entry["sum_mob"] / cnt,
                "warm_blood": entry["sum_warm"] / cnt,
                "size": entry["sum_size"] / cnt,
                "purity": entry["sum_pur"] / cnt,
                "passion": entry["sum_pas"] / cnt,
                "ignorance": entry["sum_ign"] / cnt,
                "count": cnt,
            }

    tc = trait_total_count or 1
    return {
        "total": total,
        "kingdoms": dict(sorted(kingdom_counts.items(), key=lambda x: x[1], reverse=True)),
        "ranks": dict(sorted(rank_counts.items(), key=lambda x: x[1], reverse=True)),
        "statuses": dict(sorted(status_counts.items(), key=lambda x: x[1], reverse=True)),
        "top_families": top_families,
        "db_file_count": len(db_files),
        "trait_by_kingdom": finalised_traits,
        "avg_mobility": trait_sums["mob"] / tc,
        "avg_warm_blood": trait_sums["warm"] / tc,
        "avg_size": trait_sums["size"] / tc,
        "avg_purity": trait_sums["pur"] / tc,
        "avg_passion": trait_sums["pas"] / tc,
        "avg_ignorance": trait_sums["ign"] / tc,
    }


def _compute_distribution(db_dir: str | None = None) -> list[dict]:
    """Compute trait distribution grouped by (kingdom, class_name)."""
    db_files = list_species_db_files(db_dir)
    if not db_files:
        return []

    groups: dict[tuple[str, str], dict] = {}
    has_gunas = False

    for db_path in db_files:
        with get_species_connection(db_path) as conn:
            cols = {r[1] for r in conn.execute("PRAGMA table_info(species)")}
            if "mobility_score" not in cols:
                return []
            if not has_gunas:
                has_gunas = "purity_score" in cols

            guna_cols = ", SUM(purity_score), SUM(passion_score), SUM(ignorance_score)" if has_gunas else ""
            for row in conn.execute(
                f"""SELECT kingdom, class_name,
                    SUM(mobility_score), SUM(warm_blood_score), SUM(size_score),
                    COUNT(*){guna_cols}
                FROM species
                GROUP BY kingdom, class_name"""
            ):
                k = row[0] or "Unknown"
                c = row[1] or "(unclassified)"
                key = (k, c)
                cnt = row[5]
                s_mob, s_warm, s_size = row[2] or 0, row[3] or 0, row[4] or 0
                s_pur = (row[6] or 0) if has_gunas else 0
                s_pas = (row[7] or 0) if has_gunas else 0
                s_ign = (row[8] or 0) if has_gunas else 0

                if key not in groups:
                    groups[key] = {
                        "sum_mob": 0.0, "sum_warm": 0.0, "sum_size": 0.0,
                        "sum_pur": 0.0, "sum_pas": 0.0, "sum_ign": 0.0,
                        "count": 0,
                    }
                entry = groups[key]
                entry["sum_mob"] += s_mob
                entry["sum_warm"] += s_warm
                entry["sum_size"] += s_size
                entry["sum_pur"] += s_pur
                entry["sum_pas"] += s_pas
                entry["sum_ign"] += s_ign
                entry["count"] += cnt

    result = []
    for (kingdom, class_name), entry in groups.items():
        cnt = entry["count"]
        if cnt > 0:
            result.append({
                "kingdom": kingdom,
                "class_name": class_name,
                "mobility": entry["sum_mob"] / cnt,
                "warm_blood": entry["sum_warm"] / cnt,
                "size": entry["sum_size"] / cnt,
                "purity": entry["sum_pur"] / cnt,
                "passion": entry["sum_pas"] / cnt,
                "ignorance": entry["sum_ign"] / cnt,
                "count": cnt,
            })

    return sorted(result, key=lambda r: r["count"], reverse=True)


def _compute_all_distinct(db_dir: str | None = None) -> dict[str, list[str]]:
    """Pre-compute distinct values for all filterable fields."""
    fields = ["kingdom", "phylum", "class_name", "order_name", "family", "taxon_rank", "taxonomic_status"]
    db_files = list_species_db_files(db_dir)
    if not db_files:
        return {}

    values: dict[str, set[str]] = {f: set() for f in fields}

    for db_path in db_files:
        with get_species_connection(db_path) as conn:
            for field in fields:
                rows = conn.execute(
                    f"SELECT DISTINCT {field} FROM species WHERE {field} IS NOT NULL AND {field} != ''"
                ).fetchall()
                values[field].update(row[0] for row in rows)

    return {f: sorted(v) for f, v in values.items()}


def _build_filter_sql(filters: dict | None) -> tuple[list[str], list]:
    """Build WHERE conditions from filters dict."""
    conditions = []
    params = []

    if not filters:
        return conditions, params

    for field in ["kingdom", "phylum", "class_name", "order_name",
                   "family", "genus", "taxon_rank", "taxonomic_status"]:
        if field in filters and filters[field]:
            values = filters[field]
            if isinstance(values, str):
                values = [values]
            placeholders = ",".join("?" * len(values))
            conditions.append(f"{field} IN ({placeholders})")
            params.extend(values)

    return conditions, params
