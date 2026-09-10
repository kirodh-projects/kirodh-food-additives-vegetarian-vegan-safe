# Food Additives Module

Look up E-numbers and INS numbers with vegan, vegetarian (lacto), halal,
safety, and origin classifications.

This is a self-contained domain package: database, ETL, classification
logic, maintenance scripts, Streamlit UI, and tests all live here.
It only depends on `src.shared` for config — never on `species` or `numbers`.

## Layout

```text
src/food_additives/
├── README.md              # this file
├── __init__.py            # public API (connection helpers)
├── schema.py              # CREATE TABLE for additives, source_records, schema_version
├── connection.py          # SQLite connection manager (WAL mode), get_db_path()
├── queries.py             # all read queries: search, browse, analytics, duplicates
├── constants.py           # Tier-1 lookup table + keyword lists
├── text_analysis.py       # phrase matching with context exclusions, ADI extraction
├── classifiers.py         # 3-tier vegan/vegetarian/safety/origin classification
├── parsers.py             # 7 parsers for the raw sources in additive_databases/
├── normalizers.py         # E-code normalisation, category mapping, dedup
├── e_ins_mapper.py        # E-number <-> INS cross-reference
├── web_scraper.py         # supplementary web-informed data (locally cached)
├── build_database.py      # ETL orchestrator (idempotent)
├── duplicates.py          # duplicate checker CLI (python -m src.food_additives.duplicates)
└── ui/
    ├── search.py          # search by code or name
    ├── analytics.py       # Plotly dashboard + dangerous-additives table
    ├── browse.py          # filterable, paginated table with CSV export
    ├── additive_card.py   # single-additive display card
    └── charts.py          # pie / bar / stacked-bar builders
```

## Quick start

```bash
# Build (idempotent — skips if data exists)
python -m src.food_additives.build_database

# Force rebuild
python -m src.food_additives.build_database --force

# Custom paths
python -m src.food_additives.build_database --db-path ./databases/food_additives.db --data-dir ./additive_databases

# Check duplicates
python -m src.food_additives.duplicates
# legacy wrapper still works:
python check_duplicates.py
```

## Code examples

```python
from src.food_additives.connection import get_db_path
from src.food_additives.queries import search_by_code, get_analytics_summary

db = get_db_path()
print(search_by_code(db, "E120"))   # cochineal -> vegan No
print(get_analytics_summary(db)["total"])
```

```python
from src.food_additives.classifiers import classify_all

print(classify_all("E100", "Curcumin from turmeric, natural colouring"))
# {'vegan_status': 'Yes', 'vegetarian_status': 'Yes', ...}
```

## Classification methodology (3 tiers)

1. **Tier 1 — curated lookup** (`constants.KNOWN_CLASSIFICATIONS`, ~100 E-numbers).
   Highest confidence, e.g. E120 → animal/insect, E100 → plant.
2. **Tier 2 — keyword text analysis** (`text_analysis` + keyword lists).
   Multi-word phrase matching with exclusions like "laboratory animals"
   so test contexts don't cause false positives.
   Dairy → not vegan but lacto-vegetarian OK; egg → neither.
3. **Tier 3 — web-informed supplementary data** (`web_scraper`, ~87 E-numbers,
   cached to `additive_databases/.web_scrape_cache.json`).

## Database schema

SQLite file at `$DB_PATH` (default `./databases/food_additives.db`):

- `additives` — one row per canonical E-number (`e_number` UNIQUE),
  with `ins_number`, names, `category`/`subcategory`, `description`,
  `halal_status`, `vegan_status`, `vegetarian_status`, `safety_level`,
  `origin`, `adi`, `approval_eu/us/codex`, `is_banned_anywhere`, `source_files`.
- `source_records` — audit trail (which source file contributed which row).
- `schema_version` — migration version.

Indexes on `e_number`, `ins_number`, `category`, `vegan_status`,
`vegetarian_status`, `safety_level`, `halal_status`, `origin`.

## Environment

| Variable   | Default                          | Description              |
|------------|----------------------------------|--------------------------|
| `DB_PATH`  | `./databases/food_additives.db`  | SQLite file              |
| `DATA_DIR` | `./additive_databases`           | Raw sources directory    |

See `src.shared.config` for the canonical definitions.

## Tests

```bash
pytest tests/food_additives/ -v
# 64 tests: classifiers, normalizers, e_ins_mapper, queries, build_database
```
