from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon


def _dim_vline(ax, y1, y2, x, label, offset=0.05):
    """Draw a vertical dimension line with a centered label."""
    ax.annotate(
        "",
        xy=(x, y1),
        xytext=(x, y2),
        arrowprops=dict(arrowstyle="<->", color="black", lw=1),
        annotation_clip=False,
    )
    ax.text(
        x + offset,
        (y1 + y2) / 2,
        label,
        ha="left",
        va="center",
        rotation=90,
        fontsize=9,
    )


def _dim_line(ax, x1, x2, y, label, offset=0.15):
    """Draw a dimension line with a centered label."""
    ax.annotate(
        "",
        xy=(x1, y),
        xytext=(x2, y),
        arrowprops=dict(arrowstyle="<->", color="black", lw=1),
        annotation_clip=False,
    )
    ax.text(
        (x1 + x2) / 2,
        y - offset,
        label,
        ha="center",
        va="top",
        fontsize=9,
    )


def draw_shear_scheme(
    ax: plt.Axes, Vu: float, ln: float, d: float, h: float, beam_type: str = "apoyada"
) -> None:
    """Draw a simple shear scheme on ``ax``.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis where the diagram is drawn.
    Vu : float
        Shear force in ton-force.
    ln : float
        Clear span in meters.
    d : float
        Effective depth in meters.
    beam_type : str
        Either ``"apoyada"`` or ``"volado"``.
    """
    ax.clear()

    support_w = 0.5
    column_h = 2.0
    y0 = 0
    margin = ln * 0.1
    arrow_len = 0.25
    dim_y1 = y0 - margin * 0.2
    dim_y2 = y0 - margin * 0.4

    structure_pts: list[tuple[float, float]]
    if beam_type == "volado":
        structure_pts = [
            (-support_w, y0 - column_h),
            (0, y0 - column_h),
            (0, y0),
            (ln, y0),
            (ln, y0 + h),
            (0, y0 + h),
            (-support_w, y0 + h),
        ]
    else:
        structure_pts = [
            (-support_w, y0 - column_h),
            (0, y0 - column_h),
            (0, y0),
            (ln, y0),
            (ln, y0 - column_h),
            (ln + support_w, y0 - column_h),
            (ln + support_w, y0 + h),
            (ln, y0 + h),
            (0, y0 + h),
            (-support_w, y0 + h),
        ]

    ax.add_patch(
        Polygon(structure_pts, closed=True, facecolor="0.9", edgecolor="black", linewidth=1)
    )

    # Shear diagram line
    if beam_type == "volado":
        ax.plot([0, ln], [h, 0], color="blue", lw=1)
    else:
        ax.plot([0, ln], [0, h], color="blue", lw=1)

    # Loads
    arrow_kwargs = dict(arrowstyle="-|>", color="red", lw=2)
    if beam_type == "volado":
        x_vu = d
        ax.annotate("", xy=(x_vu, h - d), xytext=(x_vu, h), arrowprops=arrow_kwargs)
        ax.text(x_vu, h + 0.05, "Vu", color="red", ha="center", va="bottom", fontsize=9)
        _dim_line(ax, 0, x_vu, dim_y1, "d")
        _dim_vline(ax, h, h - d, x_vu - margin * 0.2, "d")
        _dim_line(ax, 0, ln, dim_y2, f"ln = {ln:.2f} m")
        ax.set_xlim(-support_w - margin, ln + margin)
    else:
        for x_vu in (d, ln - d):
            ax.annotate("", xy=(x_vu, h - d), xytext=(x_vu, h), arrowprops=arrow_kwargs)
            ax.text(x_vu, h + 0.05, "Vu", color="red", ha="center", va="bottom", fontsize=9)
        _dim_line(ax, 0, d, dim_y1, "d")
        _dim_vline(ax, h, h - d, d - margin * 0.2, "d")
        _dim_line(ax, 0, ln / 2, dim_y1 - 0.1, "ln/2")
        _dim_line(ax, 0, ln, dim_y2, f"ln = {ln:.2f} m")
        ax.set_xlim(-margin, ln + margin + support_w)

    ax.axis("off")
    ax.set_ylim(y0 - column_h - margin * 0.3, h + margin * 0.6)


