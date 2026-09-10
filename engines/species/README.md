# Species engine

Independent GBIF Backbone Taxonomy search/browse + heuristic physical- and
guna-trait scores. No Streamlit, no other engines.

## Files

| File | Purpose |
|---|---|
| `config.py` | `SPECIES_DB_DIR` (vendored, self-contained) |
| `schema.py` | `CREATE TABLE species` + indexes |
| `connection.py` | Multi-file (`species_*.db`) connection manager |
| `queries.py` | `search_species`, `browse_species`, stats (+ JSON cache) |
| `traits.py` | Heuristic mobility / warm-blood / size + guna scores |
| `build_database.py` | GBIF download + two-pass ETL + trait migration |
| `plots.py` | **data / PNG / plotly** (incl. ternary) + local server |

## Use as a library

```python
from engines.species.queries import search_species, browse_species, get_species_stats
from engines.species.traits import compute_mobility, compute_gunas

print(search_species("Panthera leo", limit=2))
print(browse_species(filters={"kingdom": ["Plantae"]}, limit=5))
print(get_species_stats()["total"])
print(compute_mobility("Animalia", "Chordata", "Mammalia", "Carnivora"))
print(compute_gunas("Plantae", "Tracheophyta", "Magnoliopsida", ""))
```

## Build the database

```bash
python -m engines.species.build_database
python -m engines.species.build_database --force
python -m engines.species.build_database --db-dir ./databases
```

Output: `species_001.db … species_NNN.db` (~45 MB each) plus
`species_stats_cache.json` in `$SPECIES_DB_DIR`.

## Examples (inside this module)

```bash
python -m engines.species.examples.example_search --query \"Panthera leo\" --limit 10
python -m engines.species.examples.example_traits --kingdom Animalia --phylum Chordata --class Mammalia --order Carnivora
python -m engines.species.examples.example_stats --backend data
python -m engines.species.examples.example_stats --backend png --out species.png
python -m engines.species.examples.example_stats --backend plotly --out species.html --serve
```
