"""Simplified 2D/3D visualization for the beam design."""

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QApplication,
)
from PyQt5.QtGui import QGuiApplication
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

# Simple color mapping per diameter key using primary colors
COLOR_MAP = {
    key: ["red", "blue", "yellow"][i % 3]
    for i, key in enumerate(DIAM_CM.keys())
}

# Pre-generated noise texture for concrete-like appearance


class View3DWindow(QMainWindow):
    """Window that displays beam sections for M1, M2 and M3."""

    def __init__(self, design):
        super().__init__()
        self.design = design
        self.neg_orders = []
        self.pos_orders = []
        self.selected = None
        self.selected_patch = None
        self.dragging = False
        self.setWindowTitle("Desarrollo de Refuerzo")
        self.resize(800, 500)

        rng = np.random.default_rng(0)
        # Slightly darker texture for a gray concrete look
        self.texture = rng.normal(loc=0.6, scale=0.1, size=(64, 64))
        self.texture = np.clip(self.texture, 0, 1)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)



        self.fig = plt.figure(figsize=(8, 3), constrained_layout=True)
        self.ax_sections = [self.fig.add_subplot(1, 3, i + 1) for i in range(3)]
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        self.btn_capture = QPushButton("Capturar Vista")
        self.btn_capture.clicked.connect(self._capture_view)
        layout.addWidget(self.btn_capture)

        self.canvas.mpl_connect("pick_event", self._on_pick)
        self.canvas.mpl_connect("key_press_event", self._on_key)
        self.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.canvas.mpl_connect("button_release_event", self._on_release)

        self.draw_views()

    def draw_views(self):
        """Redraw the three section cuts."""
        try:
            b = float(self.design.edits["b (cm)"].text())
            h = float(self.design.edits["h (cm)"].text())
            r = float(self.design.edits["r (cm)"].text())
        except ValueError:
            return

        de = DIAM_CM.get(self.design.cb_estribo.currentText(), 0)

        neg_layers = [self._collect_bars(i) for i in range(3)]
        pos_layers = [self._collect_bars(i + 3) for i in range(3)]
        if not self.neg_orders:
            self.neg_orders = [self._collect_order(i) for i in range(3)]
        if not self.pos_orders:
            self.pos_orders = [self._collect_order(i + 3) for i in range(3)]
        titles = ["M1", "M2", "M3"]

        for idx, (ax, neg, pos, tit) in enumerate(zip(self.ax_sections, neg_layers, pos_layers, titles)):
            self._plot_section(ax, neg, pos, b, h, r, de, tit, idx)

        used_diams = set()
        for layers in neg_layers + pos_layers:
            for bars in layers.values():
                for _, key in bars:
                    used_diams.add(key)
        handles = [
            plt.Line2D([], [], marker='o', color=COLOR_MAP.get(d, 'black'),
                       linestyle='', label=f"\u00f8{d}")
            for d in sorted(used_diams)
        ]
        if handles:
            self.fig.legend(handles=handles, title="Di\u00e1metros",
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

    def _collect_order(self, idx):
        """Return a list of diameter keys respecting input order."""
        order = []
        for row in self.design.rebar_rows[idx]:
            try:
                qty = int(row["qty"].currentText()) if row["qty"].currentText() else 0
            except ValueError:
                qty = 0
            dia_key = row["dia"].currentText()
            if qty <= 0 or dia_key not in DIAM_CM:
                continue
            order.extend([dia_key] * qty)
        return order

    def change_order(self, sign, section, new_order):
        """Set a new bar order for a given section and redraw."""
        if sign not in ("pos", "neg"):
            return
        if not 0 <= section < 3:
            return
        if sign == "pos":
            self.pos_orders = self.pos_orders or [self._collect_order(i + 3) for i in range(3)]
            self.pos_orders[section] = list(new_order)
        else:
            self.neg_orders = self.neg_orders or [self._collect_order(i) for i in range(3)]
            self.neg_orders[section] = list(new_order)
        self.draw_views()

    def swap_bars(self, sign, section, i, j):
        """Swap two bars and redraw the view."""
        if sign not in ("pos", "neg"):
            return
        if not 0 <= section < 3:
            return
        orders = self.pos_orders if sign == "pos" else self.neg_orders
        if not orders:
            orders[:] = [self._collect_order(k + (3 if sign == "pos" else 0)) for k in range(3)]
        lst = orders[section]
        if not (0 <= i < len(lst) and 0 <= j < len(lst)):
            return
        lst[i], lst[j] = lst[j], lst[i]
        self.draw_views()

    def move_bar(self, sign, section, idx, new_idx):
        """Move a bar to a new index and redraw."""
        if sign not in ("pos", "neg"):
            return
        if not 0 <= section < 3:
            return
        orders = self.pos_orders if sign == "pos" else self.neg_orders
        if not orders:
            orders[:] = [self._collect_order(k + (3 if sign == "pos" else 0)) for k in range(3)]
        lst = orders[section]
        if not (0 <= idx < len(lst)):
            return
        new_idx = max(0, min(new_idx, len(lst) - 1))
        if idx == new_idx:
            return
        val = lst.pop(idx)
        lst.insert(new_idx, val)
        self.draw_views()

    def _distribute_x(self, n, b, r, de, db1=0.0):
        """Return X coordinates using blibre = b - 2*(r + de) - db1."""
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

    def _plot_section(self, ax, neg_layers, pos_layers, b, h, r, de, title, idx):
        ax.clear()
        ax.set_aspect("equal")
        if self.texture is not None:
            ax.imshow(self.texture, extent=(0, b, 0, h), origin='lower', alpha=0.2)
        rect_bg = patches.Rectangle((0, 0), b, h, facecolor='gray', alpha=0.15)
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

        orders_pos = self.pos_orders[idx] if idx < len(self.pos_orders) else []
        orders_neg = self.neg_orders[idx] if idx < len(self.neg_orders) else []

        pos_counts = [len(pos_layers.get(l, [])) for l in sorted(pos_layers)]
        neg_counts = [len(neg_layers.get(l, [])) for l in sorted(neg_layers)]

        pos_y = self._layer_positions_bottom(pos_layers, r, de)
        neg_y = self._layer_positions_top(neg_layers, r, de, h)

        start = 0
        for layer in sorted(pos_layers):
            bars = orders_pos[start:start + pos_counts.pop(0)] or [key for _, key in pos_layers[layer]]
            xs = self._distribute_x(len(bars), b, r, de)
            y = pos_y.get(layer, r + de)
            for j, (x, key) in enumerate(zip(xs, bars)):
                d = DIAM_CM.get(key, 0)
                circ = plt.Circle(
                    (x, y),
                    d / 2,
                    facecolor=COLOR_MAP.get(key, 'b'),
                    edgecolor="k",
                    lw=0.6,
                    alpha=0.6,
                    fill=True,
                    picker=True,
                )
                circ.set_gid(f"pos-{idx}-{start + j}")
                ax.add_patch(circ)
            start += len(bars)

        start = 0
        for layer in sorted(neg_layers):
            bars = orders_neg[start:start + neg_counts.pop(0)] or [key for _, key in neg_layers[layer]]
            xs = self._distribute_x(len(bars), b, r, de)
            y = neg_y.get(layer, h - (r + de))
            for j, (x, key) in enumerate(zip(xs, bars)):
                d = DIAM_CM.get(key, 0)
                circ = plt.Circle(
                    (x, y),
                    d / 2,
                    facecolor=COLOR_MAP.get(key, 'r'),
                    edgecolor="k",
                    lw=0.6,
                    alpha=0.6,
                    fill=True,
                    picker=True,
                )
                circ.set_gid(f"neg-{idx}-{start + j}")
                ax.add_patch(circ)
            start += len(bars)

        neg_desc = self._bars_summary(neg_layers)
        pos_desc = self._bars_summary(pos_layers)
        ax.text(b / 2, h + 1.5, f"{title}- ({neg_desc})", ha="center", va="bottom", fontsize=8, color="b")
        ax.text(b / 2, -1.5, f"{title}+ ({pos_desc})", ha="center", va="top", fontsize=8, color="r")
        ax.set_xlim(-5, b + 5)
        ax.set_ylim(-5, h + 5)
        ax.axis("off")

    # ------------------------------------------------------------------
    def _on_pick(self, event):
        artist = event.artist
        gid = getattr(artist, "get_gid", lambda: None)()
        if not gid:
            return
        try:
            sign, sec, idx = gid.split("-")
            sec = int(sec)
            idx = int(idx)
        except ValueError:
            return
        self.selected = (sign, sec, idx)
        self.selected_patch = artist
        self.dragging = True

    def _on_key(self, event):
        if not self.selected:
            return
        sign, sec, idx = self.selected
        orders = self.pos_orders if sign == "pos" else self.neg_orders
        lst = orders[sec]

        if event.key == "left" and idx > 0:
            self.swap_bars(sign, sec, idx, idx - 1)
            self.selected = (sign, sec, idx - 1)
        elif event.key == "right" and idx < len(lst) - 1:
            self.swap_bars(sign, sec, idx, idx + 1)
            self.selected = (sign, sec, idx + 1)
        else:
            return
        # redraw handled by swap_bars

    def _on_motion(self, event):
        if not self.dragging or self.selected_patch is None or event.xdata is None:
            return
        if event.inaxes not in self.ax_sections:
            return
        x, y = self.selected_patch.center
        self.selected_patch.center = (event.xdata, y)
        self.canvas.draw_idle()

    def _on_release(self, event):
        if not self.dragging or self.selected_patch is None or not self.selected:
            return
        if event.xdata is None:
            self.dragging = False
            self.selected_patch = None
            return
        sign, sec, idx = self.selected
        orders = self.pos_orders if sign == "pos" else self.neg_orders
        lst = orders[sec]
        try:
            b = float(self.design.edits["b (cm)"].text())
            r = float(self.design.edits["r (cm)"].text())
            de = DIAM_CM.get(self.design.cb_estribo.currentText(), 0)
        except ValueError:
            b = 0
            r = 0
            de = 0
        xs = self._distribute_x(len(lst), b, r, de)
        new_idx = min(range(len(xs)), key=lambda i: abs(xs[i] - event.xdata))
        self.move_bar(sign, sec, idx, new_idx)
        self.selected = (sign, sec, new_idx)
        self.dragging = False
        self.selected_patch = None

    def _capture_view(self):
        """Copy the canvas to the clipboard."""
        self.canvas.repaint()
        QApplication.processEvents()
        pix = self.canvas.grab()
        QGuiApplication.clipboard().setPixmap(pix)

