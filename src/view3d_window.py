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


class View3DWindow(QMainWindow):
    """Simple window showing 2D and 3D views of the beam."""

    def __init__(self, design):
        super().__init__()
        self.design = design
        self.setWindowTitle("Desarrollo de Refuerzo")
        self.resize(800, 900)

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

        self.fig = plt.figure(figsize=(8, 8), constrained_layout=True)
        gs = self.fig.add_gridspec(2, 3, height_ratios=[1, 2])
        self.ax_sections = [self.fig.add_subplot(gs[0, i]) for i in range(3)]
        self.ax3d = self.fig.add_subplot(gs[1, :], projection="3d")
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.draw_views()

    def draw_views(self):
        """Redraw the three sections and the 3D view."""
        try:
            b = float(self.design.edits["b (cm)"].text())
            h = float(self.design.edits["h (cm)"].text())
            r = float(self.design.edits["r (cm)"].text())
            L = float(self.le_length.text()) * 100
        except ValueError:
            return

        de = DIAM_CM.get(self.design.cb_estribo.currentText(), 0)

        neg_layers = [self._collect_bars(i) for i in range(3)]
        pos_layers = [self._collect_bars(i + 3) for i in range(3)]
        titles = ["M1", "M2", "M3"]

        for ax, neg, pos, tit in zip(self.ax_sections, neg_layers, pos_layers, titles):
            self._plot_section(ax, neg, pos, b, h, r, de, tit)

        self._plot_3d(b, h, r, de, L, pos_layers[0], neg_layers[0])

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

    def _distribute_x(self, n, b, r, de):
        if n == 1:
            return [b / 2]
        width = b - 2 * (r + de)
        spacing = width / (n - 1)
        return [r + de + i * spacing for i in range(n)]

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
        ax.plot([0, b, b, 0, 0], [0, 0, h, h, 0], "k-")
        ax.plot([r, b - r, b - r, r, r], [r, r, h - r, h - r, r], color="0.6", ls="--", lw=0.8)
        ax.plot(
            [r + de, b - r - de, b - r - de, r + de, r + de],
            [r + de, r + de, h - r - de, h - r - de, r + de],
            color="0.6",
            ls=":" ,
            lw=0.8,
        )

        extra = 3.0 if title == "M3" else 0.0
        bot_pos = self._layer_positions_bottom(pos_layers, r, de, offset=extra)
        for layer, bars in pos_layers.items():
            xs = self._distribute_x(len(bars), b, r, de)
            y = bot_pos.get(layer, r + de)
            for x, (d, key) in zip(xs, bars):
                circ = plt.Circle((x, y), d / 2, color=COLOR_MAP.get(key, "b"), fill=False)
                ax.add_patch(circ)

        top_pos = self._layer_positions_top(neg_layers, r, de, h, offset=extra)
        for layer, bars in neg_layers.items():
            xs = self._distribute_x(len(bars), b, r, de)
            y = top_pos.get(layer, h - r - de)
            for x, (d, key) in zip(xs, bars):
                circ = plt.Circle((x, y), d / 2, color=COLOR_MAP.get(key, "r"), fill=False)
                ax.add_patch(circ)
        neg_desc = self._bars_summary(neg_layers)
        pos_desc = self._bars_summary(pos_layers)
        label = f"{title}- ({neg_desc})\n{title}+ ({pos_desc})"
        ax.set_title(label, fontsize=9)
        ax.axis("off")

    def _plot_3d(self, b, h, r, de, L, pos_layers, neg_layers):
        self.ax3d.clear()
        verts = [
            (0, 0, 0),
            (b, 0, 0),
            (b, h, 0),
            (0, h, 0),
            (0, 0, 0),
            (0, 0, L),
            (b, 0, L),
            (b, 0, 0),
            (b, h, 0),
            (b, h, L),
            (b, 0, L),
            (0, 0, L),
            (0, h, L),
            (0, h, 0),
        ]
        for i in range(0, len(verts) - 1, 2):
            x1, y1, z1 = verts[i]
            x2, y2, z2 = verts[i + 1]
            self.ax3d.plot([x1, x2], [y1, y2], [z1, z2], "k-", lw=0.5)

        bot_pos = self._layer_positions_bottom(pos_layers, r, de, offset=3.0)
        for layer, bars in pos_layers.items():
            xs = self._distribute_x(len(bars), b, r, de)
            y = bot_pos.get(layer, r + de)
            for x, (d, key) in zip(xs, bars):
                self.ax3d.plot([x, x], [y, y], [0, L], color=COLOR_MAP.get(key, "r"), lw=3)

        top_pos = self._layer_positions_top(neg_layers, r, de, h, offset=3.0)
        for layer, bars in neg_layers.items():
            xs = self._distribute_x(len(bars), b, r, de)
            y = top_pos.get(layer, h - r - de)
            for x, (d, key) in zip(xs, bars):
                self.ax3d.plot([x, x], [y, y], [0, L], color=COLOR_MAP.get(key, "b"), lw=3)

        self.ax3d.set_xlim(0, b)
        self.ax3d.set_ylim(0, h)
        self.ax3d.set_zlim(0, L)
        self.ax3d.set_box_aspect((b, h, L))
        self.ax3d.axis("off")

