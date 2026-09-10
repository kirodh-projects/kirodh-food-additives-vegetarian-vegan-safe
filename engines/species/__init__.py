"""Species engine — GBIF taxonomy search/browse + trait heuristics.

Self-contained: only depends on stdlib + requests/matplotlib/plotly.
Never imports from other engines, ``src``, or Streamlit.

Examples (run from repo root):
    python -m engines.species.examples.example_search --query \"Panthera leo\"
    python -m engines.species.examples.example_traits --kingdom Animalia --phylum Chordata --class Mammalia --order Carnivora
    python -m engines.species.examples.example_stats --backend data
"""

from .connection import (
    ensure_species_db,
    get_species_connection,
    get_species_db_dir,
    list_species_db_files,
)
from .plots import (
    build_plotly_figures,
    save_matplotlib_dashboard,
    serve_html,
    write_plotly_dashboard,
)
from .queries import (
    browse_species,
    build_stats_cache,
    get_species_distinct_values,
    get_species_stats,
    get_species_total_count,
    get_trait_distribution,
    search_species,
)
from .traits import compute_gunas, compute_mobility, compute_size, compute_warm_blood

__all__ = [
    "ensure_species_db",
    "get_species_connection",
    "get_species_db_dir",
    "list_species_db_files",
    "search_species",
    "browse_species",
    "get_species_total_count",
    "get_species_stats",
    "get_trait_distribution",
    "get_species_distinct_values",
    "build_stats_cache",
    "compute_mobility",
    "compute_warm_blood",
    "compute_size",
    "compute_gunas",
    "build_plotly_figures",
    "save_matplotlib_dashboard",
    "write_plotly_dashboard",
    "serve_html",
]
