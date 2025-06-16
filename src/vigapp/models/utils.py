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
from matplotlib.figure import Figure


def draw_beam_section_png(b: float, h: float, r: float, de: float, db: float, path: str) -> str:
    """Draw a simple beam section and save it as PNG."""
    d = h - r - de - 0.5 * db
    fig = Figure(figsize=(2.4, 2.4))
    ax = fig.add_subplot(111)
    ax.set_aspect("equal")
    ax.axis("off")

    # Outer rectangle
    ax.plot([0, b, b, 0, 0], [0, 0, h, h, 0], "k-", linewidth=0.8)
    # Cover (continuous thin line)
    ax.plot(
        [r, b - r, b - r, r, r],
        [r, r, h - r, h - r, r],
        color="red",
        linestyle="-",
        linewidth=0.8,
    )
    # Stirrup offset (continuous thin line)
    off = r + de
    ax.plot(
        [off, b - off, b - off, off, off],
        [off, off, h - off, h - off, off],
        color="blue",
        linestyle="-",
        linewidth=0.8,
    )

    # Cover dimension r
    ax.annotate(
        "",
        xy=(b + 4, h),
        xytext=(b + 4, h - r),
        arrowprops=dict(arrowstyle="<->", linewidth=0.8, linestyle="-",
                        mutation_scale=6, shrinkA=0, shrinkB=0),
    )
    ax.text(b + 5, h - r / 2, f"r = {r:.1f} cm", va="center", fontsize=6)

    # Offset dimension de
    ax.annotate(
        "",
        xy=(b + 11, h - r),
        xytext=(b + 11, h - off),
        arrowprops=dict(arrowstyle="<->", linewidth=0.8, linestyle="-",
                        mutation_scale=6, shrinkA=0, shrinkB=0),
    )
    ax.text(b + 12, h - (r + off) / 2, f"de = {de:.1f} cm", va="center", fontsize=6)

    y_d = h - d
    ax.annotate(
        "",
        xy=(0, -5),
        xytext=(b, -5),
        arrowprops=dict(arrowstyle="<->", linewidth=0.8, linestyle="-",
                        mutation_scale=6, shrinkA=0, shrinkB=0),
    )
    ax.text(b / 2, -6, f"b = {b:.0f} cm", ha="center", va="top", fontsize=6)

    ax.annotate(
        "",
        xy=(-5, h),
        xytext=(-5, y_d),
        arrowprops=dict(arrowstyle="<->", linewidth=0.8, linestyle="-",
                        mutation_scale=6, shrinkA=0, shrinkB=0),
    )
    ax.text(-6, (h + y_d) / 2, f"d = {d:.1f} cm", ha="right", va="center", rotation=90, fontsize=6)

    ax.annotate(
        "",
        xy=(-12, 0),
        xytext=(-12, h),
        arrowprops=dict(arrowstyle="<->", linewidth=0.8, linestyle="-",
                        mutation_scale=6, shrinkA=0, shrinkB=0),
    )
    ax.text(-13, h / 2, f"h = {h:.0f} cm", ha="right", va="center", rotation=90, fontsize=6)

    ax.set_xlim(-15, b + 20)
    ax.set_ylim(-10, h + 10)

    fig.savefig(path, dpi=300, bbox_inches="tight")
    fig.clf()
    return path


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
    if text.startswith("$") and text.endswith("$"):
        latex = text.strip("$")
        return latex_image(latex, fontsize=fontsize)
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
