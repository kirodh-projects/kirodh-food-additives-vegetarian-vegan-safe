"""Species statistics: data / static PNG / interactive plotly + local server.

Run:
    python -m engines.species.examples.example_stats --backend data
    python -m engines.species.examples.example_stats --backend png --out species.png
    python -m engines.species.examples.example_stats --backend plotly --out species.html --serve
"""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Species statistics.")
    parser.add_argument("--backend", choices=["data", "png", "plotly"], default="data")
    parser.add_argument("--db-dir", default=None)
    parser.add_argument("--out", default="species_stats.png")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args(argv)

    from ..connection import list_species_db_files
    from ..queries import get_species_stats, get_trait_distribution

    if not list_species_db_files(args.db_dir):
        print("No species database found. Build it with:")
        print("  python -m engines.species.build_database")
        return 2
    stats = get_species_stats(args.db_dir)
    print(f"total: {stats.get('total', 0):,}  files: {stats.get('db_file_count', 0)}")

    if args.backend == "data":
        slim = {k: v for k, v in stats.items() if k != "trait_by_kingdom"}
        print(json.dumps(slim, indent=2, default=str)[:4000])
        return 0

    if args.backend == "png":
        from ..plots import save_matplotlib_dashboard

        out = args.out if args.out.endswith(".png") else args.out + ".png"
        print("writing", save_matplotlib_dashboard(stats, out))
        return 0

    from ..plots import serve_html, write_plotly_dashboard

    distribution = get_trait_distribution(args.db_dir)
    out = args.out if args.out.endswith(".html") else args.out + ".html"
    written = write_plotly_dashboard(stats, out, distribution)
    print("wrote", written)
    if args.serve:
        serve_html(written, port=args.port, open_browser=not args.no_browser)
    return 0


if __name__ == "__main__":
    sys.exit(main())
