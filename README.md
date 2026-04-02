# Food Additives - Vegan, Vegetarian & Halal Safety Database

**Author:** Kirodh

A comprehensive database and web application for looking up food additives (E-numbers and INS numbers) with classifications for vegan, vegetarian (lacto), halal, safety level, and origin. Combines multiple open data sources into a single searchable SQLite database with an interactive Streamlit dashboard.

---

## Purpose

Food product labels list additives by E-number or INS number, but it is difficult to tell at a glance whether an additive is:

- **Vegan** (no animal products at all)
- **Vegetarian** (lacto-vegetarian: dairy allowed, no eggs, no meat/fish/insects)
- **Halal** (permissible under Islamic dietary law)
- **Safe** or potentially dangerous
- **Synthetic** or naturally derived

This project solves that by merging several open databases, classifying each additive using a three-tier system (curated lookup tables, keyword text analysis, and supplementary web-informed data), and presenting the results through a searchable web interface with analytics.

---

## Features

- Search by E-number, INS number, or name (partial match)
- Detailed additive cards showing vegan, vegetarian, halal, safety, and origin status
- Analytics dashboard with interactive Plotly charts:
  - Pie charts for vegan, vegetarian, halal, and origin distributions
  - Bar charts for safety levels and category breakdown
  - Stacked bar chart: vegan status by category
  - Dangerous additives table (Avoid / Banned)
  - Metric cards: total count, % vegan, % safe, % EU-approved, etc.
- Filterable, paginated browse table with CSV export
- Idempotent database builder (safe to re-run)
- Standalone duplicate checker script

---

## Quick Start

### Prerequisites

- Python 3.12+
- pip

### Install dependencies

```bash
pip install -r requirements.txt
```

### Build the database

```bash
python -m src.etl.build_database
```

This reads all data sources from `additive_databases/`, merges and classifies them, and writes `food_additives.db` to the project root. It is idempotent: if data already exists, it skips. Use `--force` to rebuild from scratch:

```bash
python -m src.etl.build_database --force
```

### Run the app

```bash
streamlit run app.py
```

