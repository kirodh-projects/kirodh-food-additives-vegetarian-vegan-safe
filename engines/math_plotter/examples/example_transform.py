"""Data backend: compute transforms and print point counts (no plotting).

Run:
    python -m engines.math_plotter.examples.example_transform --functions \"sin(x)\" --x-min -2 --x-max 2
    python -m engines.math_plotter.examples.example_transform --functions \"sin(x)\" \"cos(x)\" --list-functions
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parabolic transform data.")
    parser.add_argument("--functions", nargs="*", default=["sin(x)"])
    parser.add_argument("--x-min", type=float, default=-2.0)
    parser.add_argument("--x-max", type=float, default=2.0)
    parser.add_argument("--n-points", type=int, default=500)
    parser.add_argument("--list-functions", action="store_true")
    args = parser.parse_args(argv)

    from ..engine import FUNCTIONS, compute_transformed_function

    if args.list_functions:
        print("available:", ", ".join(sorted(FUNCTIONS)))
        return 0
    if args.x_min >= args.x_max:
        parser.error("X min must be < X max.")
    for name in args.functions:
        if name not in FUNCTIONS:
            parser.error(f"Unknown function {name!r}. Available: {sorted(FUNCTIONS)}")
        new_x, new_y, skipped = compute_transformed_function(
            FUNCTIONS[name], args.x_min, args.x_max, args.n_points)
        print(f"{name}: {len(new_x)} plotted, {len(skipped)} out of range "
              f"(x in [{args.x_min}, {args.x_max}], n={args.n_points})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
