"""Heuristic trait scoring for species: mobility, warm-bloodedness, and size.

Each score is a probability from 0.0 to 1.0 assigned based on taxonomic
classification (kingdom > phylum > class > order), using the most specific
match available.

Scores represent *typical* values for the taxonomic group, not individual
organisms.  They are statistical heuristics, not measurements.
"""

import logging
from src.db.species_connection import get_species_connection, list_species_db_files

logger = logging.getLogger(__name__)

# ── Mobility (0 = sessile, 1 = highly mobile) ──────────────────────────

MOBILITY_BY_ORDER: dict[str, float] = {
    # Fish orders (Chordata with empty class_name)
    "Perciformes": 0.75, "Cypriniformes": 0.70, "Siluriformes": 0.65,
    "Characiformes": 0.70, "Cyprinodontiformes": 0.60, "Scorpaeniformes": 0.60,
    "Anguilliformes": 0.70, "Tetraodontiformes": 0.55, "Pleuronectiformes": 0.45,
    "Clupeiformes": 0.80, "Gadiformes": 0.70, "Salmoniformes": 0.85,
    "Beloniformes": 0.75, "Syngnathiformes": 0.30, "Lophiiformes": 0.25,
    "Myctophiformes": 0.65, "Osteoglossiformes": 0.60, "Ophidiiformes": 0.50,
    "Rajiformes": 0.55, "Carcharhiniformes": 0.85, "Lamniformes": 0.90,
    "Squaliformes": 0.70,
    # Sessile / low-mobility orders
    "Sessilia": 0.01, "Pedunculata": 0.01,  # barnacles
}

MOBILITY_BY_CLASS: dict[str, float] = {
    # Mammals & birds
    "Mammalia": 0.85, "Aves": 0.95,
    # Reptiles & amphibians
    "Amphibia": 0.65, "Squamata": 0.60, "Testudines": 0.25,
    "Crocodylia": 0.45, "Sphenodontia": 0.40,
    # Fish
    "Elasmobranchii": 0.80, "Holocephali": 0.60,
    "Petromyzonti": 0.50, "Dipneusti": 0.35, "Coelacanthi": 0.40,
    "Myxini": 0.40, "Leptocardii": 0.30,
    # Tunicates
    "Ascidiacea": 0.03, "Thaliacea": 0.25,
    # Arthropods
    "Insecta": 0.75, "Arachnida": 0.55, "Malacostraca": 0.60,
    "Copepoda": 0.45, "Diplopoda": 0.35, "Chilopoda": 0.50,
    "Collembola": 0.45, "Ostracoda": 0.30, "Trilobita": 0.40,
    "Branchiopoda": 0.40, "Merostomata": 0.35, "Pycnogonida": 0.25,
    "Maxillopoda": 0.30, "Remipedia": 0.45, "Cephalocarida": 0.30,
    "Pauropoda": 0.30, "Symphyla": 0.35,
    # Mollusks
    "Gastropoda": 0.20, "Bivalvia": 0.05, "Cephalopoda": 0.80,
    "Scaphopoda": 0.05, "Polyplacophora": 0.10, "Monoplacophora": 0.05,
    # Annelids
    "Polychaeta": 0.30, "Clitellata": 0.25,
    # Nematodes
    "Chromadorea": 0.20, "Enoplea": 0.20,
    # Cnidaria
    "Anthozoa": 0.02, "Hydrozoa": 0.15, "Scyphozoa": 0.30, "Cubozoa": 0.35,
    # Sponges
    "Demospongiae": 0.01, "Calcarea": 0.01, "Hexactinellida": 0.01,
    # Echinoderms
    "Echinoidea": 0.15, "Asteroidea": 0.15, "Holothuroidea": 0.10,
    "Ophiuroidea": 0.20, "Crinoidea": 0.05,
    # Flatworms
    "Trematoda": 0.25, "Cestoda": 0.05, "Turbellaria": 0.30,
    # Bryozoa
    "Gymnolaemata": 0.01, "Stenolaemata": 0.01, "Phylactolaemata": 0.01,
    # Brachiopods
    "Rhynchonellata": 0.02, "Lingulata": 0.02, "Craniata": 0.01,
    # Rotifers
    "Eurotatoria": 0.30, "Bdelloidea": 0.25,
    # Fungi classes
    "Agaricomycetes": 0.0, "Dothideomycetes": 0.0, "Lecanoromycetes": 0.0,
    "Sordariomycetes": 0.0, "Leotiomycetes": 0.0, "Eurotiomycetes": 0.0,
    "Pezizomycetes": 0.0, "Pucciniomycetes": 0.0, "Ustilaginomycetes": 0.0,
    "Tremellomycetes": 0.0, "Dacrymycetes": 0.0, "Exobasidiomycetes": 0.0,
    # Plant classes
    "Magnoliopsida": 0.0, "Liliopsida": 0.0, "Polypodiopsida": 0.0,
    "Pinopsida": 0.0, "Bryopsida": 0.0, "Lycopodiopsida": 0.0,
    "Jungermanniopsida": 0.0, "Marchantiopsida": 0.0, "Gnetopsida": 0.0,
    "Cycadopsida": 0.0, "Anthocerotopsida": 0.0, "Sphagnopsida": 0.0,
    # Chromista
    "Bacillariophyceae": 0.10, "Phaeophyceae": 0.0,
    "Chrysophyceae": 0.15, "Dinophyceae": 0.30,
    "Globothalamea": 0.10, "Tubothalamea": 0.05,
    # Protozoa
    "Oligohymenophorea": 0.50, "Spirotrichea": 0.50,
    "Litostomatea": 0.45, "Lobosa": 0.30,
}

