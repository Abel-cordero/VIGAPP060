# -*- coding: utf-8 -*-
"""Simple window for shear design."""

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from ..graphics.shear_scheme import draw_shear_scheme
from .design.plots import draw_section
from ..models.constants import DIAM_CM
from .shear_result_window import ShearResultWindow


class ShearDesignWindow(QMainWindow):
    """UI to input Vu and plot a linear shear diagram."""

    def __init__(self, design_win=None, parent=None, *, show_window=True,
                 menu_callback=None, back_callback=None):
        super().__init__(parent)
        self.design_win = design_win
        self.menu_callback = menu_callback
        self.back_callback = back_callback
        self.show_window = show_window
        self.setWindowTitle("Dise\u00f1o por Cortante")
        self._build_ui()
        # Wider window to display the beam section alongside the inputs
        self.resize(1050, 500)
        if show_window:
            self.show()

    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        # Main vertical layout: top area (inputs + section) and bottom area
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        main_layout.addLayout(top_layout)

        # ------------------------------------------------------------------
        # Part 1 - compact input data on the top-left
        data_widget = QWidget()
        data_layout = QGridLayout(data_widget)
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setHorizontalSpacing(5)
        data_layout.setVerticalSpacing(2)

        self.ed_vu = QLineEdit("0.0")
        self.ed_vu.setAlignment(Qt.AlignRight)
        self.ed_vu.setFixedWidth(70)
        self.ed_ln = QLineEdit("5.0")
        self.ed_ln.setAlignment(Qt.AlignRight)
        self.ed_ln.setFixedWidth(70)
        self.cb_type = QComboBox()
        self.cb_type.addItems(["Apoyada", "Volado"])

        if self.design_win is not None:
            self.r_cover = float(self.design_win.edits["r (cm)"].text())
            b_def = self.design_win.edits["b (cm)"].text()
            h_def = self.design_win.edits["h (cm)"].text()
            fc_def = self.design_win.edits["f'c (kg/cm²)"].text()
            fy_def = self.design_win.edits["fy (kg/cm²)"].text()
            bar_def = self.design_win.cb_varilla.currentText()
            stirrup_def = self.design_win.cb_estribo.currentText()
            capa_def = self.design_win.layer_combo.currentText()
        else:
            self.r_cover = 4.0
            b_def = "30"
            h_def = "50"
            fc_def = "210"
            fy_def = "4200"
            bar_def = '5/8"'
            stirrup_def = '3/8"'
            capa_def = "1"

        self.ed_b = QLineEdit(b_def)
        self.ed_b.setAlignment(Qt.AlignRight)
        self.ed_b.setFixedWidth(70)
        self.ed_h = QLineEdit(h_def)
        self.ed_h.setAlignment(Qt.AlignRight)
        self.ed_h.setFixedWidth(70)
        self.ed_fc = QLineEdit(fc_def)
        self.ed_fc.setAlignment(Qt.AlignRight)
        self.ed_fc.setFixedWidth(70)
        self.ed_fy = QLineEdit(fy_def)
        self.ed_fy.setAlignment(Qt.AlignRight)
        self.ed_fy.setFixedWidth(70)

        self.cb_varilla = QComboBox()
        self.cb_varilla.addItems(['1/2"', '5/8"', '3/4"', '1"'])
        self.cb_varilla.setCurrentText(bar_def)

        self.cb_estribo = QComboBox()
        self.cb_estribo.addItems(["8mm", '3/8"', '1/2"'])
        self.cb_estribo.setCurrentText(stirrup_def)

        self.cb_layers = QComboBox()
        self.cb_layers.addItems(["1", "2", "3", "4"])
        self.cb_layers.setCurrentText(capa_def)

        self.ed_d = QLineEdit()
        self.ed_d.setReadOnly(True)
        self.ed_d.setAlignment(Qt.AlignRight)
        self.ed_d.setFixedWidth(70)

        data_layout.addWidget(QLabel("Vu (T)"), 0, 0)
        data_layout.addWidget(self.ed_vu, 0, 1)
        data_layout.addWidget(QLabel("Ln (m)"), 1, 0)
        data_layout.addWidget(self.ed_ln, 1, 1)
        data_layout.addWidget(QLabel("b (cm)"), 2, 0)
        data_layout.addWidget(self.ed_b, 2, 1)
        data_layout.addWidget(QLabel("h (cm)"), 3, 0)
        data_layout.addWidget(self.ed_h, 3, 1)
        data_layout.addWidget(QLabel("d (cm)"), 4, 0)
        data_layout.addWidget(self.ed_d, 4, 1)
        data_layout.addWidget(QLabel("f'c (kg/cm²)"), 5, 0)
        data_layout.addWidget(self.ed_fc, 5, 1)
        data_layout.addWidget(QLabel("fy (kg/cm²)"), 6, 0)
        data_layout.addWidget(self.ed_fy, 6, 1)
        data_layout.addWidget(QLabel("\u03c6 varilla"), 7, 0)
        data_layout.addWidget(self.cb_varilla, 7, 1)
        data_layout.addWidget(QLabel("\u03c6 estribo"), 8, 0)
        data_layout.addWidget(self.cb_estribo, 8, 1)
        data_layout.addWidget(QLabel("N\u00b0 capas"), 9, 0)
        data_layout.addWidget(self.cb_layers, 9, 1)
        data_layout.addWidget(QLabel("Tipo"), 10, 0)
        data_layout.addWidget(self.cb_type, 10, 1)

        btn_menu = QPushButton("Men\u00fa")
        btn_back = QPushButton("Atr\u00e1s")
        self.btn_calc = QPushButton("Calcular")
        self.btn_pdf = QPushButton("Reporte PDF")
        self.btn_html = QPushButton("Reporte HTML")
        self.btn_dxf = QPushButton("Exportar archivo DXF")
        self.btn_pdf.setEnabled(False)
        self.btn_html.setEnabled(False)
        self.btn_dxf.setEnabled(False)

        data_layout.addWidget(btn_menu, 11, 0)
        data_layout.addWidget(btn_back, 11, 1)
        data_layout.addWidget(self.btn_calc, 12, 0, 1, 2)
        data_layout.addWidget(self.btn_pdf, 13, 0, 1, 2)
        data_layout.addWidget(self.btn_html, 14, 0, 1, 2)
        data_layout.addWidget(self.btn_dxf, 15, 0, 1, 2)

        top_layout.addWidget(data_widget)

        # Section figure displayed on the top-right
        self.fig_sec, self.ax_sec = plt.subplots(figsize=(3, 3), constrained_layout=True)
        self.canvas_sec = FigureCanvas(self.fig_sec)
        self.lbl_props = QLabel("")
        self.lbl_props.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        sec_widget = QWidget()
        sec_layout = QVBoxLayout(sec_widget)
        sec_layout.setContentsMargins(0, 0, 0, 0)
        sec_layout.addWidget(self.canvas_sec)
        sec_layout.addWidget(self.lbl_props)
        top_layout.addWidget(sec_widget)

        # Distribute space evenly between top widgets and between top/bottom
        top_layout.setStretch(0, 1)
        top_layout.setStretch(1, 1)
        main_layout.setStretch(0, 1)
        main_layout.setStretch(1, 1)

        # Bottom part - shear diagram across the width
        self.fig, self.ax = plt.subplots(figsize=(5, 3), constrained_layout=True)
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas)

        self.ed_vu.editingFinished.connect(self.draw_diagram)
        self.ed_ln.editingFinished.connect(self.draw_diagram)
        self.ed_h.editingFinished.connect(self.update_depth)
        self.cb_varilla.currentIndexChanged.connect(self.update_depth)
        self.cb_estribo.currentIndexChanged.connect(self.update_depth)
        self.cb_layers.currentIndexChanged.connect(self.update_depth)
        btn_menu.clicked.connect(self.on_menu)
        btn_back.clicked.connect(self.on_back)
        self.cb_type.currentIndexChanged.connect(self.draw_diagram)
        self.btn_calc.clicked.connect(self.calculate)
        self.btn_pdf.clicked.connect(self.export_pdf)
        self.btn_html.clicked.connect(self.export_html)
        self.btn_dxf.clicked.connect(self.export_dxf)

        self.update_depth()
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
        beam_type = "volado" if self.cb_type.currentText().lower() == "volado" else "apoyada"

        h = float(self.ed_h.text()) / 100.0
        draw_shear_scheme(self.ax, Vu, L, d, h, beam_type)
        self.canvas.draw()
        self.update_section()

    # ------------------------------------------------------------------
    def calculate(self):
        """Run shear design calculations and enable exports."""
        try:
            Vu = float(self.ed_vu.text())
            Ln = float(self.ed_ln.text())
            d = float(self.ed_d.text())
            b = float(self.ed_b.text())
            h = float(self.ed_h.text())
            fc = float(self.ed_fc.text())
            fy = float(self.ed_fy.text())
        except ValueError:
            return

        from ..models.shear_design import shear_design

        self.result = shear_design(
            Vu=Vu,
            Ln=Ln,
            d=d,
            b=b,
            h=h,
            fc=fc,
            fy=fy,
            stirrup_diam=self.cb_estribo.currentText(),
            phi_long=DIAM_CM.get(self.cb_varilla.currentText(), 0),
            beam_type=self.cb_type.currentText().lower(),
        )

        self.draw_diagram()
        self.btn_pdf.setEnabled(True)
        self.btn_html.setEnabled(True)
        self.btn_dxf.setEnabled(True)

        # Show results window
        self.result_win = ShearResultWindow(
            self.result,
            Ln,
            Vu=Vu,
            beam_type=self.cb_type.currentText().lower(),
            h=float(self.ed_h.text()) / 100.0,
            show_window=True,
        )

    # ------------------------------------------------------------------
    def export_pdf(self):
        from ..pdf_engine.shear_report import generate_shear_pdf
        if not hasattr(self, "result"):
            return
        fig_path = "shear_plot.png"
        self.fig.savefig(fig_path, dpi=150)
        data = {
            "Vu": self.ed_vu.text(),
            "Ln": self.ed_ln.text(),
            "d": self.ed_d.text(),
            "b": self.ed_b.text(),
            "h": self.ed_h.text(),
            "f'c": self.ed_fc.text(),
            "fy": self.ed_fy.text(),
        }
        generate_shear_pdf(data, self.result, fig_path, "reporte_cortante.pdf")

    # ------------------------------------------------------------------
    def export_html(self):
        from reporte_cortante_html import generar_reporte_cortante_html
        if not hasattr(self, "result"):
            return
        fig_path = "shear_plot.png"
        self.fig.savefig(fig_path, dpi=150)
        data = {
            "Vu": self.ed_vu.text(),
            "Ln": self.ed_ln.text(),
            "d": self.ed_d.text(),
            "b": self.ed_b.text(),
            "h": self.ed_h.text(),
            "f'c": self.ed_fc.text(),
            "fy": self.ed_fy.text(),
        }
        generar_reporte_cortante_html(data, self.result, fig_path)

    # ------------------------------------------------------------------
    def export_dxf(self):
        from ..graphics.shear_dxf import export_shear_dxf
        if not hasattr(self, "result"):
            return
        export_shear_dxf(
            "esquema_cortante.dxf",
            float(self.ed_vu.text()),
            float(self.ed_ln.text()),
            float(self.ed_d.text()) / 100.0,
            float(self.ed_h.text()) / 100.0,
            "volado" if self.cb_type.currentText().lower() == "volado" else "apoyada",
        )

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

    # ------------------------------------------------------------------
    def update_depth(self):
        """Recalculate effective depth and update section."""
        try:
            h = float(self.ed_h.text())
            de = DIAM_CM.get(self.cb_estribo.currentText(), 0)
            db = DIAM_CM.get(self.cb_varilla.currentText(), 0)
            capas = int(self.cb_layers.currentText())
        except ValueError:
            return

        base = h - self.r_cover - de
        if capas <= 1:
            d = base - 0.5 * db
        elif capas == 2:
            d = base - 1.5 * db - 2.5
        elif capas == 3:
            d = base - 2.5 * db - 5.0
        else:
            d = base - 2.5 * db - 8.0

        self.ed_d.setText(f"{d:.2f}")
        self.draw_diagram()

    # ------------------------------------------------------------------
    def update_section(self):
        """Draw beam section and show basic properties."""
        try:
            b = float(self.ed_b.text())
            h = float(self.ed_h.text())
            r = self.r_cover
            bar = self.cb_varilla.currentText()
            stirrup = self.cb_estribo.currentText()
        except ValueError:
            return

        try:
            d = float(self.ed_d.text())
        except ValueError:
            d = 0.0

        draw_section(self.ax_sec, b, h, r, d)
        self.canvas_sec.draw()
        self.lbl_props.setText(
            f"h={h:.0f} cm  d={d:.1f} cm  \u03c6 {bar}  \u03c6e {stirrup}"
        )


