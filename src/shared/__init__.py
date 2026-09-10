"""Shared cross-domain utilities.

- :mod:`src.shared.config` — environment variables and default paths
  (``DB_PATH``, ``DATA_DIR``, ``SPECIES_DB_DIR``).
- :mod:`src.shared.data_downloader` — generic file-download helper.

Domain packages (``food_additives``, ``species``, ``numbers``) should
import shared helpers from here instead of duplicating ``os.getenv`` /
``load_dotenv`` logic.
"""

from src.shared.config import get_data_dir, get_db_path, get_species_db_dir

__all__ = ["get_db_path", "get_data_dir", "get_species_db_dir"]
