import os
import re
import tempfile
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QFileDialog,
)
from PyQt5.QtGui import QGuiApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import sympy as sp


class FormulaWindow(QMainWindow):
    """Window to visualize formulas in a professional format."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parte 4 – Fórmulas")
        self._build_ui()
        self.resize(600, 400)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        input_layout = QHBoxLayout()
        self.edit = QLineEdit("As = Mu / (0.9 * fy * (d - a/2))")
        btn_show = QPushButton("Mostrar")
        btn_show.clicked.connect(self.show_formula)
        input_layout.addWidget(self.edit)
        input_layout.addWidget(btn_show)
        layout.addLayout(input_layout)

        self.fig, self.ax = plt.subplots(figsize=(5, 2))
        self.ax.axis("off")
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)

        btns = QHBoxLayout()
        self.btn_capture = QPushButton("Capturar")
        self.btn_capture.clicked.connect(self.capture)
        self.btn_export = QPushButton("Exportar…")
        self.btn_export.clicked.connect(self.export)
        btns.addWidget(self.btn_capture)
        btns.addWidget(self.btn_export)
        layout.addLayout(btns)

    # ------------------------------------------------------------------
    def _parse_formula(self, text: str) -> Optional[sp.Eq]:
        """Return a SymPy equation from linear text."""
        if "=" not in text:
            return None
        left, right = text.split("=", 1)
        left, right = left.strip(), right.strip()
        tokens = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text))
        symbols = {t: sp.symbols(t) for t in tokens}
        expr_l = symbols.get(left, sp.symbols(left))
        expr_r = sp.sympify(right.replace("^", "**"), locals=symbols)
        return sp.Eq(expr_l, expr_r)

    def show_formula(self):
        eq = self._parse_formula(self.edit.text())
        if eq is None:
            return
        latex = sp.latex(eq)
        self.ax.clear()
        self.ax.axis("off")
        self.ax.text(0.5, 0.5, f"${latex}$", ha="center", va="center", fontsize=12)
        self.canvas.draw()

    # ------------------------------------------------------------------
    def capture(self):
        """Copy the formula image to the clipboard."""
        self.canvas.repaint()
        QApplication.processEvents()
        pix = self.canvas.grab()
        QGuiApplication.clipboard().setPixmap(pix)

    def export(self):
        """Save the formula as PNG, PDF or DOCX."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar como",
            "",
            "PNG (*.png);;PDF (*.pdf);;Word (*.docx)",
        )
        if not path:
            return
        ext = os.path.splitext(path)[1].lower()
        if ext == ".docx":
            tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            tmp.close()
            self.fig.savefig(tmp.name, bbox_inches="tight", dpi=300)
            from docx import Document

            doc = Document()
            doc.add_picture(tmp.name)
            doc.save(path)
            os.unlink(tmp.name)
        else:
            self.fig.savefig(path, bbox_inches="tight")


if __name__ == "__main__":
    app = QApplication([])
    win = FormulaWindow()
    win.show()
    app.exec_()
