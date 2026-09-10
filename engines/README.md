# Engines

Four independent, UI-free code engines. Copy any one folder into another
project and it works — no cross-engine imports, no `src` imports, no Streamlit.

| Engine | Folder | Run examples |
|---|---|---|
| Food additives (vegan/vegetarian per E/INS) | `engines/food_additives/` | `python -m engines.food_additives.examples.example_lookup --code E120` |
| Species taxonomy | `engines/species/` | `python -m engines.species.examples.example_search --query \"Panthera leo\"` |
| Reverse subtraction `n - reverse(n)` | `engines/reverse_subtraction/` | `python -m engines.reverse_subtraction.examples.example_basic --start 1 --end 200` |
| Math plotter (parabolic transform) | `engines/math_plotter/` | `python -m engines.math_plotter.examples.example_transform --functions \"sin(x)\" --out out.png` |

Each engine offers three output modes:

1. **data** — pure Python dicts/lists (no plotting deps beyond the engine core).
2. **png** — static Matplotlib PNG via `plots.py` (`Agg` backend, no display needed).
3. **plotly** — interactive Plotly HTML file + optional local HTTP server
   (`plots.py`: `write_plotly_html(...)` + `serve_html(...)`).

Streamlit UI is kept separately under `src/*/ui/` and `src/ui/` — it consumes
data but is never imported by engines.
