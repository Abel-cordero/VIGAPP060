"""Helper utilities for unit conversions and styling."""

import base64
import io
from typing import Optional

from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget


def color_for_diameter(diam):
    """Return a color associated with a rebar diameter."""
    return "#000000"


def latex_image(latex: str, fontsize: int = 6) -> str:
    """Return an HTML ``<img>`` tag with a LaTeX expression rendered to PNG."""
    fontsize = min(fontsize, 6)
    fig = Figure(figsize=(0.01, 0.01))
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.text(0.5, 0.5, f"${latex}$", ha="center", va="center", fontsize=fontsize)
    buf = io.BytesIO()
    fig.savefig(
        buf,
        format="png",
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.0,
        transparent=True,
    )
    fig.clf()
    data = base64.b64encode(buf.getvalue()).decode()
    height = fontsize * 0.12
    style = f"height:{height:.2f}em;vertical-align:middle;"
    return f'<img src="data:image/png;base64,{data}" style="{style}"/>'


def latex_to_png(latex: str, path: str, *, fontsize: int = 12, dpi: int = 300) -> str:
    """Render a LaTeX expression to a PNG image.

    Parameters
    ----------
    latex:
        Fórmula en notación LaTeX.
    path:
        Ruta de salida para la imagen PNG.
    fontsize:
        Tamaño de letra de la fórmula.
    dpi:
        Resolución deseada en puntos por pulgada.

    Returns
    -------
    str
        La misma ruta de salida recibida.
    """
    fig = Figure(figsize=(0.01, 0.01))
    ax = fig.add_subplot(111)
    ax.axis("off")
    ax.text(0.5, 0.5, f"${latex}$", ha="center", va="center", fontsize=fontsize)
    fig.savefig(
        path,
        format="png",
        dpi=dpi,
        bbox_inches="tight",
        pad_inches=0.05,
        transparent=True,
    )
    fig.clf()
    return path


def capture_widget(widget: QWidget, path: str) -> Optional[str]:
    """Save a screenshot of ``widget`` as PNG and return the path."""
    if widget is None:
        return None
    pix = widget.grab()
    pix.save(path, "PNG")
    return path


import tempfile
import re
import sympy as sp


def parse_formula(text: str):
    """Parse a simple equation string into a SymPy Eq if possible."""
    if "=" not in text:
        return None
    left, right = text.split("=", 1)
    left, right = left.strip(), right.strip()
    tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text))
    symbols = {t: sp.symbols(t) for t in tokens}
    try:
        expr_l = symbols.get(left, sp.symbols(left))
        expr_r = sp.sympify(right.replace("^", "**"), locals=symbols)
    except Exception:
        return None
    return sp.Eq(expr_l, expr_r)


def formula_html(text: str, *, fontsize: int = 8) -> str:
    """Return HTML for ``text`` rendered as a LaTeX equation when possible."""
    eq = parse_formula(text)
    if eq is None:
        return f"<pre>{text}</pre>"
    latex = sp.latex(eq)
    return latex_image(latex, fontsize=fontsize)


def capture_widget_temp(widget: QWidget, prefix: str = "img") -> Optional[str]:
    """Capture a widget to a temporary PNG and return the path."""
    if widget is None:
        return None
    tmp = tempfile.NamedTemporaryFile(prefix=prefix, suffix=".png", delete=False)
    tmp.close()
    return capture_widget(widget, tmp.name)
