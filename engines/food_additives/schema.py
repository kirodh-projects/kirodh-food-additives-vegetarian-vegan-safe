"""Database schema definitions for the food additives database."""

SCHEMA_VERSION = 1

CREATE_ADDITIVES_TABLE = """
CREATE TABLE IF NOT EXISTS additives (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    e_number              TEXT NOT NULL,
    ins_number            TEXT,
    chemical_name         TEXT,
    common_name           TEXT NOT NULL,
    alternative_names     TEXT,
    category              TEXT NOT NULL DEFAULT 'Unknown',
    subcategory           TEXT,
    description           TEXT,
    halal_status          TEXT DEFAULT 'Unknown',
    vegan_status          TEXT DEFAULT 'Unknown',
    vegetarian_status     TEXT DEFAULT 'Unknown',
    safety_level          TEXT DEFAULT 'Unknown',
    origin                TEXT DEFAULT 'Unknown',
    adi                   TEXT,
    approval_eu           INTEGER DEFAULT 0,
    approval_us           INTEGER DEFAULT 0,
    approval_codex        INTEGER DEFAULT 0,
    is_banned_anywhere    INTEGER DEFAULT 0,
    source_files          TEXT,
    created_at            TEXT DEFAULT (datetime('now')),
    updated_at            TEXT DEFAULT (datetime('now')),
    UNIQUE(e_number)
);
"""

CREATE_SOURCE_RECORDS_TABLE = """
CREATE TABLE IF NOT EXISTS source_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    additive_id     INTEGER NOT NULL REFERENCES additives(id),
    source_file     TEXT NOT NULL,
    raw_code        TEXT NOT NULL,
    raw_data        TEXT NOT NULL,
    imported_at     TEXT DEFAULT (datetime('now'))
);
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_additives_e_number ON additives(e_number);",
    "CREATE INDEX IF NOT EXISTS idx_additives_ins_number ON additives(ins_number);",
    "CREATE INDEX IF NOT EXISTS idx_additives_category ON additives(category);",
    "CREATE INDEX IF NOT EXISTS idx_additives_vegan_status ON additives(vegan_status);",
    "CREATE INDEX IF NOT EXISTS idx_additives_vegetarian_status ON additives(vegetarian_status);",
    "CREATE INDEX IF NOT EXISTS idx_additives_safety_level ON additives(safety_level);",
    "CREATE INDEX IF NOT EXISTS idx_additives_halal_status ON additives(halal_status);",
    "CREATE INDEX IF NOT EXISTS idx_additives_origin ON additives(origin);",
]

CREATE_SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL,
    applied_at TEXT DEFAULT (datetime('now'))
);
"""


def create_tables(conn) -> None:
    """Create all database tables and indexes."""
    cursor = conn.cursor()
    cursor.execute(CREATE_ADDITIVES_TABLE)
    cursor.execute(CREATE_SOURCE_RECORDS_TABLE)
    cursor.execute(CREATE_SCHEMA_VERSION_TABLE)
    for index_sql in CREATE_INDEXES:
        cursor.execute(index_sql)
    cursor.execute(
        "INSERT OR IGNORE INTO schema_version (version) VALUES (?)",
        (SCHEMA_VERSION,),
    )
    conn.commit()
