"""Check the database for duplicate E-numbers / shared INS mappings.

Run:
    python -m engines.food_additives.examples.example_duplicates
    python -m engines.food_additives.examples.example_duplicates --db-path ./databases/food_additives.db
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Duplicate checker.")
    parser.add_argument("--db-path", default=None)
    args = parser.parse_args(argv)

    from ..connection import ensure_database
    from ..queries import check_duplicates

    db_path = ensure_database(args.db_path)
    results = check_duplicates(db_path)
    dupes = results["exact_e_number_dupes"]
    multi = results["ins_multi_mapping"]
    print(f"db: {db_path}")
    print(f"exact E-number duplicates: {len(dupes)}")
    for d in dupes[:10]:
        print("  ", d)
    print(f"INS numbers shared by several E-numbers: {len(multi)}")
    for m in multi[:10]:
        print(f"   INS {m['ins_number']}: {m['cnt']} E-numbers -> {m['e_numbers']}")
    return 1 if (dupes or multi) else 0


if __name__ == "__main__":
    sys.exit(main())
