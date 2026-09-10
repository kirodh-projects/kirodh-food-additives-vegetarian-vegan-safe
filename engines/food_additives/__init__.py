"""Food additives engine — vegan/vegetarian/halal/safety per E/INS number.

Self-contained: only depends on stdlib + pandas/requests/bs4/matplotlib/plotly.
Never imports from other engines, ``src``, or Streamlit.

Examples (run from repo root):
    python -m engines.food_additives.examples.example_lookup --code E120
    python -m engines.food_additives.examples.example_analytics --backend data
    python -m engines.food_additives.examples.example_analytics --backend png --out analytics.png
    python -m engines.food_additives.examples.example_analytics --backend plotly --out analytics.html --serve
"""

from .classifiers import classify_all
from .connection import ensure_database, get_connection, get_db_path
from .plots import (
    sanitise_key,
    save_matplotlib_dashboard,
    serve_html,
    write_plotly_dashboard,
)
from .queries import (
    get_all_additives,
    get_analytics_summary,
    get_category_vegan_breakdown,
    get_dangerous_additives,
    get_distinct_values,
    get_total_count,
    search_by_code,
    search_by_name,
)

__all__ = [
    "classify_all",
    "ensure_database",
    "get_connection",
    "get_db_path",
    "search_by_code",
    "search_by_name",
    "get_all_additives",
    "get_total_count",
    "get_analytics_summary",
    "get_category_vegan_breakdown",
    "get_dangerous_additives",
    "get_distinct_values",
    "sanitise_key",
    "save_matplotlib_dashboard",
    "write_plotly_dashboard",
    "serve_html",
]
