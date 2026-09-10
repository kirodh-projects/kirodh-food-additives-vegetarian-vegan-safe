"""Plot builders for the math-plotter engine — no Streamlit.

Three output modes:
  data   — :func:`engines.math_plotter.engine.compute_transformed_function`.
  png    — :func:`save_matplotlib_png` (Agg backend).
  plotly — :func:`build_plotly_figure` / :func:`write_plotly_html`;
           :func:`serve_html` serves the HTML locally.
"""

from __future__ import annotations

import functools
import http.server
import webbrowser
from collections.abc import Callable, Sequence
from pathlib import Path

COLORS = ["#e74c3c", "#2ecc71", "#f39c12", "#9b59b6", "#1abc9c",
          "#e67e22", "#3498db", "#e91e63", "#00bcd4", "#ff5722"]


def _check_functions(selected: Sequence[str], available: dict) -> list[str]:
    unknown = [name for name in selected if name not in available]
    if unknown:
        raise ValueError(f"Unknown function(s) {unknown}. Available: {sorted(available)}")
    return list(selected)


def build_plotly_figure(computed: dict[str, tuple[list, list, list]],
                        x_min: float, x_max: float, title: str | None = None):
    """Build an interactive Plotly figure from precomputed transforms.

    ``computed`` maps function name -> (new_x, new_y, skipped_x).
    """
    import numpy as np
    import plotly.graph_objects as go

    fig = go.Figure()
    px = np.linspace(x_min, x_max, 2000)
    fig.add_trace(go.Scatter(x=px, y=px ** 2, mode="lines",
                             name="Parabola (curved axis)",
                             line=dict(color="royalblue", width=2)))
    for i, (name, (new_x, new_y, skipped_x)) in enumerate(computed.items()):
        color = COLORS[i % len(COLORS)]
        fig.add_trace(go.Scatter(x=new_x, y=new_y, mode="lines", name=f"y = {name}",
                                 line=dict(color=color, width=2)))
        if skipped_x:
            fig.add_trace(go.Scatter(x=list(skipped_x), y=[0] * len(skipped_x),
                                     mode="markers", name=f"Out of range ({name})",
                                     marker=dict(symbol="star", color="orange", size=6)))
    fig.update_layout(
        title=title or "Parabolic Axis Transformation",
        xaxis=dict(title="x", zeroline=True, zerolinewidth=2, zerolinecolor="black",
                   gridcolor="rgba(0,0,0,0.1)"),
        yaxis=dict(title="y", zeroline=True, zerolinewidth=1,
                   zerolinecolor="rgba(0,0,0,0.3)", gridcolor="rgba(0,0,0,0.1)"),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        height=600, hovermode="closest")
    return fig


def write_plotly_html(computed: dict[str, tuple[list, list, list]],
                      out_path: str | Path, x_min: float, x_max: float,
                      title: str | None = None) -> str:
    """Write an interactive Plotly HTML file. Returns path."""
    from plotly.offline import plot

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig = build_plotly_figure(computed, x_min, x_max, title)
    plot(fig, filename=str(out), auto_open=False, include_plotlyjs=True,
         show_link=False, config={"displaylogo": False})
    return str(out)


def save_matplotlib_png(computed: dict[str, tuple[list, list, list]],
                        out_path: str | Path, x_min: float, x_max: float,
                        title: str | None = None) -> str:
    """Write a static Matplotlib PNG. Returns path."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 7))
    px = np.linspace(x_min, x_max, 2000)
    ax.plot(px, px ** 2, color="royalblue", linewidth=2, label="Parabola (curved axis)")
    for i, (name, (new_x, new_y, skipped_x)) in enumerate(computed.items()):
        color = COLORS[i % len(COLORS)]
        ax.plot(new_x, new_y, color=color, linewidth=2, label=f"y = {name}")
        if skipped_x:
            ax.plot(list(skipped_x), [0] * len(skipped_x), marker="*", linestyle="",
                    color="orange", markersize=6, label=f"Out of range ({name})")
    ax.set_title(title or "Parabolic Axis Transformation")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(fontsize="small")
    fig.tight_layout()
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return str(out)


def compute_selected(functions: dict[str, Callable], selected: Sequence[str],
                     x_min: float, x_max: float,
                     n_points: int = 500) -> dict[str, tuple[list, list, list]]:
    """Compute transforms for the selected preset names (lazy engine import)."""
    from .engine import compute_transformed_function

    names = _check_functions(selected, functions)
    return {name: compute_transformed_function(functions[name], x_min, x_max, n_points)
            for name in names}


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
