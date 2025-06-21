"""Helper utilities for unit conversions and styling."""

from matplotlib.figure import Figure


def color_for_diameter(diam):
    """Return a color associated with a rebar diameter."""
    return "#000000"


def latex_image(latex: str, fontsize: int = 10) -> str:
    """Return HTML using MathJax for a LaTeX expression."""
    style = f"font-size:{fontsize}px"
    return f'<span style="{style}">\\({latex}\\)</span>'


