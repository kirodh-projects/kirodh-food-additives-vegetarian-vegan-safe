# Species Module

Browse and search all ~5.9 million known species (including extinct)
from the GBIF Backbone Taxonomy, with full taxonomic hierarchy plus
heuristic physical- and guna-trait scores.

Self-contained domain package: database, ETL, traits, UI, and tests.
Only depends on `src.shared` for config.

## Layout

```text
src/species/
├── README.md              # this file
├── __init__.py            # public API (connection helpers)
├── schema.py              # CREATE TABLE species + db_meta, indexes
├── connection.py          # multi-file connection manager, shard listing
├── queries.py             # search / browse / stats across all shards (+ JSON cache)
├── traits.py              # heuristic mobility / warm-blood / size + guna scores
├── build_database.py      # GBIF download + two-pass ETL + trait migration
└── ui/
    └── species_page.py    # Search / Browse / Physical Traits / Gunas / Statistics tabs
```

## Quick start

```bash
# Build (downloads ~490 MB GBIF backbone once, then caches it)
python -m src.species.build_database

# Force re-download + rebuild
python -m src.species.build_database --force

# Custom directory
python -m src.species.build_database --db-dir ./databases
```

Output: `species_001.db … species_046.db` (~45 MB each) plus
`species_stats_cache.json` in `$SPECIES_DB_DIR` (default `./databases`).

## Code examples

```python
from src.species.queries import search_species, browse_species, get_species_stats

print(search_species("Panthera leo")[:2])
print(browse_species(filters={"kingdom": ["Plantae"]}, limit=5))
print(get_species_stats()["total"])  # ~5_884_673
```

```python
from src.species.traits import compute_mobility, compute_gunas

print(compute_mobility("Animalia", "Chordata", "Mammalia", "Carnivora"))  # 0.68-ish
print(compute_gunas("Plantae", "Tracheophyta", "Magnoliopsida", ""))
# (sattva, rajas, tamas) with sum ≈ 1.0
```

## How the build works (two passes + traits)

1. **Pass 1** — stream the ~7.7 M-row GBIF file, build an in-memory
   `taxon_id -> name` map for higher taxa (kingdom → genus). Needed
   because the file stores hierarchy as numeric IDs.
2. **Pass 2** — stream again, keep only `species / subspecies / variety /
   form` ranks, resolve hierarchy IDs to names, insert in batches of
   10,000, rotating to a new SQLite file at ~45 MB.
3. **Pass 3** — `traits.migrate_species_traits()`: add the six trait
   columns via a single `UPDATE … CASE` per file, then rebuild the
   stats cache via `queries.build_stats_cache()`.

## Database schema

Each shard has a `species` table:

| Column | Description |
|---|---|
| `taxon_id` | GBIF taxon identifier |
| `scientific_name` / `canonical_name` / `authorship` | names |
| `kingdom`, `phylum`, `class_name`, `order_name`, `family`, `genus` | hierarchy |
| `specific_epithet`, `infraspecific_epithet` | epithets |
| `taxon_rank` | species, subspecies, variety, form |
| `taxonomic_status`, `accepted_taxon_id` | synonym handling |
| `mobility_score`, `warm_blood_score`, `size_score` | physical heuristics 0–1 |
| `purity_score`, `passion_score`, `ignorance_score` | guna heuristics, sum ≈ 1 |

Indexes on `taxon_id`, `scientific_name`, `canonical_name`,
`kingdom`, `family`, `genus`, `taxon_rank`, `taxonomic_status`.

`queries` reads through a `species_stats_cache.json` file
(`stats` + `distribution` + `distinct`) so the dashboard loads fast.

## Trait methodology

Scores are *typical values for the taxonomic group*, not measurements,
resolved most-specific-first: order → class → phylum → kingdom.
Examples: Mammalia → mobility 0.85, warm-blood 0.95; Plantae → mobility 0.

Gunas (Vedic): sattva (purity) + rajas (passion) + tamas (ignorance) ≈ 1.
Plants skew sattvic, predators rajasic, decomposers/parasites tamasic.
See `traits.py` docstring for the full rationale.

## Environment

| Variable         | Default       | Description                  |
|------------------|---------------|------------------------------|
| `SPECIES_DB_DIR` | `./databases` | Shard + cache directory      |

## Tests

```bash
pytest tests/species/ -v
# traits (pure functions) + species queries across temp shards
```
