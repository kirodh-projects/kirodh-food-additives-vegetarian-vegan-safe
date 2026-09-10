"""Plot builders for the food-additives engine — no Streamlit.

Three output modes:
  data   — callers use :mod:`engines.food_additives.queries` dicts directly.
  png    — :func:`save_matplotlib_dashboard` writes a static PNG (Agg backend).
  plotly — :func:`build_plotly_figures` / :func:`write_plotly_dashboard`
           write an interactive HTML file; :func:`serve_html` serves it locally.
"""

from __future__ import annotations

import functools
import http.server
import re
import webbrowser
from pathlib import Path

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


def sanitise_key(name: str) -> str:
    """Make a string safe for filenames."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_") or "plot"


# ── Plotly ───────────────────────────────────────────────────────────────

def make_pie_chart(data: dict, title: str, color_map: dict | None = None):
    """Create a Plotly pie chart from {label: count}."""
    import plotly.graph_objects as go

    labels = list(data.keys())
    values = list(data.values())
    colors = [color_map.get(label, "#95a5a6") for label in labels] if color_map else None
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors) if colors else None,
        textinfo="label+percent",
        hovertemplate="%{label}: %{value} (%{percent})<extra></extra>",
    )])
    fig.update_layout(title=title, showlegend=True,
                      margin=dict(t=40, b=20, l=20, r=20), height=350)
    return fig


def make_bar_chart(data: dict, title: str, color_map: dict | None = None, horizontal: bool = False):
    """Create a Plotly bar chart from {label: count}."""
    import plotly.graph_objects as go

    labels = list(data.keys())
    values = list(data.values())
    colors = [color_map.get(label, "#3498db") for label in labels] if color_map else None
    if horizontal:
        fig = go.Figure(data=[go.Bar(
            y=labels, x=values, orientation="h", marker_color=colors,
            hovertemplate="%{y}: %{x}<extra></extra>")])
    else:
        fig = go.Figure(data=[go.Bar(
            x=labels, y=values, marker_color=colors,
            hovertemplate="%{x}: %{y}<extra></extra>")])
    fig.update_layout(title=title, margin=dict(t=40, b=20, l=20, r=20), height=400)
    return fig


def make_stacked_bar(df, x_col: str, color_col: str, title: str, color_map: dict | None = None):
    """Create a Plotly stacked bar chart from a DataFrame with a 'cnt' column."""
    import plotly.graph_objects as go

    pivot = df.pivot_table(index=x_col, columns=color_col, values="cnt",
                           aggfunc="sum", fill_value=0)
    fig = go.Figure()
    for col_name in pivot.columns:
        color = color_map.get(col_name) if color_map else None
        fig.add_trace(go.Bar(name=col_name, x=pivot.index.tolist(),
                             y=pivot[col_name].tolist(), marker_color=color))
    fig.update_layout(barmode="stack", title=title,
                      margin=dict(t=40, b=20, l=20, r=20),
                      height=450, xaxis_tickangle=-45)
    return fig


def build_plotly_figures(summary: dict, breakdown: list[dict] | None = None) -> dict[str, object]:
    """Build the standard analytics figures. Returns {name: plotly.Figure}."""
    import pandas as pd

    figs: dict[str, object] = {}
    if summary.get("vegan_status"):
        figs["vegan_pie"] = make_pie_chart(summary["vegan_status"], "Vegan Status", VEGAN_COLORS)
    if summary.get("vegetarian_status"):
        figs["vegetarian_pie"] = make_pie_chart(
            summary["vegetarian_status"], "Vegetarian Status (Lacto)", VEGAN_COLORS)
    if summary.get("halal_status"):
        figs["halal_pie"] = make_pie_chart(summary["halal_status"], "Halal Status", HALAL_COLORS)
    if summary.get("origin"):
        figs["origin_pie"] = make_pie_chart(summary["origin"], "Origin", ORIGIN_COLORS)
    if summary.get("safety_level"):
        figs["safety_bar"] = make_bar_chart(summary["safety_level"], "Safety Levels", SAFETY_COLORS)
    if summary.get("category"):
        top = dict(sorted(summary["category"].items(), key=lambda kv: kv[1], reverse=True)[:15])
        figs["category_bar"] = make_bar_chart(top, "Top 15 Categories")
    if breakdown:
        df = pd.DataFrame(breakdown)
        if not df.empty:
            figs["vegan_by_category"] = make_stacked_bar(
                df, "category", "vegan_status", "Vegan Status by Category", VEGAN_COLORS)
    return figs


def write_plotly_dashboard(summary: dict, out_path: str | Path,
                           breakdown: list[dict] | None = None) -> str:
    """Write all analytics figures to one interactive HTML file. Returns path."""
    from plotly.offline import get_plotlyjs_version, plot

    figs = build_plotly_figures(summary, breakdown)
    if not figs:
        raise ValueError("Nothing to plot: summary is empty.")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    divs = []
    include_js = True
    for name, fig in figs.items():
        divs.append(f"<h2>{name.replace('_', ' ').title()}</h2>")
        divs.append(plot(fig, output_type="div", include_plotlyjs=include_js,
                         show_link=False, config={"displaylogo": False}))
        include_js = False  # only embed plotly.js once
    html = (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>Food additives dashboard</title></head><body>"
            f"<h1>Food additives dashboard (plotly {get_plotlyjs_version()})</h1>"
            + "\n".join(divs) + "</body></html>")
    out.write_text(html, encoding="utf-8")
    return str(out)


# ── Matplotlib (static PNG) ──────────────────────────────────────────────

def save_matplotlib_dashboard(summary: dict, out_path: str | Path,
                              breakdown: list[dict] | None = None) -> str:
    """Write a static 2x2 PNG dashboard. Returns path."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    fig.suptitle(f"Food additives dashboard (n={summary.get('total', 0)})", fontsize=14)

    # Vegan pie
    ax = axes[0, 0]
    vegan = summary.get("vegan_status", {})
    if vegan:
        ax.pie(list(vegan.values()), labels=list(vegan.keys()), autopct="%1.0f%%",
               colors=[VEGAN_COLORS.get(k, "#95a5a6") for k in vegan])
    ax.set_title("Vegan status")

    # Safety bar
    ax = axes[0, 1]
    safety = summary.get("safety_level", {})
    if safety:
        ax.bar(list(safety.keys()), list(safety.values()),
               color=[SAFETY_COLORS.get(k, "#3498db") for k in safety])
        ax.tick_params(axis="x", rotation=30)
    ax.set_title("Safety levels")

    # Top categories bar
    ax = axes[1, 0]
    cats = summary.get("category", {})
    if cats:
        top = sorted(cats.items(), key=lambda kv: kv[1], reverse=True)[:10]
        ax.barh([k for k, _ in reversed(top)], [v for _, v in reversed(top)], color="#3498db")
    ax.set_title("Top 10 categories")

    # Vegan-by-category stacked bar (top 6 categories for readability)
    ax = axes[1, 1]
    if breakdown:
        import pandas as pd

        df = pd.DataFrame(breakdown)
        if not df.empty:
            pivot = df.pivot_table(index="category", columns="vegan_status",
                                   values="cnt", aggfunc="sum", fill_value=0)
            totals = pivot.sum(axis=1).sort_values(ascending=False).head(6).index
            pivot.loc[totals].plot(kind="barh", stacked=True, ax=ax,
                                   color=[VEGAN_COLORS.get(c, "#95a5a6") for c in pivot.columns])
            ax.legend(title="Vegan", fontsize="small")
    ax.set_title("Vegan by category (top 6)")

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return str(out)


# ── Local server ─────────────────────────────────────────────────────────

def serve_html(html_path: str | Path, port: int = 0, open_browser: bool = True) -> None:
    """Serve an HTML file over local HTTP (blocking until Ctrl-C)."""
    path = Path(html_path).resolve()
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(path.parent))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://127.0.0.1:{httpd.server_port}/{path.name}"
        print(f"Serving {path.name} at {url}  (Ctrl-C to stop)")
        if open_browser:
            try:
                webbrowser.open(url)
            except Exception:
                pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")
