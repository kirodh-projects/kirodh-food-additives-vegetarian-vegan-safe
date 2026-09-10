"""Pure reverse-subtraction logic: ``n - reverse(n)``.

UI-free so it can be unit-tested and reused in scripts.
The Streamlit page lives in :mod:`src.numbers.ui.reverse_subtract_page`.

Examples:
    8    -> 8 - 8       = 0
    21   -> 21 - 12     = 9
    12   -> 12 - 21     = -9
    100  -> 100 - 1     = 99
    -21  -> -21 - (-12) = -9
"""

__all__ = ["reverse_number", "compute_reverse_subtraction"]


def reverse_number(n: int) -> int:
    """Reverse the digits of an integer, preserving sign.

    reverse_number(21)  -> 12
    reverse_number(100) -> 1
    reverse_number(-21) -> -12
    """
    sign = -1 if n < 0 else 1
    reversed_str = str(abs(n))[::-1]
    return sign * int(reversed_str)


def compute_reverse_subtraction(start: int, end: int) -> tuple[list[int], list[int]]:
    """Compute ``n - reverse(n)`` for each integer in ``[start, end]``.

    Returns ``(x_values, y_values)``.
    """
    xs = list(range(start, end + 1))
    ys = [n - reverse_number(n) for n in xs]
    return xs, ys
