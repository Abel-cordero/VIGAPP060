"""Helper utilities for unit conversions and styling."""

import base64
import io

from matplotlib.figure import Figure


def color_for_diameter(diam):
    """Return a color associated with a rebar diameter."""
    return "#000000"


def latex_image(latex: str, fontsize: int = 10) -> str:
    """Return an HTML ``<img>`` tag with a LaTeX expression rendered to PNG."""
    fig = Figure(figsize=(0.00, 0.001))
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.text(0.05, 0.05, f"${latex}$", ha="center", va="center", fontsize=fontsize)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight", transparent=True)
    fig.clf()
    data = base64.b64encode(buf.getvalue()).decode()
    style = "height:0.1em;vertical-align:middle;"
    return f'<img src="data:image/png;base64,{data}" style="{style}"/>'


