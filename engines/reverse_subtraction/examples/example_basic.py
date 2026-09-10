"""Data backend: print n - reverse(n) values + stats (no plotting).

Run:
    python -m engines.reverse_subtraction.examples.example_basic --start 1 --end 200
    python -m engines.reverse_subtraction.examples.example_basic --start 1 --end 30 --show-values
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reverse subtraction data.")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=200)
    parser.add_argument("--show-values", action="store_true")
    args = parser.parse_args(argv)

    if args.start > args.end:
        parser.error("Start must be <= end.")
    if args.end - args.start > 100_000:
        parser.error("Range too large (max 100,000).")

    from ..engine import compute_reverse_subtraction, compute_stats

    xs, ys = compute_reverse_subtraction(args.start, args.end)
    stats = compute_stats(xs, ys)
    print(f"n = {args.start}..{args.end}  count={stats['count']} zeros={stats['zeros']} "
          f"max={stats['max']} min={stats['min']} mean={stats['mean']:.2f}")
    print("zeros (palindromes):", ", ".join(map(str, stats["zero_values"][:50]))
          or "none", "..." if stats["zeros"] > 50 else "")
    if args.show_values:
        for x, y in zip(xs, ys):
            print(f"  {x} -> {y}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
