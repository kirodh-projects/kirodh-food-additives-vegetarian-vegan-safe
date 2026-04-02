"""Reverse Subtraction Plotter: plots n - reverse(n) for a range of integers.

For each integer n in the range, the y-value is n minus the integer formed
by reversing its digits. Negative numbers are handled by reversing the
absolute value and reapplying the sign.

Examples:
    8    -> 8 - 8       = 0
    21   -> 21 - 12     = 9
    12   -> 12 - 21     = -9
    100  -> 100 - 1     = 99
    -21  -> -21 - (-12) = -9
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st


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
    """Compute n - reverse(n) for each integer in [start, end].

    Returns (x_values, y_values).
    """
    xs = list(range(start, end + 1))
    ys = [n - reverse_number(n) for n in xs]
    return xs, ys


def render_reverse_subtract_page() -> None:
    """Render the reverse subtraction plotter page."""
    st.header("Reverse Subtraction Plotter")
    st.caption(
        "For each integer **n**, plot **n - reverse(n)** where reverse(n) "
        "is the number with its digits reversed. "
        "E.g. 21 - 12 = 9, 100 - 001 = 99."
    )

    # --- Controls ---
    col1, col2 = st.columns(2)
    with col1:
        start = st.number_input("Start", value=1, step=1)
    with col2:
        end = st.number_input("End", value=200, step=1)

    if start > end:
        st.error("Start must be less than or equal to End.")
        return

    if end - start > 100_000:
        st.error("Range too large (max 100,000). Please narrow it down.")
        return

    if st.button("Plot", type="primary"):
        xs, ys = compute_reverse_subtraction(int(start), int(end))

        # Main scatter/line plot
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="lines+markers" if len(xs) <= 500 else "lines",
            name="n - reverse(n)",
            line=dict(color="#3498db", width=1.5),
            marker=dict(size=3),
            hovertemplate="n = %{x}<br>n - reverse(n) = %{y}<extra></extra>",
        ))

        # Zero line
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

        fig.update_layout(
            title=f"n - reverse(n) for n = {int(start)} to {int(end)}",
            xaxis_title="n",
            yaxis_title="n - reverse(n)",
            height=550,
            hovermode="x unified",
        )

        st.plotly_chart(fig, use_container_width=True)

        # --- Stats ---
        ys_arr = np.array(ys)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Zeros (palindromic diff)", int(np.sum(ys_arr == 0)))
        with col2:
            st.metric("Max value", int(np.max(ys_arr)))
        with col3:
            st.metric("Min value", int(np.min(ys_arr)))
        with col4:
            st.metric("Mean", f"{np.mean(ys_arr):.2f}")

        # --- Table of notable values ---
        with st.expander("Values where n - reverse(n) = 0 (digit palindromes & repdigits)"):
            zeros = [x for x, y in zip(xs, ys) if y == 0]
            if zeros:
                st.write(", ".join(str(z) for z in zeros))
            else:
                st.write("None in this range.")
