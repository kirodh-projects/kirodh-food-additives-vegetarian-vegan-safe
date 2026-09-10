"""Pluggable code engines — each subpackage works independently.

- :mod:`engines.food_additives` — vegan/vegetarian/halal/safety lookup per E/INS number
- :mod:`engines.species` — GBIF species search/browse + trait heuristics
- :mod:`engines.reverse_subtraction` — n - reverse(n) data + plots
- :mod:`engines.math_plotter` — parabolic axis transform data + plots

Engines never import from each other, from ``src``, or from Streamlit.
Each engine has its own ``config.py``, ``plots.py`` (data / PNG / plotly),
``README.md`` and runnable ``examples/``.
"""

__all__ = ["food_additives", "species", "reverse_subtraction", "math_plotter"]