MOBILITY_BY_PHYLUM: dict[str, float] = {
    "Chordata": 0.70, "Arthropoda": 0.55, "Mollusca": 0.25,
    "Annelida": 0.28, "Cnidaria": 0.10, "Nematoda": 0.20,
    "Platyhelminthes": 0.20, "Porifera": 0.01, "Echinodermata": 0.15,
    "Bryozoa": 0.01, "Brachiopoda": 0.02, "Ctenophora": 0.35,
    "Rotifera": 0.28, "Tardigrada": 0.20, "Hemichordata": 0.10,
    "Chaetognatha": 0.40, "Nemertea": 0.25, "Sipuncula": 0.10,
    "Acanthocephala": 0.05, "Onychophora": 0.30,
    "Tracheophyta": 0.0, "Bryophyta": 0.0, "Marchantiophyta": 0.0,
    "Rhodophyta": 0.0, "Chlorophyta": 0.05, "Charophyta": 0.0,
    "Anthocerotophyta": 0.0,
    "Ascomycota": 0.0, "Basidiomycota": 0.0, "Zygomycota": 0.0,
    "Glomeromycota": 0.0, "Chytridiomycota": 0.10,
    "Ochrophyta": 0.05, "Foraminifera": 0.08, "Ciliophora": 0.45,
    "Myzozoa": 0.30, "Haptophyta": 0.15,
    "Proteobacteria": 0.30, "Firmicutes": 0.20, "Actinobacteria": 0.10,
    "Cyanobacteria": 0.10, "Bacteroidetes": 0.15,
    "Euryarchaeota": 0.15, "Crenarchaeota": 0.10,
}

MOBILITY_BY_KINGDOM: dict[str, float] = {
    "Animalia": 0.45, "Plantae": 0.0, "Fungi": 0.0,
    "Chromista": 0.08, "Bacteria": 0.20, "Archaea": 0.12,
    "Protozoa": 0.40, "Viruses": 0.0, "incertae sedis": 0.10,
}


# ── Warm-bloodedness / endothermy (0 = ectotherm, 1 = full endotherm) ──

WARM_BLOOD_BY_ORDER: dict[str, float] = {
    # Some fish with regional endothermy
    "Lamniformes": 0.25, "Scombriformes": 0.15,
    # Leatherback turtles
    "Testudines": 0.10,
    # Large flying insects generate significant heat
    "Hymenoptera": 0.08, "Lepidoptera": 0.05, "Coleoptera": 0.03,
}

WARM_BLOOD_BY_CLASS: dict[str, float] = {
    "Mammalia": 0.95, "Aves": 0.95,
    # Slight endothermy
    "Elasmobranchii": 0.08, "Cephalopoda": 0.05,
    "Insecta": 0.03, "Squamata": 0.02,
}

