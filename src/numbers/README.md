# Numbers Module

Fun number explorations: reverse subtraction and parabolic axis transforms.

Design rule: **pure logic is UI-free** so it can be unit-tested and reused
in scripts; Streamlit pages are thin visualisation wrappers.

## Layout

```text
src/numbers/
├── README.md                  # this file
├── __init__.py                # re-exports core functions
├── reverse_subtraction.py     # reverse_number(), compute_reverse_subtraction()
├── parabolic_transform.py     # arc_length(), x_from_signed_arc(),
│                              # transform_point(), compute_transformed_function(),
│                              # FUNCTIONS presets, Axis (matplotlib, legacy)
└── ui/
    ├── reverse_subtract_page.py  # Streamlit page for n - reverse(n)
    └── math_plotter_page.py      # Streamlit page for parabolic transform
```

## Quick start

No build step, no database, no downloads.

```bash
# Run the full app and open Tools -> Math Plotter / Reverse Subtraction
streamlit run app.py

# Or use the logic directly in Python (see below)
```

## Code examples

### Reverse subtraction: `n - reverse(n)`

```python
from src.numbers.reverse_subtraction import reverse_number, compute_reverse_subtraction

assert reverse_number(21) == 12
assert reverse_number(100) == 1
assert reverse_number(-21) == -12

xs, ys = compute_reverse_subtraction(1, 200)
# ys[i] == xs[i] - reverse_number(xs[i])
# zeros mark digit-palindromes, e.g. 1-9, 11, 22, ...
```

### Parabolic transform: wrap a function onto `y = x^2`

```python
from src.numbers.parabolic_transform import (
    FUNCTIONS, arc_length, compute_transformed_function,
)

print(arc_length(1.0))  # signed arc length from vertex to x=1

new_x, new_y, skipped = compute_transformed_function(
    FUNCTIONS["sin(x)"], x_min=-2.0, x_max=2.0, n_points=500
)
# new_x/new_y are plottable; skipped holds out-of-range inputs
```

### Legacy matplotlib script

```python
from src.numbers.parabolic_transform import Axis

Axis(-2, 2).render("transformed_exact.png")
# `python math_plotter.py` at the repo root still works — it is a thin wrapper.
```

## How it works

### Reverse subtraction

For each integer `n`, reverse its decimal digits (preserving sign) and
plot `n - reverse(n)`. Multiples of 9 dominate; zeros appear at
palindromes and repdigits.

### Parabolic axis transformation

1. The parabola `y = x^2` is the curved axis.
2. Each `f(x)` value is treated as a **signed arc-length** from the vertex.
3. The arc-length integral is inverted (bisection) to find the point on
   the parabola, then the original `x` is projected along the
   **perpendicular** at that point.
4. Outputs outside the parabola's arc-length range can't be plotted and
   are shown as orange stars.

10 presets: `exp(-x^2)`, `2^x`, `x^2`, `sin(x)`, `cos(x)`, `x`, `-5x`,
`x^3`, `1/(1+x^2)`, `tanh(x)`.

## Tests

```bash
pytest tests/numbers/ -v
# reverse_number edge cases, arc-length symmetry/roundtrip,
# transform_point, preset functions
```
