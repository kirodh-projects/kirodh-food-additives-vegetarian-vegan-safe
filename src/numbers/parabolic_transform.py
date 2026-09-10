"""Pure parabolic axis transformation logic.

Concept:
  - A parabola ``y = x^2`` serves as a curved "axis".
  - An input function's output is interpreted as signed arc-length
    along the parabola.
  - Points are projected perpendicular to the parabola at the
    corresponding arc-length position.

UI-free so it can be unit-tested and reused in scripts.
The Streamlit page lives in :mod:`src.numbers.ui.math_plotter_page`.
The legacy matplotlib script at the repo root (``math_plotter.py``)
is now a thin wrapper around :class:`Axis` here.
"""

import math
from collections.abc import Callable

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad
from scipy.optimize import root_scalar

__all__ = [
    "FUNCTIONS",
    "arc_length",
    "x_from_signed_arc",
    "transform_point",
    "compute_transformed_function",
    "Axis",
]


def arc_length(x: float) -> float:
    """Return signed arc length along y=x^2 from the vertex (x=0) to x."""
    integrand = lambda t: np.sqrt(1 + (2 * t) ** 2)  # noqa: E731
    if x >= 0:
        s, _ = quad(integrand, 0, x)
    else:
        s, _ = quad(integrand, x, 0)
        s = -s
    return s


def x_from_signed_arc(s_target: float, x_min: float, x_max: float) -> float | None:
    """Find the parabola x coordinate for a signed arc-length ``s_target``."""
    s_min = arc_length(x_min)
    s_max = arc_length(x_max)

    if s_target < s_min or s_target > s_max:
        return None

    func = lambda x: arc_length(x) - s_target  # noqa: E731
    bracket = (0, x_max) if s_target >= 0 else (x_min, 0)

    try:
        sol = root_scalar(func, bracket=bracket, method="bisect")
        return sol.root
    except ValueError:
        return None


def transform_point(
    x: float,
    y: float,
    x_min: float,
    x_max: float,
) -> tuple[float, float] | None:
    """Transform a point using the parabolic axis.

    Args:
        x: the original x coordinate (horizontal position).
        y: function output, interpreted as signed arc-length along the parabola.
        x_min: left edge of the parabola range.
        x_max: right edge of the parabola range.
    """
    x0 = x_from_signed_arc(y, x_min, x_max)
    if x0 is None:
        return None

    y0 = x0**2
    slope = 2 * x0
    if abs(slope) < 1e-12:
        return (x, y0)

    m_perp = -1.0 / slope
    y_intersection = m_perp * (x - x0) + y0
    return (x, y_intersection)


def compute_transformed_function(
    func: Callable[[float], float],
    x_min: float,
    x_max: float,
    n_points: int = 500,
) -> tuple[list[float], list[float], list[float]]:
    """Compute the transformed version of a function.

    Returns ``(new_x, new_y, skipped_x)`` where ``skipped_x`` holds
    inputs whose output fell outside the parabola's arc-length range.
    """
    xs = np.linspace(x_min, x_max, n_points)

    new_x, new_y, skipped_x = [], [], []

    for x in xs:
        y_arc = func(x)
        pt = transform_point(x, y_arc, x_min, x_max)
        if pt is not None:
            new_x.append(pt[0])
            new_y.append(pt[1])
        else:
            skipped_x.append(x)

    return new_x, new_y, skipped_x


FUNCTIONS: dict[str, Callable[[float], float]] = {
    "exp(-x^2)": lambda x: math.exp(-(x**2)),
    "2^x": lambda x: math.exp2(x),
    "x^2": lambda x: x**2,
    "sin(x)": lambda x: math.sin(x),
    "cos(x)": lambda x: math.cos(x),
    "x": lambda x: x,
    "-5x": lambda x: -5 * x,
    "x^3": lambda x: x**3,
    "1/(1+x^2)": lambda x: 1 / (1 + x**2),
    "tanh(x)": lambda x: math.tanh(x),
}


class Axis:
    """Legacy matplotlib wrapper (kept for ``math_plotter.py`` compat).

    New code should use the pure functions above directly, or the
    Streamlit page in :mod:`src.numbers.ui.math_plotter_page`.
    """

    def __init__(self, x_min: float = -10, x_max: float = 10):
        self.x_min = x_min
        self.x_max = x_max
        self.figure = None
        self.ax = None

    def _setup_plot(self):
        self.figure, self.ax = plt.subplots()
        self.ax.set_xlim(self.x_min, self.x_max)

        self.ax.spines["left"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.get_yaxis().set_visible(False)

        self.ax.spines["bottom"].set_position(("data", 0))
        self.ax.spines["top"].set_visible(False)

        self.ax.grid(True, linestyle="--", alpha=0.3)

    def plot_parabola(self):
        x = np.linspace(self.x_min, self.x_max, 2000)
        y = x**2
        self.ax.plot(x, y, label="Parabola (new y-axis)")

    def arc_length(self, x: float) -> float:
        """Return signed arc length from vertex x=0 to x."""
        return arc_length(x)

    def x_from_signed_arc(self, s_target: float):
        """Find parabola x coordinate for signed arc-length ``s_target``."""
        return x_from_signed_arc(s_target, self.x_min, self.x_max)

    def transform_point(self, x: float, y: float):
        """Transform ``(x, y)`` where ``y`` is a signed arc-length."""
        return transform_point(x, y, self.x_min, self.x_max)

    def plot_function(self, func, label, n_points=500):
        xs = np.linspace(self.x_min, self.x_max, n_points)

        new_x, new_y, skipped_x = compute_transformed_function(
            func, self.x_min, self.x_max, n_points
        )
        # Keep original behaviour: recompute via instance methods so
        # subclasses keep working, but reuse the shared helper result.
        _ = xs  # xs kept for API parity with the original script

        self.ax.plot(new_x, new_y, label=label)

        if skipped_x:
            self.ax.plot(
                skipped_x,
                [0] * len(skipped_x),
                marker="*",
                linestyle="",
                color="orange",
                label=f"Out of range points ({label})",
            )

    def render(self, filename="transformed_exact.png"):
        self._setup_plot()
        self.plot_parabola()

        self.plot_function(lambda x: math.exp(-(x**2)), "y=-5x")

        self.ax.legend()
        plt.savefig(filename, bbox_inches="tight")
        print(f"{filename} saved")


if __name__ == "__main__":
    a = Axis(-2, 2)
    a.render()