WARM_BLOOD_BY_PHYLUM: dict[str, float] = {
    "Chordata": 0.05,
}

WARM_BLOOD_BY_KINGDOM: dict[str, float] = {
    "Animalia": 0.02, "Plantae": 0.0, "Fungi": 0.0,
    "Chromista": 0.0, "Bacteria": 0.0, "Archaea": 0.0,
    "Protozoa": 0.0, "Viruses": 0.0, "incertae sedis": 0.0,
}


# ── Body size (0 = microscopic, 1 = largest known organisms) ───────────
# Logarithmic scale: 0.0 ~= virus (100nm), 0.5 ~= medium mammal (1m),
# 1.0 ~= blue whale (30m) / giant sequoia

SIZE_BY_ORDER: dict[str, float] = {
    # Large mammals
    "Cetacea": 0.85, "Proboscidea": 0.82, "Perissodactyla": 0.72,
    "Artiodactyla": 0.68, "Carnivora": 0.60, "Sirenia": 0.70,
    # Small mammals
    "Rodentia": 0.30, "Chiroptera": 0.25, "Eulipotyphla": 0.22,
    "Lagomorpha": 0.30,
    # Primates
    "Primates": 0.48,
    # Large reptile orders
    "Crocodylia": 0.60,
    # Large birds
    "Struthioniformes": 0.50, "Casuariiformes": 0.48,
    # Large fish orders
    "Lamniformes": 0.65, "Orectolobiformes": 0.60,
    # Very small arthropods
    "Acari": 0.06,
}

SIZE_BY_CLASS: dict[str, float] = {
    # Mammals & birds
    "Mammalia": 0.50, "Aves": 0.35,
    # Reptiles & amphibians
    "Amphibia": 0.22, "Squamata": 0.28, "Testudines": 0.40,
    "Crocodylia": 0.60, "Sphenodontia": 0.32,
    # Fish
    "Elasmobranchii": 0.50, "Holocephali": 0.40,
    "Petromyzonti": 0.30, "Dipneusti": 0.38, "Coelacanthi": 0.45,
    "Myxini": 0.28, "Leptocardii": 0.15,
    # Tunicates
    "Ascidiacea": 0.15, "Thaliacea": 0.12,
    # Arthropods
    "Insecta": 0.12, "Arachnida": 0.10, "Malacostraca": 0.20,
    "Copepoda": 0.06, "Diplopoda": 0.14, "Chilopoda": 0.14,
    "Collembola": 0.06, "Ostracoda": 0.05, "Trilobita": 0.15,
    "Branchiopoda": 0.06, "Merostomata": 0.25, "Pycnogonida": 0.10,
    "Maxillopoda": 0.06, "Pauropoda": 0.04, "Symphyla": 0.05,
    # Mollusks
    "Gastropoda": 0.14, "Bivalvia": 0.16, "Cephalopoda": 0.35,
    "Scaphopoda": 0.10, "Polyplacophora": 0.12, "Monoplacophora": 0.08,
    # Annelids
    "Polychaeta": 0.14, "Clitellata": 0.14,
    # Nematodes
    "Chromadorea": 0.06, "Enoplea": 0.06,
    # Cnidaria
    "Anthozoa": 0.15, "Hydrozoa": 0.08, "Scyphozoa": 0.25, "Cubozoa": 0.18,
    # Sponges
    "Demospongiae": 0.18, "Calcarea": 0.10, "Hexactinellida": 0.20,
    # Echinoderms
    "Echinoidea": 0.16, "Asteroidea": 0.20, "Holothuroidea": 0.22,
    "Ophiuroidea": 0.14, "Crinoidea": 0.18,
    # Flatworms
    "Trematoda": 0.06, "Cestoda": 0.12, "Turbellaria": 0.06,
    # Bryozoa
    "Gymnolaemata": 0.04, "Stenolaemata": 0.04, "Phylactolaemata": 0.05,
    # Brachiopods
    "Rhynchonellata": 0.10, "Lingulata": 0.08, "Craniata": 0.06,
    # Rotifers
    "Eurotatoria": 0.04, "Bdelloidea": 0.03,
    # Fungi
    "Agaricomycetes": 0.14, "Dothideomycetes": 0.06, "Lecanoromycetes": 0.08,
    "Sordariomycetes": 0.06, "Leotiomycetes": 0.06, "Eurotiomycetes": 0.05,
    "Pezizomycetes": 0.08, "Pucciniomycetes": 0.04, "Ustilaginomycetes": 0.04,
    "Tremellomycetes": 0.06, "Dacrymycetes": 0.06, "Exobasidiomycetes": 0.04,
    # Plants
    "Magnoliopsida": 0.38, "Liliopsida": 0.30, "Polypodiopsida": 0.25,
    "Pinopsida": 0.65, "Bryopsida": 0.05, "Lycopodiopsida": 0.15,
    "Jungermanniopsida": 0.04, "Marchantiopsida": 0.04, "Gnetopsida": 0.30,
    "Cycadopsida": 0.45, "Anthocerotopsida": 0.04, "Sphagnopsida": 0.05,
    # Chromista
    "Bacillariophyceae": 0.04, "Phaeophyceae": 0.30,
    "Chrysophyceae": 0.03, "Dinophyceae": 0.03,
    "Globothalamea": 0.04, "Tubothalamea": 0.04,
    # Protozoa
    "Oligohymenophorea": 0.04, "Spirotrichea": 0.04,
    "Litostomatea": 0.04, "Lobosa": 0.05,
}

