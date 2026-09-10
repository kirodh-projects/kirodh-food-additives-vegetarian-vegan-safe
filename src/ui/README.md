# UI Module (app shell)

Thin Streamlit routing layer. All domain logic lives in the domain
packages — this module only wires them together.

- `src.food_additives.ui` — Search / Analytics / Browse
- `src.species.ui` — Species Taxonomy tabs
- `src.numbers.ui` — Math Plotter / Reverse Subtraction
- `src.ui.app:main()` — sidebar routing between the three sections

## Layout

```text
src/ui/
├── README.md  # this file
└── app.py     # main() — page config, sidebar, section routing
```

## Run

```bash
streamlit run app.py
# app.py at the repo root calls src.ui.app:main()
```

`main()` ensures the food-additives DB exists, then shows a sidebar to
pick **Food Additives** / **Species Taxonomy** / **Tools** and delegates
to the domain `render_*` functions. No SQL or classification logic here.

## Backward compatibility

The old `src.ui.pages.*` and `src.ui.components.*` import paths still
work as thin re-export shims, but new code should import from the
domain packages, e.g.:

```python
from src.food_additives.ui.search import render_search_page
from src.species.ui.species_page import render_species_page
from src.numbers.ui.math_plotter_page import render_math_plotter_page
```
