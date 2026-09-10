"""PNG backend: save a static Matplotlib plot.

Run:
    python -m engines.reverse_subtraction.examples.example_plot_png --start 1 --end 200 --out reverse.png
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reverse subtraction PNG plot.")
    parser.add_argument("--start", type=int, default=1)
    parser.add_argument("--end", type=int, default=200)
    parser.add_argument("--out", default="reverse_subtraction.png")
    args = parser.parse_args(argv)

    from ..engine import compute_reverse_subtraction, compute_stats
    from ..plots import save_matplotlib_png

    xs, ys = compute_reverse_subtraction(args.start, args.end)
    print("stats:", compute_stats(xs, ys))
    print("writing", save_matplotlib_png(xs, ys, args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
