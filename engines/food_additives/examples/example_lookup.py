"""Look up one additive by E/INS code or name.

Run:
    python -m engines.food_additives.examples.example_lookup --code E120
    python -m engines.food_additives.examples.example_lookup --code 100
    python -m engines.food_additives.examples.example_lookup --name curcumin
    python -m engines.food_additives.examples.example_lookup --code E100 --db-path ./databases/food_additives.db
"""

from __future__ import annotations

import argparse
import json
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Look up a food additive.")
    parser.add_argument("--code", default=None, help="E-number or INS number, e.g. E120, 100, INS100")
    parser.add_argument("--name", default=None, help="Partial name search, e.g. curcumin")
    parser.add_argument("--db-path", default=None, help="SQLite DB path (default: $DB_PATH)")
    args = parser.parse_args(argv)

    if not args.code and not args.name:
        parser.error("Provide --code and/or --name.")

    from ..connection import ensure_database
    from ..queries import search_by_code, search_by_name

    db_path = ensure_database(args.db_path)
    if args.code:
        hit = search_by_code(db_path, args.code)
        print(f"--- code search: {args.code!r} (db: {db_path}) ---")
        print(json.dumps(hit, indent=2, default=str) if hit else "No match.")
    if args.name:
        hits = search_by_name(db_path, args.name)
        print(f"--- name search: {args.name!r} -> {len(hits)} hit(s) ---")
        for hit in hits[:10]:
            print(f"  {hit['e_number']:8s} INS={str(hit.get('ins_number')):10s} "
                  f"vegan={hit.get('vegan_status')} veg={hit.get('vegetarian_status')} "
                  f"safety={hit.get('safety_level')} :: {hit.get('common_name')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
