# Simplified shear design window based on flexion design logic
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QComboBox,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from ..models.constants import DIAM_CM, BAR_DATA
from ..models.utils import draw_beam_section_png

import math


class ShearDesignWindow(QMainWindow):
    """Very basic window for shear reinforcement design."""

    def __init__(self, section_defaults=None, parent=None, *, show_window=True):
        super().__init__(parent)
        self.setWindowTitle("Dise\u00f1o por Cortante")
        self.section_defaults = section_defaults or {}
        self._build_ui()
        self.resize(800, 600)
        if show_window:
            self.show()

    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QGridLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(10)

        # Inputs for shear design
        layout.addWidget(QLabel("VU"), 0, 0)
        self.ed_vu = QLineEdit("0.0")
        self.ed_vu.setAlignment(Qt.AlignRight)
        layout.addWidget(self.ed_vu, 0, 1)
        self.cb_vu_unit = QComboBox()
        self.cb_vu_unit.addItems(["tnf", "kgf", "kN"])
        layout.addWidget(self.cb_vu_unit, 0, 2)

        layout.addWidget(QLabel("LN (m)"), 1, 0)
        self.ed_ln = QLineEdit("3.0")
        self.ed_ln.setAlignment(Qt.AlignRight)
        layout.addWidget(self.ed_ln, 1, 1)

        self.rb_dual1 = QRadioButton("Dual 1")
        self.rb_dual2 = QRadioButton("Dual 2")
        self.rb_dual2.setChecked(True)
        bg = QButtonGroup(self)
        bg.addButton(self.rb_dual1)
        bg.addButton(self.rb_dual2)
        layout.addWidget(QLabel("Sistema:"), 2, 0)
        layout.addWidget(self.rb_dual1, 2, 1)
        layout.addWidget(self.rb_dual2, 2, 2)

        btn_calc = QPushButton("Calcular")
        btn_calc.clicked.connect(self.on_calculate)
        layout.addWidget(btn_calc, 3, 2)

        # Section info side panel
        side = QGridLayout()
        layout.addLayout(side, 0, 3, 4, 1)

        labels = [
            ("b (cm)", "30"),
            ("h (cm)", "50"),
            ("r (cm)", "4"),
            ("f'c (kg/cm²)", "210"),
            ("fy (kg/cm²)", "4200"),
        ]
        self.section_edits = {}
        for row, (text, val) in enumerate(labels):
            lbl = QLabel(text)
            side.addWidget(lbl, row, 0)
            ed = QLineEdit(self.section_defaults.get(text, val))
            ed.setAlignment(Qt.AlignRight)
            side.addWidget(ed, row, 1)
            self.section_edits[text] = ed

        side.addWidget(QLabel("\u03d5 estribo"), len(labels), 0)
        self.cb_estribo = QComboBox()
        self.cb_estribo.addItems(["8mm", '3/8"', '1/2"'])
        self.cb_estribo.setCurrentText('3/8"')
        side.addWidget(self.cb_estribo, len(labels), 1)

        side.addWidget(QLabel("\u03d5 barra"), len(labels)+1, 0)
        self.cb_barra = QComboBox()
        self.cb_barra.addItems(['1/2"', '5/8"', '3/4"', '1"'])
        self.cb_barra.setCurrentText('1/2"')
        side.addWidget(self.cb_barra, len(labels)+1, 1)

        self.fig, self.ax = plt.subplots(figsize=(3,3), constrained_layout=True)
        self.canvas = FigureCanvas(self.fig)
        side.addWidget(self.canvas, 0, 2, len(labels)+2, 1)
        self.draw_section()

        # Results label
        self.lbl_result = QLabel("")
        layout.addWidget(self.lbl_result, 4, 0, 1, 4)

    # ------------------------------------------------------------------
    def draw_section(self):
        try:
            b = float(self.section_edits["b (cm)"].text())
            h = float(self.section_edits["h (cm)"].text())
            r = float(self.section_edits["r (cm)"].text())
            de = DIAM_CM.get(self.cb_estribo.currentText(), 0)
            db = DIAM_CM.get(self.cb_barra.currentText(), 0)
        except ValueError:
            return
        path = draw_beam_section_png(b, h, r, de, db, "/tmp/sec.png")
        self.ax.clear()
        img = plt.imread(path)
        self.ax.imshow(img)
        self.ax.axis("off")
        self.canvas.draw()

    # ------------------------------------------------------------------
    def _vu_tons(self):
        try:
            val = float(self.ed_vu.text())
        except ValueError:
            return 0.0
        unit = self.cb_vu_unit.currentText()
        if unit == "kgf":
            return val / 1000.0
        if unit == "kN":
            return val * 0.101972
        return val

    # ------------------------------------------------------------------
    def on_calculate(self):
        Vu = self._vu_tons()
        try:
            Ln = float(self.ed_ln.text()) * 100  # m -> cm
            b = float(self.section_edits["b (cm)"].text())
            h = float(self.section_edits["h (cm)"].text())
            r = float(self.section_edits["r (cm)"].text())
            fc = float(self.section_edits["f'c (kg/cm²)"].text())
            fy = float(self.section_edits["fy (kg/cm²)"].text())
            de = DIAM_CM.get(self.cb_estribo.currentText(), 0)
            db = DIAM_CM.get(self.cb_barra.currentText(), 0)
        except ValueError:
            QMessageBox.warning(self, "Error", "Datos num\u00e9ricos inv\u00e1lidos")
            return
        d = h - r - de - 0.5 * db
        Av = 2 * BAR_DATA.get(self.cb_estribo.currentText(), 0)
        Vc = 0.53 * math.sqrt(fc) * b * d / 1000.0
        phi = 0.85
        Sc_min = min(
            max(d*10/4, 150),
            10 * DIAM_CM.get(self.cb_barra.currentText(),0)*10,
            24 * de*10,
            300
        )
        Sr_min = min(300, 0.5 * d * 10)
        Vs_nom = Av * fy * d / Sc_min / 1000.0
        if Vu <= phi * (Vc + Vs_nom):
            Sc = Sc_min
            Sr = Sr_min
        else:
            Vs_req = max(Vu/phi - Vc, 0)
            S_calc = Av * fy * d / (Vs_req * 1000.0)
            Sc = min(Sc_min, S_calc)
            Sr = min(Sr_min, S_calc)
        txt = (
            f"d = {d:.1f} cm\n"
            f"Vc = {Vc:.2f} tnf\n"
            f"Separaci\u00f3n Zc = {Sc:.0f} mm\n"
            f"Separaci\u00f3n Zr = {Sr:.0f} mm"
        )
        self.lbl_result.setText(txt)
        self.draw_section()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    win = ShearDesignWindow()
    win.show()
    app.exec_()
