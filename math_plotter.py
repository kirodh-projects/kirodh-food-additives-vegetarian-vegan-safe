"""Legacy entry point. Canonical location: :mod:`src.numbers.parabolic_transform`.

Kept so existing scripts/docs keep working::

    python math_plotter.py
"""

from src.numbers.parabolic_transform import Axis

__all__ = ["Axis"]


if __name__ == "__main__":
    a = Axis(-2, 2)
    a.render()