SIZE_BY_PHYLUM: dict[str, float] = {
    "Chordata": 0.40, "Arthropoda": 0.12, "Mollusca": 0.16,
    "Annelida": 0.14, "Cnidaria": 0.14, "Nematoda": 0.06,
    "Platyhelminthes": 0.06, "Porifera": 0.16, "Echinodermata": 0.18,
    "Bryozoa": 0.04, "Brachiopoda": 0.08, "Ctenophora": 0.12,
    "Rotifera": 0.04, "Tardigrada": 0.04, "Hemichordata": 0.12,
    "Chaetognatha": 0.10, "Nemertea": 0.14, "Sipuncula": 0.10,
    "Acanthocephala": 0.06, "Onychophora": 0.12,
    "Tracheophyta": 0.38, "Bryophyta": 0.05, "Marchantiophyta": 0.04,
    "Rhodophyta": 0.15, "Chlorophyta": 0.08, "Charophyta": 0.10,
    "Anthocerotophyta": 0.04,
    "Ascomycota": 0.06, "Basidiomycota": 0.12, "Zygomycota": 0.04,
    "Glomeromycota": 0.04, "Chytridiomycota": 0.03,
    "Ochrophyta": 0.10, "Foraminifera": 0.04, "Ciliophora": 0.04,
    "Myzozoa": 0.03, "Haptophyta": 0.03,
    "Proteobacteria": 0.02, "Firmicutes": 0.02, "Actinobacteria": 0.02,
    "Cyanobacteria": 0.03, "Bacteroidetes": 0.02,
    "Euryarchaeota": 0.02, "Crenarchaeota": 0.02,
}

SIZE_BY_KINGDOM: dict[str, float] = {
    "Animalia": 0.22, "Plantae": 0.30, "Fungi": 0.10,
    "Chromista": 0.06, "Bacteria": 0.02, "Archaea": 0.02,
    "Protozoa": 0.04, "Viruses": 0.01, "incertae sedis": 0.10,
}


# ── Resolution helpers ──────────────────────────────────────────────────

def _resolve(
    kingdom: str, phylum: str, class_name: str, order_name: str,
    by_order: dict[str, float],
    by_class: dict[str, float],
    by_phylum: dict[str, float],
    by_kingdom: dict[str, float],
    default: float = 0.5,
) -> float:
    """Return the most-specific matching score."""
    if order_name and order_name in by_order:
        return by_order[order_name]
    if class_name and class_name in by_class:
        return by_class[class_name]
    if phylum and phylum in by_phylum:
        return by_phylum[phylum]
    if kingdom and kingdom in by_kingdom:
        return by_kingdom[kingdom]
    return default


