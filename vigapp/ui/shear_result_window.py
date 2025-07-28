from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from ..graphics.shear_scheme import draw_stirrup_distribution


class ShearResultWindow(QMainWindow):
    """Window that displays stirrup distribution and a summary."""

    def __init__(self, result, ln, *, Vu=0.0, beam_type="apoyada", parent=None, show_window=True):
        super().__init__(parent)
        self.result = result
        self.ln = ln
        self.Vu = Vu
        self.beam_type = beam_type
        self.setWindowTitle("Resultados Cortante")
        self._build_ui()
        if show_window:
            self.show()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.fig, self.ax = plt.subplots(figsize=(6, 3))
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        summary_lines = [
            f"Vu = {self.Vu:.2f} T",
            f"Vc = {self.result.Vc:.2f} T",
            f"Vs = {self.result.Vs:.2f} T",
            f"Lo = {self.result.Lo:.2f} m, n_sc = {self.result.n_sc}, S_sc = {self.result.S_sc:.2f} cm, sep real = {self.result.sep_sc_real:.2f} cm",
            f"Lc = {self.result.Lc:.2f} m, n_sr = {self.result.n_sr}, S_sr = {self.result.S_sr:.2f} cm, sep real = {self.result.sep_sr_real:.2f} cm",
        ]
        self.lbl_summary = QLabel("\n".join(summary_lines))
        self.lbl_summary.setAlignment(Qt.AlignTop)
        layout.addWidget(self.lbl_summary)

        draw_stirrup_distribution(self.ax, self.ln, self.result, self.beam_type)
        self.ax.set_title("Distribuci\u00f3n de estribos")
        self.canvas.draw()

