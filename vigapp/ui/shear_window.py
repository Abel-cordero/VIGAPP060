# -*- coding: utf-8 -*-
"""Simple window for shear design."""

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt


class ShearDesignWindow(QMainWindow):
    """UI to input Vu and plot a linear shear diagram."""

    def __init__(self, design_win, parent=None, *, show_window=True,
                 menu_callback=None, back_callback=None):
        super().__init__(parent)
        self.design_win = design_win
        self.menu_callback = menu_callback
        self.back_callback = back_callback
        self.setWindowTitle("Dise\u00f1o por Cortante")
        self._build_ui()
        self.resize(600, 500)
        if show_window:
            self.show()

    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QGridLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(10)

        self.ed_vu = QLineEdit("0.0")
        self.ed_vu.setAlignment(Qt.AlignRight)
        self.ed_ln = QLineEdit("5.0")
        self.ed_ln.setAlignment(Qt.AlignRight)

        d_val = self.design_win.calc_effective_depth()
        self.ed_d = QLineEdit(f"{d_val:.2f}")
        self.ed_d.setReadOnly(True)
        self.ed_d.setAlignment(Qt.AlignRight)

        layout.addWidget(QLabel("Vu (T)"), 0, 0)
        layout.addWidget(self.ed_vu, 0, 1)
        layout.addWidget(QLabel("Ln (m)"), 1, 0)
        layout.addWidget(self.ed_ln, 1, 1)
        layout.addWidget(QLabel("d (cm)"), 2, 0)
        layout.addWidget(self.ed_d, 2, 1)

        btn_menu = QPushButton("Men\u00fa")
        btn_back = QPushButton("Atr\u00e1s")
        layout.addWidget(btn_menu, 3, 0)
        layout.addWidget(btn_back, 3, 1)

        self.fig, self.ax = plt.subplots(figsize=(5, 3), constrained_layout=True)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas, 4, 0, 1, 2)

        self.ed_vu.editingFinished.connect(self.draw_diagram)
        self.ed_ln.editingFinished.connect(self.draw_diagram)
        btn_menu.clicked.connect(self.on_menu)
        btn_back.clicked.connect(self.on_back)

        self.draw_diagram()

    # ------------------------------------------------------------------
    def draw_diagram(self):
        try:
            Vu = float(self.ed_vu.text())
            L = float(self.ed_ln.text())
            d_cm = float(self.ed_d.text())
        except ValueError:
            return

        d = d_cm / 100.0
        x = [0, d, L - d, L]
        y = [0, Vu, Vu, 0]

        self.ax.clear()
        self.ax.plot(x, y, "b-", lw=2)
        self.ax.set_xlabel("Longitud (m)")
        self.ax.set_ylabel("Cortante (T)")
        self.ax.grid(True)
        self.canvas.draw()

    # ------------------------------------------------------------------
    def on_menu(self):
        if self.menu_callback:
            self.menu_callback()

    def on_back(self):
        if self.back_callback:
            self.back_callback()
        else:
            self.close()
            parent = self.parent()
            if parent:
                parent.show()