def compute_mobility(kingdom: str, phylum: str, class_name: str, order_name: str) -> float:
    return _resolve(kingdom, phylum, class_name, order_name,
                    MOBILITY_BY_ORDER, MOBILITY_BY_CLASS,
                    MOBILITY_BY_PHYLUM, MOBILITY_BY_KINGDOM, 0.25)


def compute_warm_blood(kingdom: str, phylum: str, class_name: str, order_name: str) -> float:
    return _resolve(kingdom, phylum, class_name, order_name,
                    WARM_BLOOD_BY_ORDER, WARM_BLOOD_BY_CLASS,
                    WARM_BLOOD_BY_PHYLUM, WARM_BLOOD_BY_KINGDOM, 0.0)


def compute_size(kingdom: str, phylum: str, class_name: str, order_name: str) -> float:
    return _resolve(kingdom, phylum, class_name, order_name,
                    SIZE_BY_ORDER, SIZE_BY_CLASS,
                    SIZE_BY_PHYLUM, SIZE_BY_KINGDOM, 0.10)


# ── SQL generation for bulk UPDATE ──────────────────────────────────────

def _build_case_sql(
    by_order: dict[str, float],
    by_class: dict[str, float],
    by_phylum: dict[str, float],
    by_kingdom: dict[str, float],
    default: float,
) -> str:
    """Build a CASE expression that resolves order > class > phylum > kingdom."""
    parts = []
    for name, val in by_order.items():
        parts.append(f"WHEN order_name = '{name}' THEN {val}")
    for name, val in by_class.items():
        parts.append(f"WHEN class_name = '{name}' THEN {val}")
    for name, val in by_phylum.items():
        parts.append(f"WHEN phylum = '{name}' THEN {val}")
    for name, val in by_kingdom.items():
        parts.append(f"WHEN kingdom = '{name}' THEN {val}")
    case_body = "\n        ".join(parts)
    return f"""CASE
        {case_body}
        ELSE {default}
    END"""


def build_trait_update_sql() -> str:
    """Build a single UPDATE statement that sets all three trait columns."""
    mobility_case = _build_case_sql(
        MOBILITY_BY_ORDER, MOBILITY_BY_CLASS,
        MOBILITY_BY_PHYLUM, MOBILITY_BY_KINGDOM, 0.25,
    )
    warm_blood_case = _build_case_sql(
        WARM_BLOOD_BY_ORDER, WARM_BLOOD_BY_CLASS,
        WARM_BLOOD_BY_PHYLUM, WARM_BLOOD_BY_KINGDOM, 0.0,
    )
    size_case = _build_case_sql(
        SIZE_BY_ORDER, SIZE_BY_CLASS,
        SIZE_BY_PHYLUM, SIZE_BY_KINGDOM, 0.10,
    )
    return f"""UPDATE species SET
    mobility_score = {mobility_case},
    warm_blood_score = {warm_blood_case},
    size_score = {size_case}
"""


# ── Migration: add columns + populate ───────────────────────────────────

def migrate_species_traits(db_dir: str | None = None) -> int:
    """Add trait columns to all species DB files and populate them."""
    import sqlite3
    db_files = list_species_db_files(db_dir)
    if not db_files:
        logger.warning("No species DB files found.")
        return 0

    update_sql = build_trait_update_sql()
    total_updated = 0

    for i, db_path in enumerate(db_files, 1):
        logger.info("  [%d/%d] Migrating %s ...", i, len(db_files), db_path)

        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=OFF")

        # Add columns if they don't exist
        existing_cols = {row[1] for row in conn.execute("PRAGMA table_info(species)")}
        for col in ("mobility_score", "warm_blood_score", "size_score"):
            if col not in existing_cols:
                conn.execute(f"ALTER TABLE species ADD COLUMN {col} REAL DEFAULT 0.0")

        # Populate
        cursor = conn.execute(update_sql)
        updated = cursor.rowcount
        total_updated += updated

        conn.commit()
        conn.close()
        logger.info("    Updated %d rows", updated)

    logger.info("Trait migration complete. %d rows updated across %d files.",
                total_updated, len(db_files))

    # Build precomputed stats cache for fast UI loading
    logger.info("Building stats cache...")
    from src.db.species_queries import build_stats_cache
    build_stats_cache(db_dir)

    return total_updated
