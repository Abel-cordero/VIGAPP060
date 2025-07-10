"""Plotting helpers for the design window."""
from matplotlib.axes import Axes
import numpy as np


def draw_section(ax: Axes, b: float, h: float, r: float, d: float) -> None:
    """Draw a schematic beam section."""
    y_d = h - d
    ax.clear()
    ax.set_aspect("equal")
    ax.plot([0, b, b, 0, 0], [0, 0, h, h, 0], "k-")
    ax.plot([r, b - r, b - r, r, r], [r, r, h - r, h - r, r], "r--")
    ax.annotate("", xy=(0, -5), xytext=(b, -5), arrowprops=dict(arrowstyle="<->"))
    ax.text(b / 2, -6, f"b = {b:.0f} cm", ha="center", va="top", fontsize=8)
    ax.annotate("", xy=(-5, h), xytext=(-5, y_d), arrowprops=dict(arrowstyle="<->"))
    ax.text(-6, (h + y_d) / 2, f"d = {d:.1f} cm", ha="right", va="center", rotation=90, fontsize=8)
    ax.annotate("", xy=(-12, 0), xytext=(-12, h), arrowprops=dict(arrowstyle="<->"))
    ax.text(-13, h / 2, f"h = {h:.0f} cm", ha="right", va="center", rotation=90, fontsize=8)
    ax.set_xlim(-15, b + 10)
    ax.set_ylim(-10, h + 10)
    ax.axis("off")


def plot_required(ax: Axes, areas_n, areas_p) -> None:
    """Plot required steel areas."""
    x_ctrl = [0.0, 0.5, 1.0]
    ax.clear()
    ax.plot([0, 1], [0, 0], "k-", lw=6)
    y_off = 0.1 * max(np.max(areas_n), np.max(areas_p), 1)
    label_off = 0.2 * y_off
    for idx, (x, a) in enumerate(zip(x_ctrl, areas_n), 1):
        ax.text(x, y_off, f"As- {a:.2f}", ha="center", va="bottom", color="b", fontsize=9)
        ax.text(x, label_off, f"M{idx}-", ha="center", va="bottom", fontsize=7)
    for idx, (x, a) in enumerate(zip(x_ctrl, areas_p), 1):
        ax.text(x, -y_off, f"As+ {a:.2f}", ha="center", va="top", color="r", fontsize=9)
        ax.text(x, -label_off, f"M{idx}+", ha="center", va="top", fontsize=7)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-2 * y_off, 2 * y_off)
    ax.axis("off")


def plot_design(ax: Axes, areas, statuses) -> None:
    """Plot selected reinforcement."""
    x_ctrl = [0.0, 0.5, 1.0]
    areas_n = areas[:3]
    areas_p = areas[3:]
    ax.clear()
    ax.plot([0, 1], [0, 0], "k-", lw=6)
    y_off = 0.1 * max(max(areas_n, default=0), max(areas_p, default=0), 1)
    label_off = 0.2 * y_off
    for idx, (x, a, st) in enumerate(zip(x_ctrl, areas_n, statuses[:3]), 1):
        ax.text(x, y_off, f"Asd- {a:.2f} {st}", ha="center", va="bottom", color="g", fontsize=9)
        ax.text(x, label_off, f"M{idx}-", ha="center", va="bottom", fontsize=7)
    for idx, (x, a, st) in enumerate(zip(x_ctrl, areas_p, statuses[3:]), 1):
        ax.text(x, -y_off, f"Asd+ {a:.2f} {st}", ha="center", va="top", color="g", fontsize=9)
        ax.text(x, -label_off, f"M{idx}+", ha="center", va="top", fontsize=7)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-2 * y_off, 2 * y_off)
    ax.axis("off")

