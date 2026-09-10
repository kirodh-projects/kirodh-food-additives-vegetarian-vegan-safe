# Food additives engine

Independent vegan / vegetarian (lacto) / halal / safety / origin lookup per
E-number or INS number. No Streamlit, no other engines.

## Files

| File | Purpose |
|---|---|
| `config.py` | `DB_PATH` / `DATA_DIR` (vendored, self-contained) |
| `schema.py` | `CREATE TABLE` for `additives`, `source_records` |
| `connection.py` | SQLite connection (WAL) + `ensure_database()` |
| `queries.py` | `search_by_code`, `search_by_name`, browse, analytics, duplicates |
| `classifiers.py` | 3-tier vegan/vegetarian/safety/origin classification |
| `constants.py` | Tier-1 lookup + keyword lists |
| `text_analysis.py` | Phrase matching + ADI extraction |
| `parsers.py` | 7 parsers for `additive_databases/` |
| `normalizers.py` | E-code normalisation, category mapping, dedup |
| `e_ins_mapper.py` | E-number <-> INS cross-reference |
| `web_scraper.py` | Supplementary web-informed data (locally cached) |
| `build_database.py` | ETL orchestrator (idempotent) |
| `duplicates.py` | Duplicate checker CLI |
| `plots.py` | **data / PNG / plotly** dashboard builders + local server |

## Use as a library

```python
from engines.food_additives.connection import ensure_database
from engines.food_additives.queries import search_by_code, get_analytics_summary
from engines.food_additives.classifiers import classify_all

db = ensure_database("./databases/food_additives.db")
print(search_by_code(db, "E120"))   # cochineal -> vegan No
print(get_analytics_summary(db)["total"])
print(classify_all("E100", "Curcumin from turmeric, natural colouring"))
```

## Build the database

```bash
python -m engines.food_additives.build_database
python -m engines.food_additives.build_database --force
python -m engines.food_additives.build_database --db-path ./databases/food_additives.db --data-dir ./additive_databases
```

Note: `build_database.py` still says `python -m src.food_additives...` in its
docstring — use the `engines.` path above (behaviour is identical).

## Examples (inside this module)

```bash
python -m engines.food_additives.examples.example_lookup --code E120
python -m engines.food_additives.examples.example_analytics --backend data
python -m engines.food_additives.examples.example_analytics --backend png --out analytics.png
python -m engines.food_additives.examples.example_analytics --backend plotly --out analytics.html --serve
python -m engines.food_additives.examples.example_duplicates
```
