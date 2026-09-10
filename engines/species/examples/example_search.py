"""Search species by scientific name / genus / family.

Run:
    python -m engines.species.examples.example_search --query \"Panthera leo\" --limit 10
    python -m engines.species.examples.example_search --query Felidae --limit 5 --db-dir ./databases
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search species.")
    parser.add_argument("--query", required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--db-dir", default=None)
    args = parser.parse_args(argv)

    from ..connection import list_species_db_files
    from ..queries import search_species

    files = list_species_db_files(args.db_dir)
    if not files:
        print("No species database found. Build it with:")
        print("  python -m engines.species.build_database")
        return 2
    print(f"shards: {len(files)}")
    for hit in search_species(args.query, db_dir=args.db_dir, limit=args.limit):
        print(f"  {hit.get('scientific_name')} | {hit.get('kingdom')} > "
              f"{hit.get('family')} > {hit.get('genus')} "
              f"[{hit.get('taxon_rank')}/{hit.get('taxonomic_status')}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
