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


class View3DWindow(QMainWindow):
    """Simple window showing 2D and 3D views of the beam."""

    def __init__(self, design):
        super().__init__()
        self.design = design
        self.setWindowTitle("Desarrollo de Refuerzo")

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

        self.fig = plt.figure(figsize=(8, 4), constrained_layout=True)
        self.ax2d = self.fig.add_subplot(1, 2, 1)
        self.ax3d = self.fig.add_subplot(1, 2, 2, projection="3d")
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        self.draw_views()

    def draw_views(self):
        try:
            b = float(self.design.edits["b (cm)"].text())
            h = float(self.design.edits["h (cm)"].text())
            r = float(self.design.edits["r (cm)"].text())
            L = float(self.le_length.text()) * 100
        except ValueError:
            return
        de = DIAM_CM.get(self.design.cb_estribo.currentText(), 0)
        db = DIAM_CM.get(self.design.cb_varilla.currentText(), 0)

        self.ax2d.clear()
        self.ax2d.set_aspect("equal")
        self.ax2d.plot([0, b, b, 0, 0], [0, 0, h, h, 0], "k-")
        yb = r + de + db / 2
        xs = [r + de + db / 2, b - r - de - db / 2]
        for x in xs:
            circ = plt.Circle((x, yb), db / 2, color="b", fill=False)
            self.ax2d.add_patch(circ)
        self.ax2d.axis("off")

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

        for x in xs:
            self.ax3d.plot([x, x], [yb, yb], [0, L], "r-", lw=2)

        self.ax3d.set_xlim(0, b)
        self.ax3d.set_ylim(0, h)
        self.ax3d.set_zlim(0, L)
        self.ax3d.set_box_aspect((b, h, L))
        self.ax3d.axis("off")

        self.canvas.draw()

