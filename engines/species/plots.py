"""Plot builders for the species engine — no Streamlit.

Three output modes:
  data   — callers use :mod:`engines.species.queries` dicts/lists directly.
  png    — :func:`save_matplotlib_dashboard` writes a static PNG (Agg backend).
  plotly — :func:`build_plotly_figures` / :func:`write_plotly_dashboard`
           (+ ternary trait/guna plots); :func:`serve_html` serves locally.

Note: ternary (3-axis) plots are Plotly-only. The Matplotlib dashboard
covers kingdom pie, rank bars, top families and trait-by-kingdom bars.
"""

from __future__ import annotations

import functools
import http.server
import math
import webbrowser
from pathlib import Path

KINGDOM_COLORS = {
    "Animalia": "#e74c3c", "Plantae": "#2ecc71", "Fungi": "#9b59b6",
    "Chromista": "#f39c12", "Bacteria": "#3498db", "Archaea": "#1abc9c",
    "Protozoa": "#e67e22", "Viruses": "#95a5a6",
    "incertae sedis": "#bdc3c7", "Unknown": "#bdc3c7",
}


# ── Plotly ───────────────────────────────────────────────────────────────

def kingdom_pie_figure(kingdoms: dict):
    import plotly.graph_objects as go

    colors = [KINGDOM_COLORS.get(k, "#95a5a6") for k in kingdoms]
    fig = go.Figure(data=[go.Pie(
        labels=list(kingdoms.keys()), values=list(kingdoms.values()),
        marker=dict(colors=colors), textinfo="label+percent",
        hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>")])
    fig.update_layout(title="Species by Kingdom", height=400, margin=dict(t=40, b=20))
    return fig


def rank_bar_figure(ranks: dict):
    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Bar(
        x=list(ranks.keys()), y=list(ranks.values()), marker_color="#3498db",
        hovertemplate="%{x}: %{y:,}<extra></extra>")])
    fig.update_layout(title="Records by Taxon Rank", height=400, margin=dict(t=40, b=20))
    return fig


def top_families_figure(top_families: dict):
    import plotly.graph_objects as go

    fig = go.Figure(data=[go.Bar(
        y=list(top_families.keys()), x=list(top_families.values()),
        orientation="h", marker_color="#2ecc71",
        hovertemplate="%{y}: %{x:,}<extra></extra>")])
    fig.update_layout(title="Top 20 Families by Species Count", height=500,
                      margin=dict(t=40, b=20, l=150), yaxis=dict(autorange="reversed"))
    return fig


def trait_grouped_bar_figure(trait_by_kingdom: dict):
    import plotly.graph_objects as go

    kingdoms = list(trait_by_kingdom.keys())
    fig = go.Figure()
    for name, color, key in [("Mobility", "#3498db", "mobility"),
                             ("Warm-blooded", "#e74c3c", "warm_blood"),
                             ("Size", "#2ecc71", "size")]:
        fig.add_trace(go.Bar(name=name, x=kingdoms,
                             y=[trait_by_kingdom[k][key] for k in kingdoms],
                             marker_color=color))
    fig.update_layout(title="Average Trait Scores by Kingdom", barmode="group",
                      yaxis=dict(title="Score (0-1)", range=[0, 1]),
                      height=450, margin=dict(t=40, b=20))
    return fig


def ternary_figure(distribution: list[dict], mode: str = "physical"):
    """Ternary scatter of (mobility, warm_blood, size) or (purity, passion, ignorance)."""
    import plotly.graph_objects as go

    if mode == "physical":
        cols, titles = ("mobility", "warm_blood", "size"), ("Mobility", "Warm-blooded", "Size")
    elif mode == "guna":
        cols, titles = ("purity", "passion", "ignorance"), ("Purity (Sattva)", "Passion (Rajas)", "Ignorance (Tamas)")
    else:
        raise ValueError("mode must be 'physical' or 'guna'")

    eps = 0.001
    kingdoms = sorted({row["kingdom"] for row in distribution})
    fig = go.Figure()
    for kingdom in kingdoms:
        rows = [r for r in distribution if r["kingdom"] == kingdom]
        if not rows:
            continue
        fig.add_trace(go.Scatterternary(
            a=[r[cols[0]] + eps for r in rows],
            b=[r[cols[1]] + eps for r in rows],
            c=[r[cols[2]] + eps for r in rows],
            mode="markers", name=kingdom,
            marker=dict(
                size=[max(4, min(40, 3 * math.log10(max(r["count"], 1)) + 2)) for r in rows],
                color=KINGDOM_COLORS.get(kingdom, "#95a5a6"),
                line=dict(width=0.5, color="white"), opacity=0.8),
            text=[f"{r.get('class_name', '')}<br>{kingdom}<br>Species: {r['count']:,}<br>"
                  f"{titles[0]}: {r[cols[0]]:.3f}<br>{titles[1]}: {r[cols[1]]:.3f}<br>"
                  f"{titles[2]}: {r[cols[2]]:.3f}" for r in rows],
            hoverinfo="text"))
    fig.update_layout(
        ternary=dict(aaxis=dict(title=titles[0], min=0), baxis=dict(title=titles[1], min=0),
                     caxis=dict(title=titles[2], min=0)),
        height=700, margin=dict(t=40, b=40, l=60, r=60),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5))
    return fig


