"""Pure reverse-subtraction engine: ``n - reverse(n)``.

Self-contained with no UI, no Streamlit, no other engines.
Import from anywhere::

    from engines.reverse_subtraction import reverse_number, compute_reverse_subtraction

Examples:
    8    -> 8 - 8       = 0
    21   -> 21 - 12     = 9
    12   -> 12 - 21     = -9
    100  -> 100 - 1     = 99
    -21  -> -21 - (-12) = -9
"""

__all__ = ["reverse_number", "compute_reverse_subtraction", "compute_stats"]


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


def compute_stats(xs: list[int], ys: list[int]) -> dict:
    """Descriptive stats for a computed range (data backend)."""
    if not xs:
        return {"count": 0, "zeros": 0, "max": None, "min": None, "mean": None, "zero_values": []}
    zero_values = [x for x, y in zip(xs, ys) if y == 0]
    return {
        "count": len(xs),
        "start": xs[0],
        "end": xs[-1],
        "zeros": len(zero_values),
        "max": max(ys),
        "min": min(ys),
        "mean": sum(ys) / len(ys),
        "zero_values": zero_values,
    }
