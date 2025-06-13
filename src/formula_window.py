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
    QComboBox,
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

        self._formulas = {
            # Reglas de corrección de momentos
            "Corrección Mp": "Mp_corr = Max(abs(Mp), f*abs(Mn), Mmax/4)",
            "Corrección Mn": "Mn_corr = -Max(abs(Mn), Mmax/4)",

            # Datos básicos
            "Peralte efectivo d": "d = h - r - phi_estribo - 0.5*phi_barra",
            "Coeficiente beta1": "beta1 = 0.85 - 0.05*(fc-280)/70",
            "p_balanceada": "p_bal = (0.85*fc*beta1/fy)*(6000/(6000+fy))",
            "p_maxima": "p_max = 0.75*p_bal",

            # Límites y verificaciones
            "As_min": "As_min = 0.7*sqrt(fc)/fy*b*d",
            "As_max": "As_max = p_max*b*d",
            "Base requerida": "b_req = 2*r + 2*phi_estribo + (n-1)*2.5 + sum_d",

            # Acero por momento último
            "As por momento": (
                "As = (1.7*fc*b*d)/(2*fy) - 0.5*sqrt((2.89*(fc*b*d)**2)/fy**2 - "
                "(6.8*fc*b*Mu)/(phi*fy**2))"
            ),
        }

        self._build_ui()
        self.setFixedSize(560, 720)

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.box = QComboBox()
        self.box.addItems(self._formulas.keys())
        self.box.currentIndexChanged.connect(self._formula_selected)
        layout.addWidget(self.box)

        input_layout = QHBoxLayout()
        self.edit = QLineEdit("As = Mu / (0.9 * fy * (d - a/2))")
        btn_show = QPushButton("Mostrar")
        btn_show.clicked.connect(self.show_formula)
        input_layout.addWidget(self.edit)
        input_layout.addWidget(btn_show)
        layout.addLayout(input_layout)

        self.fig, self.ax = plt.subplots(figsize=(4, 1.5))
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

    def _formula_selected(self, index: int):
        text = self.box.itemText(index)
        formula = self._formulas.get(text, "")
        if formula:
            self.edit.setText(formula)
            self.show_formula()

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
        self.ax.text(0.5, 0.5, f"${latex}$", ha="center", va="center", fontsize=10)
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
