"""Database schema for the species taxonomy database."""

SCHEMA_VERSION = 2

CREATE_SPECIES_TABLE = """
CREATE TABLE IF NOT EXISTS species (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    taxon_id            INTEGER,
    scientific_name     TEXT NOT NULL,
    canonical_name      TEXT,
    authorship          TEXT,
    kingdom             TEXT,
    phylum              TEXT,
    class_name          TEXT,
    order_name          TEXT,
    family              TEXT,
    genus               TEXT,
    specific_epithet    TEXT,
    infraspecific_epithet TEXT,
    taxon_rank          TEXT,
    taxonomic_status    TEXT,
    accepted_taxon_id   INTEGER,
    source              TEXT DEFAULT 'GBIF',
    mobility_score      REAL DEFAULT 0.0,
    warm_blood_score    REAL DEFAULT 0.0,
    size_score          REAL DEFAULT 0.0
);
"""

CREATE_SPECIES_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_species_scientific ON species(scientific_name COLLATE NOCASE);",
    "CREATE INDEX IF NOT EXISTS idx_species_canonical ON species(canonical_name COLLATE NOCASE);",
    "CREATE INDEX IF NOT EXISTS idx_species_kingdom ON species(kingdom);",
    "CREATE INDEX IF NOT EXISTS idx_species_family ON species(family);",
    "CREATE INDEX IF NOT EXISTS idx_species_genus ON species(genus);",
    "CREATE INDEX IF NOT EXISTS idx_species_taxon_rank ON species(taxon_rank);",
    "CREATE INDEX IF NOT EXISTS idx_species_taxonomic_status ON species(taxonomic_status);",
    "CREATE INDEX IF NOT EXISTS idx_species_taxon_id ON species(taxon_id);",
]

CREATE_SPECIES_META = """
CREATE TABLE IF NOT EXISTS db_meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""


def create_species_tables(conn) -> None:
    """Create species tables and indexes."""
    cursor = conn.cursor()
    cursor.execute(CREATE_SPECIES_TABLE)
    cursor.execute(CREATE_SPECIES_META)
    for idx_sql in CREATE_SPECIES_INDEXES:
        cursor.execute(idx_sql)
    conn.commit()
