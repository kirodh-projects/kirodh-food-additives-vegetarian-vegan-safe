"""Math plotter engine — parabolic axis transform data + plots.

Self-contained: numpy/scipy + matplotlib/plotly only.
Never imports from other engines, ``src``, or Streamlit.

Examples (run from repo root):
    python -m engines.math_plotter.examples.example_transform --functions \"sin(x)\" --x-min -2 --x-max 2
    python -m engines.math_plotter.examples.example_plot_png --functions \"sin(x)\" \"cos(x)\" --out transform.png
    python -m engines.math_plotter.examples.example_plot_plotly --functions \"exp(-x^2)\" --out transform.html --serve
"""

from .engine import (
    FUNCTIONS,
    Axis,
    arc_length,
    compute_transformed_function,
    transform_point,
    x_from_signed_arc,
)
from .plots import save_matplotlib_png, serve_html, write_plotly_html

__all__ = [
    "FUNCTIONS",
    "arc_length",
    "x_from_signed_arc",
    "transform_point",
    "compute_transformed_function",
    "Axis",
    "save_matplotlib_png",
    "write_plotly_html",
    "serve_html",
]
