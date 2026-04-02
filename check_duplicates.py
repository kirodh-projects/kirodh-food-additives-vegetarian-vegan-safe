"""Standalone script to check for duplicates in the food additives database.

Usage:
    python check_duplicates.py [--db-path PATH]
"""

import argparse
import sys

from src.db.connection import get_db_path
from src.db.queries import check_duplicates


def main():
    parser = argparse.ArgumentParser(description="Check for duplicates in the database")
    parser.add_argument("--db-path", type=str, default=None, help="Path to the database")
    args = parser.parse_args()

    db_path = args.db_path or get_db_path()
    print(f"Checking database: {db_path}\n")

    results = check_duplicates(db_path)

    found_issues = False

    # Exact E-number duplicates
    dupes = results["exact_e_number_dupes"]
    if dupes:
        found_issues = True
        print(f"DUPLICATE E-NUMBERS ({len(dupes)} found):")
        for d in dupes:
            print(f"  {d['e_number']}: {d['cnt']} occurrences")
    else:
        print("E-number duplicates: None (OK)")

    print()

    # INS numbers mapped to multiple E-numbers
    multi = results["ins_multi_mapping"]
    if multi:
        found_issues = True
        print(f"INS NUMBERS WITH MULTIPLE E-NUMBERS ({len(multi)} found):")
        for m in multi:
            print(f"  INS {m['ins_number']}: {m['cnt']} E-numbers -> {m['e_numbers']}")
    else:
        print("INS multi-mappings: None (OK)")

    print()

    if found_issues:
        print("Issues found. Review the duplicates above.")
        sys.exit(1)
    else:
        print("All checks passed. No duplicate issues found.")
        sys.exit(0)


if __name__ == "__main__":
    main()
