"""Simplified 2D/3D visualization for the beam design."""

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QLabel,
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
from matplotlib import patches
import numpy as np


DIAM_CM = {
    "6mm": 0.6,
    "8mm": 0.8,
    '3/8"': 0.95,
    "12mm": 1.2,
    '1/2"': 1.27,
    '5/8"': 1.59,
    '3/4"': 1.91,
    '1"': 2.54,
}

# Simple color mapping per diameter key
COLOR_MAP = {
    key: color for key, color in zip(
        DIAM_CM.keys(),
        list(mcolors.TABLEAU_COLORS.values())
    )
}

# Pre-generated noise texture for concrete-like appearance


class View3DWindow(QMainWindow):
    """Window that displays beam sections for M1, M2 and M3."""

    def __init__(self, design):
        super().__init__()
        self.design = design
        self.setWindowTitle("Desarrollo de Refuerzo")
        self.resize(800, 400)

        rng = np.random.default_rng(0)
        self.texture = rng.normal(loc=0.7, scale=0.1, size=(64, 64))
        self.texture = np.clip(self.texture, 0, 1)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("L (m)"))
        self.le_length = QLineEdit("1.0")
        self.le_length.setFixedWidth(60)
        self.le_length.editingFinished.connect(self.draw_views)
        input_layout.addWidget(self.le_length)
        layout.addLayout(input_layout)

        self.fig = plt.figure(figsize=(8, 3), constrained_layout=True)
        self.ax_sections = [self.fig.add_subplot(1, 3, i + 1) for i in range(3)]
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.draw_views()

    def draw_views(self):
        """Redraw the three section cuts."""
        try:
            b = float(self.design.edits["b (cm)"].text())
            h = float(self.design.edits["h (cm)"].text())
            r = float(self.design.edits["r (cm)"].text())
            _ = float(self.le_length.text())  # L is no longer used
        except ValueError:
            return

        de = DIAM_CM.get(self.design.cb_estribo.currentText(), 0)

        neg_layers = [self._collect_bars(i) for i in range(3)]
        pos_layers = [self._collect_bars(i + 3) for i in range(3)]
        titles = ["M1", "M2", "M3"]

        for ax, neg, pos, tit in zip(self.ax_sections, neg_layers, pos_layers, titles):
            self._plot_section(ax, neg, pos, b, h, r, de, tit)

        used_diams = set()
        for layers in neg_layers + pos_layers:
            for bars in layers.values():
                used_diams.update(key for _, key in bars)
        handles = [
            plt.Line2D([], [], marker='o', color=COLOR_MAP.get(d), linestyle='',
                       label=d)
            for d in used_diams
        ]
        if handles:
            self.fig.legend(handles=handles, title="Diámetros",
                            loc='lower center', ncol=len(handles))

        self.canvas.draw()

    # ------------------------------------------------------------------
    def _collect_bars(self, idx):
        """Return a dict of bars grouped by layer for a given index."""
        layers = {}
        for row in self.design.rebar_rows[idx]:
            try:
                qty = int(row["qty"].currentText()) if row["qty"].currentText() else 0
            except ValueError:
                qty = 0
            dia_key = row["dia"].currentText()
            dia = DIAM_CM.get(dia_key, 0)
            if qty <= 0 or dia == 0:
                continue
            layer = int(row["capa"].currentText()) if row["capa"].currentText() else 1
            layers.setdefault(layer, []).extend([(dia, dia_key)] * qty)
        return layers

    def _distribute_x(self, n, b, r, de, db1=0.0):
        """Return X coordinates for ``n`` bars within the clear width."""
        if n == 1:
            return [b / 2]
        width = b - 2 * (r + de) - db1
        spacing = width / (n - 1)
        start = r + de + db1 / 2
        return [start + i * spacing for i in range(n)]

    def _layer_positions_bottom(self, layers, r, de, offset=0.0):
        """Return Y positions of each layer from the bottom."""
        positions = {}
        base = r + de + offset
        prev_d = 0
        for layer in sorted(layers):
            diam_layer = max(d for d, _ in layers[layer])
            base += prev_d + (2.5 if layer > 1 else 0)
            positions[layer] = base + diam_layer / 2
            prev_d = diam_layer
        return positions

    def _layer_positions_top(self, layers, r, de, h, offset=0.0):
        """Return Y positions of each layer from the top."""
        positions = {}
        base = h - (r + de + offset)
        prev_d = 0
        for layer in sorted(layers):
            diam_layer = max(d for d, _ in layers[layer])
            base -= prev_d + (2.5 if layer > 1 else 0)
            positions[layer] = base - diam_layer / 2
            prev_d = diam_layer
        return positions

    def _bars_summary(self, layers):
        """Return a short text description of bars in all layers."""
        counts = {}
        for bars in layers.values():
            for _, key in bars:
                counts[key] = counts.get(key, 0) + 1
        parts = [f"{n}\u00f8{key}" for key, n in counts.items()]
        return " + ".join(parts)

    def _plot_section(self, ax, neg_layers, pos_layers, b, h, r, de, title):
        ax.clear()
        ax.set_aspect("equal")
        if self.texture is not None:
            ax.imshow(self.texture, extent=(0, b, 0, h), origin='lower', alpha=0.3)
        rect_bg = patches.Rectangle((0, 0), b, h, facecolor='lightgray', alpha=0.2)
        ax.add_patch(rect_bg)
        ax.plot([0, b, b, 0, 0], [0, 0, h, h, 0], "k-")
        ax.plot([r, b - r, b - r, r, r], [r, r, h - r, h - r, r], color="0.6", ls="--", lw=0.8)
        ax.plot(
            [r + de, b - r - de, b - r - de, r + de, r + de],
            [r + de, r + de, h - r - de, h - r - de, r + de],
            color="0.6",
            ls=":" ,
            lw=0.8,
        )

        db1_pos = max((d for d, _ in pos_layers.get(1, [])), default=0)
        db1_neg = max((d for d, _ in neg_layers.get(1, [])), default=0)
        db1 = max(db1_pos, db1_neg)

        bot_pos = self._layer_positions_bottom(pos_layers, r, de)
        for layer, bars in pos_layers.items():
            xs = self._distribute_x(len(bars), b, r, de, db1)
            y = bot_pos.get(layer, r + de)
            for x, (d, key) in zip(xs, bars):
                circ = plt.Circle((x, y), d / 2, color=COLOR_MAP.get(key, "b"), fill=False)
                ax.add_patch(circ)

        top_pos = self._layer_positions_top(neg_layers, r, de, h)
        for layer, bars in neg_layers.items():
            xs = self._distribute_x(len(bars), b, r, de, db1)
            y = top_pos.get(layer, h - r - de)
            for x, (d, key) in zip(xs, bars):
                circ = plt.Circle((x, y), d / 2, color=COLOR_MAP.get(key, "r"), fill=False)
                ax.add_patch(circ)
        # Place labels above and below the section instead of using the title
        neg_desc = self._bars_summary(neg_layers)
        pos_desc = self._bars_summary(pos_layers)
        ax.text(b / 2, h + 1.5, f"{title}- ({neg_desc})", ha="center", va="bottom", fontsize=8, color="b")
        ax.text(b / 2, -1.5, f"{title}+ ({pos_desc})", ha="center", va="top", fontsize=8, color="r")
        ax.set_xlim(-5, b + 5)
        ax.set_ylim(-5, h + 5)
        ax.axis("off")

