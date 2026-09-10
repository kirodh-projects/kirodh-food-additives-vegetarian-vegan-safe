# Shared Module

Cross-domain helpers used by every other module. Keep this package
**dependency-free of domain code**: `shared` must never import from
`food_additives`, `species`, `numbers`, or `ui`.

## Layout

```text
src/shared/
├── README.md              # this file
├── __init__.py            # re-exports config helpers
├── config.py              # DB_PATH / DATA_DIR / SPECIES_DB_DIR + getters
└── data_downloader.py     # generic download_file() / ensure_data()
```

## Usage

```python
from src.shared.config import get_db_path, get_data_dir, get_species_db_dir

db_path = get_db_path()          # $DB_PATH or ./databases/food_additives.db
data_dir = get_data_dir()        # $DATA_DIR or ./additive_databases
species_dir = get_species_db_dir()  # $SPECIES_DB_DIR or ./databases
```

```python
from src.shared.data_downloader import download_file, ensure_data

download_file("https://example.com/e.csv", "./data/e_numbers.csv")
ensure_data()  # uses $DATA_DIR / $E_DATA_URL
```

## Environment

| Variable         | Default                          | Used by            |
|------------------|----------------------------------|--------------------|
| `DB_PATH`        | `./databases/food_additives.db`  | `food_additives`   |
| `DATA_DIR`       | `./additive_databases`           | `food_additives`   |
| `SPECIES_DB_DIR` | `./databases`                    | `species`          |
| `APP_ENV`        | `development`                    | app                |
| `E_DATA_URL`     | *(unset)*                        | `data_downloader`  |

Domain `connection` modules re-export these getters so old imports
like `from src.food_additives.connection import get_db_path` keep working,
but new code should import from `src.shared.config` directly.
