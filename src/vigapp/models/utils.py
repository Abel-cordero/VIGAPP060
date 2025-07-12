"""Helper utilities for unit conversions and styling."""

from typing import Optional

from matplotlib.figure import Figure
from PyQt5.QtWidgets import QWidget
from matplotlib.patches import Rectangle


def color_for_diameter(diam):
    """Return a color associated with a rebar diameter."""
    return "#000000"


def latex_image(latex: str, fontsize: int = 6) -> str:
    """Return HTML using MathJax for a LaTeX expression."""
    style = f"font-size:{fontsize}px"
    return f'<span style="{style}">\\({latex}\\)</span>'


def latex_to_png(latex: str, path: str, *, fontsize: int = 12, dpi: int = 300) -> str:
    """Deprecated helper kept for backwards compatibility."""
    raise NotImplementedError("LaTeX a PNG deshabilitado")


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


def draw_beam_section_png(b: float, h: float, r: float, de: float, db: float, path: str) -> str:
    """Draw a simple beam section and save it as PNG."""
    d = h - r - de - 0.5 * db
    fig = Figure(figsize=(2.4, 2.4))
    ax = fig.add_subplot(111)
    ax.set_aspect("equal")
    ax.axis("off")

    # Outer rectangle
    lw = 0.6
    ax.plot([0, b, b, 0, 0], [0, 0, h, h, 0], "k-", linewidth=lw)
    # Cover (continuous thin line)
    ax.plot(
        [r, b - r, b - r, r, r],
        [r, r, h - r, h - r, r],
        color="red",
        linestyle="-",
        linewidth=lw,
    )
    # Stirrup offset (continuous thin line)
    off = r + de
    ax.plot(
        [off, b - off, b - off, off, off],
        [off, off, h - off, h - off, off],
        color="blue",
        linestyle="-",
        linewidth=lw,
    )

    tick = 0.8

    def _dim_v(x, y1, y2, label, off_side="right"):
        ax.plot([x, x], [y1, y2], color="black", linewidth=lw)
        ax.plot([x - tick, x + tick], [y1, y1], color="black", linewidth=lw)
        ax.plot([x - tick, x + tick], [y2, y2], color="black", linewidth=lw)
        if off_side == "right":
            ax.text(x + 1.5 * tick, (y1 + y2) / 2, label, va="center", fontsize=6)
        else:
            ax.text(x - 1.5 * tick, (y1 + y2) / 2, label, ha="right", va="center", fontsize=6, rotation=90)

    def _dim_h(x1, x2, y, label):
        ax.plot([x1, x2], [y, y], color="black", linewidth=lw)
        ax.plot([x1, x1], [y - tick, y + tick], color="black", linewidth=lw)
        ax.plot([x2, x2], [y - tick, y + tick], color="black", linewidth=lw)
        ax.text((x1 + x2) / 2, y - 1.5 * tick, label, ha="center", va="top", fontsize=6)

    _dim_v(b + 4, h, h - r, f"r = {r:.1f} cm")
    _dim_v(b + 11, h - r, h - off, f"ϕ = {de:.1f} cm")

    y_d = h - d
    _dim_h(0, b, -5, f"b = {b:.0f} cm")
    _dim_v(-5, h, y_d, f"d = {d:.1f} cm", off_side="left")
    _dim_v(-12, 0, h, f"h = {h:.0f} cm", off_side="left")

    ax.set_xlim(-15, b + 20)
    ax.set_ylim(-10, h + 10)

    fig.savefig(path, dpi=300, bbox_inches="tight")
    fig.clf()
    return path


def draw_beam_elevation_png(L: float, h: float, cantilever: bool, path: str) -> str:
    """Draw a simple beam elevation with one or two columns."""
    fig = Figure(figsize=(4.0, 1.6))
    ax = fig.add_subplot(111)
    ax.set_aspect("equal")
    ax.axis("off")

    col_w = 30.0
    lw = 0.6

    # Beam outline
    ax.plot([0, L, L, 0, 0], [0, 0, h, h, 0], "k-", linewidth=lw)

    col_h = h * 1.2
    y_base = -0.2 * h
    cols = [0] if cantilever else [0, L]
    for x in cols:
        rect = Rectangle((x - col_w / 2, y_base), col_w, col_h,
                         edgecolor="0.3", facecolor="0.85", linewidth=lw)
        ax.add_patch(rect)

    tick = h * 0.05

    def _dim_h(x1, x2, y, label):
        ax.plot([x1, x2], [y, y], color="black", linewidth=lw)
        ax.plot([x1, x1], [y - tick, y + tick], color="black", linewidth=lw)
        ax.plot([x2, x2], [y - tick, y + tick], color="black", linewidth=lw)
        ax.text((x1 + x2) / 2, y - 2 * tick, label, ha="center", va="top", fontsize=6)

    def _dim_v(x, y1, y2, label):
        ax.plot([x, x], [y1, y2], color="black", linewidth=lw)
        ax.plot([x - tick, x + tick], [y1, y1], color="black", linewidth=lw)
        ax.plot([x - tick, x + tick], [y2, y2], color="black", linewidth=lw)
        ax.text(x + 2 * tick, (y1 + y2) / 2, label, va="center", fontsize=6)

    _dim_h(0, L, y_base - 3 * tick, f"l = {L/100:.2f} m")
    _dim_v(L + 4 * tick, 0, h, f"h = {h:.0f} cm")

    ax.set_xlim(-col_w, L + col_w)
    ax.set_ylim(y_base - 4 * tick, h + col_h * 0.1)

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
        return f'<span style="font-size:{fontsize}px">\\({latex}\\)</span>'
    eq = parse_formula(text)
    if eq is None:
        return f"<pre>{text}</pre>"
    latex = sp.latex(eq)
    return f'<span style="font-size:{fontsize}px">\\({latex}\\)</span>'


def capture_widget_temp(widget: QWidget, prefix: str = "img") -> Optional[str]:
    """Capture a widget to a temporary PNG and return the path."""
    if widget is None:
        return None
    tmp = tempfile.NamedTemporaryFile(prefix=prefix, suffix=".png", delete=False)
    tmp.close()
    return capture_widget(widget, tmp.name)
