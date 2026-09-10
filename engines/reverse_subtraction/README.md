# Reverse subtraction engine

Independent `n - reverse(n)` number exploration. No Streamlit, no other engines.

## Files

| File | Purpose |
|---|---|
| `engine.py` | `reverse_number`, `compute_reverse_subtraction`, `compute_stats` (pure) |
| `plots.py` | **data / PNG / plotly** builders + local server |
| `examples/` | Runnable scripts (see below) |

## Use as a library

```python
from engines.reverse_subtraction import reverse_number, compute_reverse_subtraction, compute_stats

assert reverse_number(21) == 12
xs, ys = compute_reverse_subtraction(1, 200)
print(compute_stats(xs, ys))  # zeros, max, min, mean
```

## Examples (inside this module)

```bash
python -m engines.reverse_subtraction.examples.example_basic --start 1 --end 200
python -m engines.reverse_subtraction.examples.example_plot_png --start 1 --end 200 --out reverse.png
python -m engines.reverse_subtraction.examples.example_plot_plotly --start 1 --end 200 --out reverse.html --serve
```
