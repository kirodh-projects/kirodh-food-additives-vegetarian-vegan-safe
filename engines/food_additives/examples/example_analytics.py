"""Analytics dashboard: data / static PNG / interactive plotly + local server.

Run:
    python -m engines.food_additives.examples.example_analytics --backend data
    python -m engines.food_additives.examples.example_analytics --backend png --out analytics.png
    python -m engines.food_additives.examples.example_analytics --backend plotly --out analytics.html
    python -m engines.food_additives.examples.example_analytics --backend plotly --out analytics.html --serve
"""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Food additives analytics.")
    parser.add_argument("--backend", choices=["data", "png", "plotly"], default="data")
    parser.add_argument("--db-path", default=None)
    parser.add_argument("--out", default="food_analytics.png", help="Output file for png/plotly")
    parser.add_argument("--serve", action="store_true", help="Serve plotly HTML locally (plotly only)")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)

    from ..connection import ensure_database
    from ..queries import get_analytics_summary, get_category_vegan_breakdown

    db_path = ensure_database(args.db_path)
    summary = get_analytics_summary(db_path)
    print(f"db: {db_path}  total: {summary.get('total', 0)}")

    if args.backend == "data":
        print(json.dumps(summary, indent=2, default=str)[:4000])
        return 0

    breakdown = get_category_vegan_breakdown(db_path)
    if args.backend == "png":
        from ..plots import save_matplotlib_dashboard

        out = args.out if args.out.endswith(".png") else args.out + ".png"
        print("writing", save_matplotlib_dashboard(summary, out, breakdown))
        return 0

    from ..plots import serve_html, write_plotly_dashboard

    out = args.out if args.out.endswith(".html") else args.out + ".html"
    written = write_plotly_dashboard(summary, out, breakdown)
    print("wrote", written)
    if args.serve:
        serve_html(written, port=args.port, open_browser=not args.no_browser)
    return 0


if __name__ == "__main__":
    sys.exit(main())
