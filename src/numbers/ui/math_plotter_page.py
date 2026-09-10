"""Math Plotter page: parabolic axis transformation of arbitrary functions.

Interactive Streamlit page with Plotly charts. Core math lives in
:mod:`src.numbers.parabolic_transform` (UI-free, unit-tested).

Concept:
  - A parabola y = x^2 serves as a curved "axis"
  - An input function's output is interpreted as signed arc-length along the parabola
  - Points are projected perpendicular to the parabola at the corresponding arc-length position
  - The result is a visual transformation of the function onto the curved axis
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from src.numbers.parabolic_transform import FUNCTIONS, compute_transformed_function

__all__ = ["FUNCTIONS", "render_math_plotter_page"]


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
