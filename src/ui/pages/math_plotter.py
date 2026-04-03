"""Math Plotter page: parabolic axis transformation of arbitrary functions.

Reimplements the logic from math_plotter.py as an interactive Streamlit page
with Plotly charts. The original file is preserved at the project root.

Concept:
  - A parabola y = x^2 serves as a curved "axis"
  - An input function's output is interpreted as signed arc-length along the parabola
  - Points are projected perpendicular to the parabola at the corresponding arc-length position
  - The result is a visual transformation of the function onto the curved axis
"""

import math

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from scipy.integrate import quad
from scipy.optimize import root_scalar


# ---------------------------------------------------------------------------
# Core transformation logic (preserved from math_plotter.py)
# ---------------------------------------------------------------------------

def arc_length(x: float) -> float:
    """Return signed arc length along y=x^2 from the vertex (x=0) to x."""
    integrand = lambda t: np.sqrt(1 + (2 * t) ** 2)
    if x >= 0:
        s, _ = quad(integrand, 0, x)
    else:
        s, _ = quad(integrand, x, 0)
        s = -s
    return s


def x_from_signed_arc(s_target: float, x_min: float, x_max: float) -> float | None:
    """Find the parabola x coordinate corresponding to a signed arc-length s_target."""
    s_min = arc_length(x_min)
    s_max = arc_length(x_max)

    if s_target < s_min or s_target > s_max:
        return None

    func = lambda x: arc_length(x) - s_target
    bracket = (0, x_max) if s_target >= 0 else (x_min, 0)

    try:
        sol = root_scalar(func, bracket=bracket, method="bisect")
        return sol.root
    except ValueError:
        return None


def transform_point(
    x: float, y: float, x_min: float, x_max: float,
) -> tuple[float, float] | None:
    """Transform a point using the parabolic axis.

    x: the original x coordinate (horizontal position)
    y: function output, interpreted as signed arc-length along the parabola
    """
    x0 = x_from_signed_arc(y, x_min, x_max)
    if x0 is None:
        return None

    y0 = x0 ** 2
    slope = 2 * x0
    if abs(slope) < 1e-12:
        return (x, y0)

    m_perp = -1.0 / slope
    y_intersection = m_perp * (x - x0) + y0
    return (x, y_intersection)


def compute_transformed_function(
    func, x_min: float, x_max: float, n_points: int = 500,
) -> tuple[list[float], list[float], list[float]]:
    """Compute the transformed version of a function.

    Returns (new_x, new_y, skipped_x).
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


# ---------------------------------------------------------------------------
# Available functions for transformation
# ---------------------------------------------------------------------------

FUNCTIONS = {
    "exp(-x^2)": lambda x: math.exp(-(x ** 2)),
    "2^x": lambda x: math.exp2(x),
    "x^2": lambda x: x ** 2,
    "sin(x)": lambda x: math.sin(x),
    "cos(x)": lambda x: math.cos(x),
    "x": lambda x: x,
    "-5x": lambda x: -5 * x,
    "x^3": lambda x: x ** 3,
    "1/(1+x^2)": lambda x: 1 / (1 + x ** 2),
    "tanh(x)": lambda x: math.tanh(x),
}


# ---------------------------------------------------------------------------
# Streamlit page
# ---------------------------------------------------------------------------

def render_math_plotter_page() -> None:
    """Render the math plotter page."""
    st.header("Math Plotter - Parabolic Axis Transform")
    st.caption(
        "Transform arbitrary functions using a parabola (y = x\u00b2) as a curved axis. "
        "Function outputs are interpreted as signed arc-lengths along the parabola, "
        "then projected perpendicular to it."
    )

    # --- Controls ---
    col1, col2, col3 = st.columns(3)

    with col1:
        x_min = st.number_input("X min", value=-2.0, step=0.5)
    with col2:
        x_max = st.number_input("X max", value=2.0, step=0.5)
    with col3:
        n_points = st.slider("Resolution (points)", 100, 2000, 500, step=100)

    if x_min >= x_max:
        st.error("X min must be less than X max.")
        return

    selected_funcs = st.multiselect(
        "Select functions to transform",
        list(FUNCTIONS.keys()),
        default=["exp(-x^2)"],
    )

    if not selected_funcs:
        st.info("Select at least one function.")
        return

    if st.button("Plot", type="primary"):
        _render_plot(x_min, x_max, n_points, selected_funcs)


def _render_plot(
    x_min: float, x_max: float, n_points: int, selected_funcs: list[str],
) -> None:
    """Compute transformations and render the Plotly chart."""
    fig = go.Figure()

    # Parabola (the curved axis)
    px = np.linspace(x_min, x_max, 2000)
    py = px ** 2
    fig.add_trace(go.Scatter(
        x=px, y=py,
        mode="lines",
        name="Parabola (curved axis)",
        line=dict(color="royalblue", width=2),
    ))

    # Transform each selected function
    colors = [
        "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6",
        "#1abc9c", "#e67e22", "#3498db", "#e91e63",
        "#00bcd4", "#ff5722",
    ]

    total_skipped = 0

    for i, func_name in enumerate(selected_funcs):
        func = FUNCTIONS[func_name]
        color = colors[i % len(colors)]

        with st.spinner(f"Computing {func_name}..."):
            new_x, new_y, skipped_x = compute_transformed_function(
                func, x_min, x_max, n_points,
            )

        fig.add_trace(go.Scatter(
            x=new_x, y=new_y,
            mode="lines",
            name=f"y = {func_name}",
            line=dict(color=color, width=2),
        ))

        if skipped_x:
            total_skipped += len(skipped_x)
            fig.add_trace(go.Scatter(
                x=skipped_x,
                y=[0] * len(skipped_x),
                mode="markers",
                name=f"Out of range ({func_name})",
                marker=dict(symbol="star", color="orange", size=6),
            ))

    # Layout
    fig.update_layout(
        title="Parabolic Axis Transformation",
        xaxis=dict(
            title="x",
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor="black",
            gridcolor="rgba(0,0,0,0.1)",
        ),
        yaxis=dict(
            title="y",
            zeroline=True,
            zerolinewidth=1,
            zerolinecolor="rgba(0,0,0,0.3)",
            gridcolor="rgba(0,0,0,0.1)",
        ),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        height=600,
        hovermode="closest",
    )

    st.plotly_chart(fig, width="stretch")

    if total_skipped > 0:
        st.warning(
            f"{total_skipped} point(s) fell outside the parabola's arc-length range "
            f"and could not be plotted (shown as orange stars on the x-axis)."
        )

    # Explanation
    with st.expander("How does this work?"):
        st.markdown("""
**Parabolic Axis Transformation**

1. The parabola **y = x\u00b2** serves as a curved coordinate axis
2. For each input point **(x, f(x))**:
   - **f(x)** is treated as a **signed arc-length** along the parabola from its vertex
   - The corresponding point on the parabola is found by inverting the arc-length integral
   - A **perpendicular line** to the parabola is drawn at that point
   - The original **x** coordinate determines where on that perpendicular the point lands
3. The result is the original function "wrapped" onto the parabolic axis

This is useful for visualizing how functions behave when mapped to non-linear coordinate systems.
        """)
