"""Plotly backend: write interactive HTML + optionally serve locally.

Run:
    python -m engines.math_plotter.examples.example_plot_plotly --functions \"exp(-x^2)\" --out transform.html
    python -m engines.math_plotter.examples.example_plot_plotly --functions \"sin(x)\" \"cos(x)\" --out transform.html --serve
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parabolic transform Plotly plot.")
    parser.add_argument("--functions", nargs="*", default=["exp(-x^2)"])
    parser.add_argument("--x-min", type=float, default=-2.0)
    parser.add_argument("--x-max", type=float, default=2.0)
    parser.add_argument("--n-points", type=int, default=500)
    parser.add_argument("--out", default="parabolic_transform.html")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)

    from ..engine import FUNCTIONS
    from ..plots import compute_selected, serve_html, write_plotly_html

    computed = compute_selected(FUNCTIONS, args.functions, args.x_min, args.x_max, args.n_points)
    out = args.out if args.out.endswith(".html") else args.out + ".html"
    written = write_plotly_html(computed, out, args.x_min, args.x_max)
    print("wrote", written)
    if args.serve:
        serve_html(written, port=args.port, open_browser=not args.no_browser)
    return 0


if __name__ == "__main__":
    sys.exit(main())
