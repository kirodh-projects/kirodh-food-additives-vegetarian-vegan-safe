"""Numbers / math tools domain package.

Pure, UI-free number logic lives here:

- :mod:`src.numbers.reverse_subtraction` — ``n - reverse(n)`` computation.
- :mod:`src.numbers.parabolic_transform` — parabolic axis transformation
  (arc length, perpendicular projection, preset functions, ``Axis`` class).

Streamlit pages that visualise the above live in :mod:`src.numbers.ui`:

- :mod:`src.numbers.ui.reverse_subtract_page`
- :mod:`src.numbers.ui.math_plotter_page`

The pure functions are intentionally Streamlit-free so they can be
unit-tested and reused in scripts.
"""

from src.numbers.parabolic_transform import (
    FUNCTIONS,
    arc_length,
    compute_transformed_function,
    transform_point,
    x_from_signed_arc,
)
from src.numbers.reverse_subtraction import compute_reverse_subtraction, reverse_number

__all__ = [
    "FUNCTIONS",
    "arc_length",
    "x_from_signed_arc",
    "transform_point",
    "compute_transformed_function",
    "reverse_number",
    "compute_reverse_subtraction",
]
