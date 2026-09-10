"""PNG backend: save a static Matplotlib plot.

Run:
    python -m engines.math_plotter.examples.example_plot_png --functions \"sin(x)\" \"cos(x)\" --out transform.png
"""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Parabolic transform PNG plot.")
    parser.add_argument("--functions", nargs="*", default=["exp(-x^2)"])
    parser.add_argument("--x-min", type=float, default=-2.0)
    parser.add_argument("--x-max", type=float, default=2.0)
    parser.add_argument("--n-points", type=int, default=500)
    parser.add_argument("--out", default="parabolic_transform.png")
    args = parser.parse_args(argv)

    from ..engine import FUNCTIONS
    from ..plots import compute_selected, save_matplotlib_png

    computed = compute_selected(FUNCTIONS, args.functions, args.x_min, args.x_max, args.n_points)
    for name, (_, _, skipped) in computed.items():
        print(f"{name}: {len(computed[name][0])} plotted, {len(skipped)} out of range")
    print("writing", save_matplotlib_png(computed, args.out, args.x_min, args.x_max))
    return 0


if __name__ == "__main__":
    sys.exit(main())