def build_plotly_figures(stats: dict, distribution: list[dict] | None = None) -> dict[str, object]:
    """Build standard species figures. Returns {name: plotly.Figure}."""
    figs: dict[str, object] = {}
    if stats.get("kingdoms"):
        figs["kingdom_pie"] = kingdom_pie_figure(stats["kingdoms"])
    if stats.get("ranks"):
        figs["rank_bar"] = rank_bar_figure(stats["ranks"])
    if stats.get("top_families"):
        figs["top_families"] = top_families_figure(stats["top_families"])
    if stats.get("trait_by_kingdom"):
        figs["traits_by_kingdom"] = trait_grouped_bar_figure(stats["trait_by_kingdom"])
    if distribution:
        figs["ternary_physical"] = ternary_figure(distribution, "physical")
        if distribution and "purity" in distribution[0]:
            figs["ternary_guna"] = ternary_figure(distribution, "guna")
    return figs


def write_plotly_dashboard(stats: dict, out_path: str | Path,
                           distribution: list[dict] | None = None) -> str:
    """Write all species figures to one interactive HTML file. Returns path."""
    from plotly.offline import plot

    figs = build_plotly_figures(stats, distribution)
    if not figs:
        raise ValueError("Nothing to plot: stats are empty.")
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    divs = [f"<h1>Species dashboard (n={stats.get('total', 0):,})</h1>"]
    include_js = True
    for name, fig in figs.items():
        divs.append(f"<h2>{name.replace('_', ' ').title()}</h2>")
        divs.append(plot(fig, output_type="div", include_plotlyjs=include_js,
                         show_link=False, config={"displaylogo": False}))
        include_js = False
    out.write_text("<!doctype html><html><head><meta charset='utf-8'>"
                   "<title>Species dashboard</title></head><body>"
                   + "\n".join(divs) + "</body></html>", encoding="utf-8")
    return str(out)


# ── Matplotlib (static PNG) ──────────────────────────────────────────────

def save_matplotlib_dashboard(stats: dict, out_path: str | Path) -> str:
    """Write a static 2x2 PNG dashboard (kingdoms, ranks, families, traits)."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 2, figsize=(13, 9))
    total = stats.get("total", 0)
    fig.suptitle(f"Species dashboard (n={total:,})", fontsize=14)

    ax = axes[0, 0]
    kingdoms = stats.get("kingdoms", {})
    if kingdoms:
        ax.pie(list(kingdoms.values()), labels=list(kingdoms.keys()), autopct="%1.0f%%",
               colors=[KINGDOM_COLORS.get(k, "#95a5a6") for k in kingdoms])
    ax.set_title("Species by kingdom")

    ax = axes[0, 1]
    ranks = stats.get("ranks", {})
    if ranks:
        ax.bar(list(ranks.keys()), list(ranks.values()), color="#3498db")
        ax.tick_params(axis="x", rotation=30)
    ax.set_title("Records by taxon rank")

    ax = axes[1, 0]
    fams = stats.get("top_families", {})
    if fams:
        top = list(fams.items())[:10]
        ax.barh([k for k, _ in reversed(top)], [v for _, v in reversed(top)], color="#2ecc71")
    ax.set_title("Top 10 families")

    ax = axes[1, 1]
    traits = stats.get("trait_by_kingdom", {})
    if traits:
        import numpy as np

        names = list(traits.keys())
        x = np.arange(len(names))
        w = 0.25
        ax.bar(x - w, [traits[k]["mobility"] for k in names], w, label="Mobility", color="#3498db")
        ax.bar(x, [traits[k]["warm_blood"] for k in names], w, label="Warm-blooded", color="#e74c3c")
        ax.bar(x + w, [traits[k]["size"] for k in names], w, label="Size", color="#2ecc71")
        ax.set_xticks(x)
        ax.set_xticklabels(names, rotation=30, ha="right", fontsize="small")
        ax.set_ylim(0, 1)
        ax.legend(fontsize="small")
    ax.set_title("Avg trait scores by kingdom")

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
