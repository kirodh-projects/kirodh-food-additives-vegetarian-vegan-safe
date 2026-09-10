"""Standalone script to check for duplicates in the food additives database.

Usage:
    python check_duplicates.py [--db-path PATH]

Thin wrapper around :mod:`src.food_additives.duplicates` (canonical location).
"""

from src.food_additives.duplicates import main

if __name__ == "__main__":
    main()
