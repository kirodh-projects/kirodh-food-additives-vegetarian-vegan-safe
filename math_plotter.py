import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad
from scipy.optimize import root_scalar

class Axis:
    def __init__(self, x_min=-10, x_max=10):
        self.x_min = x_min
        self.x_max = x_max
        self.figure = None
        self.ax = None

    # -------------------------
    # Plot setup
    # -------------------------
    def _setup_plot(self):
        self.figure, self.ax = plt.subplots()
        self.ax.set_xlim(self.x_min, self.x_max)

        self.ax.spines['left'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.get_yaxis().set_visible(False)

        self.ax.spines['bottom'].set_position(('data', 0))
        self.ax.spines['top'].set_visible(False)

        self.ax.grid(True, linestyle="--", alpha=0.3)

    # -------------------------
    # Base parabola
    # -------------------------
    def plot_parabola(self):
        x = np.linspace(self.x_min, self.x_max, 2000)
        y = x ** 2
        self.ax.plot(x, y, label="Parabola (new y-axis)")

    # -------------------------
    # Arc length function
    # -------------------------
    def arc_length(self, x):
        """Return signed arc length from vertex x=0 to x"""
        integrand = lambda t: np.sqrt(1 + (2*t)**2)
        if x >= 0:
            s, _ = quad(integrand, 0, x)
        else:
            s, _ = quad(integrand, x, 0)
            s = -s
        return s

    # -------------------------
    # Invert arc length: find parabola x for signed arc-length s
    # -------------------------
    def x_from_signed_arc(self, s_target):
        """Find parabola x coordinate corresponding to signed arc-length s_target"""
        func = lambda x: self.arc_length(x) - s_target
        # bracket depends on sign
        bracket = (0, self.x_max) if s_target >= 0 else (self.x_min, 0)
        sol = root_scalar(func, bracket=bracket, method='bisect')
        return sol.root

    # -------------------------
    # Transform function
    # -------------------------
    def transform_point(self, x, y):
        """
        x : vertical line position
        y : signed arc-length output (can be negative)
        """
        # Find parabola point exactly at signed arc-length y
        x0 = self.x_from_signed_arc(y)
        y0 = x0**2

        slope = 2 * x0
        if abs(slope) < 1e-12:
            # vertex case
            return (x, y0)

        m_perp = -1.0 / slope
        y_intersection = m_perp * (x - x0) + y0
        return (x, y_intersection)

    # -------------------------
    # Plot arbitrary function
    # -------------------------
    def plot_function(self, func, label):
        xs = np.linspace(self.x_min, self.x_max, 300)
        new_x = []
        new_y = []

        for x in xs:
            y_arc = func(x)  # function output is the signed arc-length
            pt = self.transform_point(x, y_arc)
            new_x.append(pt[0])
            new_y.append(pt[1])

        self.ax.plot(new_x, new_y, label=label)

    # -------------------------
    # Master render
    # -------------------------
    def render(self, filename="transformed_exact.png"):
        self._setup_plot()
        self.plot_parabola()

        # Examples: output is signed arc-length
        self.plot_function(lambda x: -x, "y=-x")
        self.plot_function(lambda x: x, "y=x")
        self.plot_function(lambda x: x**2, "y=x^2")

        self.ax.legend()
        plt.savefig(filename, bbox_inches="tight")
        print(f"{filename} saved")


if __name__ == "__main__":
    a = Axis(-10, 10)
    a.render()