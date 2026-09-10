"""Local config for the species engine (no cross-engine imports).

Vendored so this engine is self-contained: copy the
``engines/species/`` folder anywhere and it keeps working.
"""

import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_SPECIES_DB_DIR = "./databases"


def get_species_db_dir() -> str:
    """Directory for species taxonomy DB files."""
    return os.getenv("SPECIES_DB_DIR", DEFAULT_SPECIES_DB_DIR)
