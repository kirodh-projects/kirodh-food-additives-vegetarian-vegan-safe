"""Reverse-subtraction engine — ``n - reverse(n)`` data + plots.

Self-contained: stdlib + matplotlib/plotly/numpy only.
Never imports from other engines, ``src``, or Streamlit.

Examples (run from repo root):
    python -m engines.reverse_subtraction.examples.example_basic --start 1 --end 200
    python -m engines.reverse_subtraction.examples.example_plot_png --start 1 --end 200 --out reverse.png
    python -m engines.reverse_subtraction.examples.example_plot_plotly --start 1 --end 200 --out reverse.html --serve
"""

from .engine import compute_reverse_subtraction, compute_stats, reverse_number
from .plots import save_matplotlib_png, serve_html, write_plotly_html

__all__ = [
    "reverse_number",
    "compute_reverse_subtraction",
    "compute_stats",
    "save_matplotlib_png",
    "write_plotly_html",
    "serve_html",
]
