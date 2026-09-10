"""Plot builders for the reverse-subtraction engine — no Streamlit.

Three output modes:
  data   — :func:`engines.reverse_subtraction.engine.compute_reverse_subtraction`
           + :func:`engines.reverse_subtraction.engine.compute_stats`.
  png    — :func:`save_matplotlib_png` (Agg backend).
  plotly — :func:`build_plotly_figure` / :func:`write_plotly_html`;
           :func:`serve_html` serves the HTML locally.
"""

from __future__ import annotations

import functools
import http.server
import webbrowser
from pathlib import Path


def build_plotly_figure(xs: list[int], ys: list[int], title: str | None = None):
    """Build an interactive Plotly line+marker figure."""
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys,
        mode="lines+markers" if len(xs) <= 500 else "lines",
        name="n - reverse(n)",
        line=dict(color="#3498db", width=1.5),
        marker=dict(size=3),
        hovertemplate="n = %{x}<br>n - reverse(n) = %{y}<extra></extra>"))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(
        title=title or f"n - reverse(n) for n = {xs[0]} to {xs[-1]}" if xs else "n - reverse(n)",
        xaxis_title="n", yaxis_title="n - reverse(n)", height=550, hovermode="x unified")
    return fig


def write_plotly_html(xs: list[int], ys: list[int], out_path: str | Path,
                      title: str | None = None) -> str:
    """Write an interactive Plotly HTML file. Returns path."""
    from plotly.offline import plot

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig = build_plotly_figure(xs, ys, title)
    plot(fig, filename=str(out), auto_open=False, include_plotlyjs=True,
         show_link=False, config={"displaylogo": False})
    return str(out)


def save_matplotlib_png(xs: list[int], ys: list[int], out_path: str | Path,
                        title: str | None = None) -> str:
    """Write a static Matplotlib PNG. Returns path."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(xs, ys, color="#3498db", linewidth=1.2,
            marker="." if len(xs) <= 500 else None, markersize=3)
    ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
    ax.set_title(title or (f"n - reverse(n) for n = {xs[0]} to {xs[-1]}" if xs else "n - reverse(n)"))
    ax.set_xlabel("n")
    ax.set_ylabel("n - reverse(n)")
    ax.grid(True, linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return str(out)


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
