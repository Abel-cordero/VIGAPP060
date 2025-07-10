from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def _dim_line(ax, x1, x2, y, label, offset=0.15):
    ax.annotate(
        "",
        xy=(x1, y),
        xytext=(x2, y),
        arrowprops=dict(arrowstyle="<->", color="black", lw=1),
        annotation_clip=False,
    )
    ax.text((x1 + x2) / 2, y - offset, label, ha="center", va="top", fontsize=9)


def draw_shear_scheme(ax: plt.Axes, Vu: float, ln: float, d: float, beam_type: str = "apoyada") -> None:
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
    h = 0.4
    support_w = 0.2
    y0 = 0

    # Beam rectangle
    if beam_type == "volado":
        ax.add_patch(Rectangle((0, y0), ln, h, edgecolor="black", facecolor="none"))
        ax.add_patch(Rectangle((-support_w, y0), support_w, h, facecolor="0.7"))
        x_vu = ln - d
        ax.annotate(
            "",
            xy=(x_vu, h),
            xytext=(x_vu, h + 0.3),
            arrowprops=dict(arrowstyle="-|>", color="red", lw=2),
        )
        ax.text(x_vu, h + 0.32, "Vu", color="red", ha="center", va="bottom", fontsize=9)
        ax.plot([0, ln], [h, 0], color="blue", lw=1)
        _dim_line(ax, ln, x_vu, y0 - 0.1, "d")
        _dim_line(ax, 0, ln, y0 - 0.25, f"ln = {ln:.2f} m")
        ax.set_xlim(-support_w - 0.2, ln + 0.2)
    else:
        ax.add_patch(Rectangle((0, y0), ln, h, edgecolor="black", facecolor="none"))
        x_vu_left = d
        x_vu_right = ln - d
        for x_vu in (x_vu_left, x_vu_right):
            ax.annotate(
                "",
                xy=(x_vu, h),
                xytext=(x_vu, h + 0.3),
                arrowprops=dict(arrowstyle="-|>", color="red", lw=2),
            )
            ax.text(x_vu, h + 0.32, "Vu", color="red", ha="center", va="bottom", fontsize=9)
        ax.plot([0, ln], [h, 0], color="blue", lw=1)
        _dim_line(ax, 0, d, y0 - 0.1, "d")
        _dim_line(ax, ln/2, ln, y0 - 0.1, "ln/2")
        _dim_line(ax, 0, ln, y0 - 0.25, f"ln = {ln:.2f} m")
        ax.set_xlim(-0.2, ln + 0.2)

    ax.axis("off")
    ax.set_ylim(-0.5, h + 0.5)

