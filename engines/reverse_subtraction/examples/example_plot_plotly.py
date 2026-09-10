"""Plotly backend: write interactive HTML + optionally serve locally.

Run:
    python -m engines.reverse_subtraction.examples.example_plot_plotly --start 1 --end 200 --out reverse.html
    python -m engines.reverse_subtraction.examples.example_plot_plotly --start 1 --end 200 --out reverse.html --serve
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reverse subtraction Plotly plot.")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=200)
    parser.add_argument("--out", default="reverse_subtraction.html")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)

    from ..engine import compute_reverse_subtraction
    from ..plots import serve_html, write_plotly_html

    xs, ys = compute_reverse_subtraction(args.start, args.end)
    out = args.out if args.out.endswith(".html") else args.out + ".html"
    written = write_plotly_html(xs, ys, out)
    print("wrote", written)
    if args.serve:
        serve_html(written, port=args.port, open_browser=not args.no_browser)
    return 0


if __name__ == "__main__":
    sys.exit(main())
