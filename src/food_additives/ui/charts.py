"""Plotly chart builder functions for the analytics dashboard."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


# Consistent color maps across charts
VEGAN_COLORS = {"Yes": "#2ecc71", "No": "#e74c3c", "Maybe": "#f39c12", "Unknown": "#95a5a6"}
SAFETY_COLORS = {
    "Safe": "#2ecc71", "Caution": "#f39c12", "Avoid": "#e74c3c",
    "Banned": "#8e44ad", "Unknown": "#95a5a6",
}
HALAL_COLORS = {"Halal": "#2ecc71", "Doubtful": "#f39c12", "Haram": "#e74c3c", "Unknown": "#95a5a6"}
ORIGIN_COLORS = {
    "Synthetic": "#3498db", "Natural (Plant)": "#2ecc71",
    "Natural (Animal)": "#e74c3c", "Natural (Mineral)": "#f39c12",
    "Mixed": "#9b59b6", "Unknown": "#95a5a6",
}


def make_pie_chart(
    data: dict[str, int],
    title: str,
    color_map: dict[str, str] | None = None,
) -> go.Figure:
    """Create a pie chart from a dict of {label: count}."""
    labels = list(data.keys())
    values = list(data.values())
    colors = [color_map.get(l, "#95a5a6") for l in labels] if color_map else None

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors) if colors else None,
        textinfo="label+percent",
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    )])
    fig.update_layout(
        title=title,
        showlegend=True,
        margin=dict(t=40, b=20, l=20, r=20),
        height=350,
    )
    return fig


def make_bar_chart(
    data: dict[str, int],
    title: str,
    color_map: dict[str, str] | None = None,
    horizontal: bool = False,
) -> go.Figure:
    """Create a bar chart from a dict of {label: count}."""
    labels = list(data.keys())
    values = list(data.values())
    colors = [color_map.get(l, "#3498db") for l in labels] if color_map else None

    if horizontal:
        fig = go.Figure(data=[go.Bar(
            y=labels, x=values, orientation="h",
            marker_color=colors,
            hovertemplate="%{y}: %{x}<extra></extra>",
        )])
    else:
        fig = go.Figure(data=[go.Bar(
            x=labels, y=values,
            marker_color=colors,
            hovertemplate="%{x}: %{y}<extra></extra>",
        )])

    fig.update_layout(
        title=title,
        margin=dict(t=40, b=20, l=20, r=20),
        height=400,
    )
    return fig


def make_stacked_bar(
    df: pd.DataFrame,
    x_col: str,
    color_col: str,
    title: str,
    color_map: dict[str, str] | None = None,
) -> go.Figure:
    """Create a stacked bar chart from a DataFrame."""
    pivot = df.pivot_table(
        index=x_col, columns=color_col, values="cnt",
        aggfunc="sum", fill_value=0,
    )

    fig = go.Figure()
    for col_name in pivot.columns:
        color = color_map.get(col_name, None) if color_map else None
        fig.add_trace(go.Bar(
            name=col_name,
            x=pivot.index.tolist(),
            y=pivot[col_name].tolist(),
            marker_color=color,
        ))

    fig.update_layout(
        barmode="stack",
        title=title,
        margin=dict(t=40, b=20, l=20, r=20),
        height=450,
        xaxis_tickangle=-45,
    )
    return fig
