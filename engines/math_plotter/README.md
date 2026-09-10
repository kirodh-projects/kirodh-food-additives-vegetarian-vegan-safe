# Math plotter engine

Independent parabolic axis transformation: wrap any preset function onto the
parabola `y = x²` via signed arc-length. No Streamlit, no other engines.

## Files

| File | Purpose |
|---|---|
| `engine.py` | `arc_length`, `x_from_signed_arc`, `transform_point`, `compute_transformed_function`, `FUNCTIONS`, `Axis` (pure) |
| `plots.py` | **data / PNG / plotly** builders + local server |
| `examples/` | Runnable scripts (see below) |

Presets (10): `exp(-x^2)`, `2^x`, `x^2`, `sin(x)`, `cos(x)`, `x`, `-5x`,
`x^3`, `1/(1+x^2)`, `tanh(x)`.

## How it works

1. The parabola `y = x²` is the curved axis.
2. Each `f(x)` value is treated as a signed arc-length from the vertex.
3. The arc-length integral is inverted (bisection) to find the point on the
   parabola, then the original `x` is projected along the perpendicular.
4. Outputs outside the parabola's arc-length range can't be plotted and are
   reported as `skipped` (orange stars in plots).

## Use as a library

```python
from engines.math_plotter import FUNCTIONS, compute_transformed_function

new_x, new_y, skipped = compute_transformed_function(FUNCTIONS["sin(x)"], -2.0, 2.0, 500)
```

## Examples (inside this module)

```bash
python -m engines.math_plotter.examples.example_transform --functions \"sin(x)\" --x-min -2 --x-max 2
python -m engines.math_plotter.examples.example_plot_png --functions \"sin(x)\" \"cos(x)\" --out transform.png
python -m engines.math_plotter.examples.example_plot_plotly --functions \"exp(-x^2)\" --out transform.html --serve
```