The app opens at [http://localhost:8501](http://localhost:8501).

### Check for duplicates

```bash
python check_duplicates.py
```

### Run tests

```bash
pip install pytest pytest-cov
pytest tests/ -v
```

With coverage:

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## Docker

```bash
docker compose up --build
```

The database is built at image build time. The app is available at [http://localhost:8501](http://localhost:8501).

---

## Project Structure

```
.
+-- app.py                          # Streamlit entry point (thin wrapper)
+-- check_duplicates.py             # Standalone duplicate checker script
+-- pyproject.toml                  # Project config, dependencies, pytest/ruff settings
+-- requirements.txt                # Python dependencies
+-- Dockerfile                      # Python 3.12-slim container
+-- docker-compose.yaml             # Docker Compose service definition
+-- .env                            # Environment config (DB_PATH, DATA_DIR)
+-- food_additives.db               # SQLite database (generated, gitignored)
+-- math_plotter.py                 # Unrelated utility (not part of this app)
+-- data_downloader.py              # Legacy data downloader (deprecated)
|
+-- additive_databases/             # Raw data sources (read-only)
|   +-- additives.csv              # Primary: 562 E-numbers with info & halal status
|   +-- final_INS_and_E_merged.csv # Merged INS/E mapping reference
|   +-- INSfoodnotes.xlsx          # INS notes (Excel)
|   +-- E-Number-Database/         # E-number database (CSV + SQLite)
|   |   +-- CSV/additives.csv
|   |   +-- SQL database/E_Number.db
|   +-- food-additive/             # E and INS indexes with approval status
|       +-- e/index.csv            # 511 E-numbers
|       +-- e/assets/e100..e1000.csv  # Per-category detail CSVs
|       +-- e/assets/classification.csv  # E-number range classification
|       +-- ins/index.csv          # 437 INS numbers
|
+-- src/
|   +-- db/                         # Database layer (read path)
|   |   +-- schema.py              # CREATE TABLE definitions, schema version
|   |   +-- connection.py          # SQLite connection context manager (WAL mode)
|   |   +-- queries.py             # All read queries (search, analytics, browse, duplicates)
|   |
|   +-- etl/                        # ETL pipeline (write path)
|   |   +-- build_database.py      # Main ETL orchestrator (entry point)
|   |   +-- parsers.py             # 7 parsers for each raw data source
|   |   +-- normalizers.py         # E-code normalization, category mapping, dedup
|   |   +-- classifiers.py        # Three-tier vegan/vegetarian/safety/origin classification
|   |   +-- e_ins_mapper.py       # E-number <-> INS number cross-reference
|   |   +-- web_scraper.py        # Supplementary web-informed classification data
|   |
|   +-- ui/                         # Streamlit UI layer
|   |   +-- app.py                 # App routing (Search / Analytics / Browse)
|   |   +-- pages/
|   |   |   +-- search.py         # Search by E/INS number or name
|   |   |   +-- analytics.py      # Charts and statistics dashboard
|   |   |   +-- browse.py         # Filterable, paginated data table + CSV export
|   |   +-- components/
|   |       +-- additive_card.py  # Single additive display card with status pills
|   |       +-- charts.py         # Plotly chart builder functions
|   |
|   +-- utils/                      # Shared utilities
|       +-- constants.py           # Keyword lists, known E-number classification tables
|       +-- text_analysis.py       # Keyword matching with context exclusion logic
|
+-- tests/                          # Test suite (89 tests)
    +-- conftest.py                # Shared fixtures (in-memory DB, sample data)
    +-- test_classifiers.py        # 32 tests: vegan/vegetarian/safety/origin classification
    +-- test_normalizers.py        # 18 tests: E-code normalization, category mapping
    +-- test_e_ins_mapper.py       # 9 tests: E-to-INS mapping
    +-- test_queries.py            # 12 tests: search, analytics, filters, pagination
    +-- test_build_database.py     # 5 tests: full ETL integration, idempotency
```

---

## Database Schema

The SQLite database (`food_additives.db`) contains two tables:

### `additives` (primary table)

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key (auto-increment) |
| `e_number` | TEXT | Canonical E-number, e.g. "E100", "E160a" (UNIQUE) |
| `ins_number` | TEXT | Corresponding INS number, e.g. "100", "160a" (nullable) |
| `chemical_name` | TEXT | Chemical/scientific name |
| `common_name` | TEXT | Primary display name |
| `alternative_names` | TEXT | Semicolon-delimited aliases |
| `category` | TEXT | Normalized category (15 values: Colouring, Preservative, Emulsifier, etc.) |
| `subcategory` | TEXT | Finer classification from E-number ranges |
| `description` | TEXT | Full description (origin, uses, side effects) |
| `halal_status` | TEXT | Halal / Doubtful / Haram / Unknown |
| `vegan_status` | TEXT | Yes / No / Maybe / Unknown |
| `vegetarian_status` | TEXT | Yes / No / Maybe / Unknown (lacto-vegetarian: dairy OK, eggs NOT OK) |
| `safety_level` | TEXT | Safe / Caution / Avoid / Banned / Unknown |
| `origin` | TEXT | Synthetic / Natural (Plant) / Natural (Animal) / Natural (Mineral) / Mixed / Unknown |
| `adi` | TEXT | Acceptable Daily Intake (extracted from description if present) |
| `approval_eu` | INTEGER | 1 if approved in the EU |
| `approval_us` | INTEGER | 1 if approved in the US |
| `approval_codex` | INTEGER | 1 if in the Codex Alimentarius |
| `is_banned_anywhere` | INTEGER | 1 if banned in any jurisdiction |
| `source_files` | TEXT | Which data source files contributed to this record |
| `created_at` | TEXT | Record creation timestamp |
| `updated_at` | TEXT | Record update timestamp |

Indexes on: `e_number`, `ins_number`, `category`, `vegan_status`, `vegetarian_status`, `safety_level`, `halal_status`, `origin`.

### `source_records` (audit trail)

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Primary key |
| `additive_id` | INTEGER | Foreign key to `additives.id` |
| `source_file` | TEXT | Which source file this record came from |
| `raw_code` | TEXT | Original code as it appeared in the source |
| `raw_data` | TEXT | JSON blob of the original parsed row |
| `imported_at` | TEXT | Import timestamp |

### `schema_version`

Tracks the database schema version for future migrations.

---

## Classification Methodology

Each additive is classified for vegan, vegetarian, safety, and origin using a **three-tier system**:

### Tier 1: Curated Lookup Table (highest confidence)

A manually verified dictionary of ~100 well-known E-numbers with established classifications. Examples:
- E120 (Cochineal) -> Vegan: No, Vegetarian: No, Origin: Animal (crushed insects)
- E100 (Curcumin) -> Vegan: Yes, Vegetarian: Yes, Origin: Plant (turmeric)
- E966 (Lactitol) -> Vegan: No, Vegetarian: Yes, Origin: Animal (dairy-derived, no killing)

### Tier 2: Keyword Text Analysis (medium confidence)

For E-numbers not in the lookup table, the `description` field is scanned using multi-word phrase matching with context exclusions:
- **Animal keywords** ("pancreas of pigs", "cow bile", "gelatin") -> Not vegan/vegetarian
- **Egg keywords** ("egg white", "albumin", "lysozyme") -> Not vegan AND not lacto-vegetarian
- **Dairy keywords** ("milk", "lactose", "casein") -> Not vegan, but lacto-vegetarian OK
- **Safety keywords** ("carcinogenic", "banned", "no side effects") -> Safety classification
- **Context exclusions** ("laboratory animals", "tested in animals") -> Prevents false positives from test/study contexts

### Tier 3: Web-Informed Supplementary Data (fallback)

An additional curated dataset of ~87 E-numbers informed by publicly available dietary classification resources. Cached locally to avoid repeated lookups.

---

## Database Statistics

After building from all sources:

| Metric | Count |
|---|---|
| Total unique additives | 561 |
| E-to-INS mappings | 398 |
| Vegan: Yes | 296 |
| Vegan: Maybe | 52 |
| Vegan: No | 116 |
| Safe | 220 |
| Caution | 85 |
| Avoid | 112 |
| Banned | 13 |

---

## Test Coverage

89 tests passing across 5 test modules:

| Module | Tests | Coverage |
|---|---|---|
| `test_classifiers.py` | 32 | classifiers.py: 100% |
| `test_normalizers.py` | 18 | normalizers.py: 88% |
| `test_e_ins_mapper.py` | 9 | e_ins_mapper.py: 98% |
| `test_queries.py` | 12 | queries.py: 82% |
| `test_build_database.py` | 5 | build_database.py: 87% |

Core logic modules (classifiers, schema, constants) have 100% coverage. UI components are not unit-tested as they require a Streamlit runtime.

---

## Configuration

Environment variables (`.env`):

| Variable | Default | Description |
|---|---|---|
| `DB_PATH` | `./food_additives.db` | Path to the SQLite database file |
| `DATA_DIR` | `./additive_databases` | Path to the raw data sources directory |
| `APP_ENV` | `development` | Application environment |

---

## Data Sources

With many thanks to the following open data projects:

| Source | Description | License |
|---|---|---|
| [FAO GSFA Online](https://www.fao.org/gsfaonline/additives/search.html) | Codex Alimentarius food additive database | Public |
| [E-Number-Database](https://github.com/SuhasDissa/E-Number-Database) | 562 E-numbers with descriptions and halal status | GPL-3.0 |
| [food-additive](https://github.com/nodef/food-additive) | E-number and INS number indexes with approval status | AGPL-3.0 |
| [food-info.net](https://www.food-info.net/uk/qa/qa-fi45.htm) | Food additive Q&A reference | Public |

---

## License

See [LICENSE](LICENSE) for details.
