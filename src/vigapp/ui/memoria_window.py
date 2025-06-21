"""Window triggering PDF generation for the calculation memory."""

import os
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QInputDialog,
    QTextBrowser,
)
from PyQt5.QtGui import QPixmap
import re

from ..models.utils import formula_html
from reporte_flexion_html import generar_reporte_html


class MemoriaWindow(QMainWindow):
    """Window used to export the calculation memory as HTML."""

    def __init__(self, title: str, data: dict, parent=None, *, show_window=True,
                 menu_callback=None):
        super().__init__(parent)
        self.menu_callback = menu_callback
        self.data = data
        self.setWindowTitle(title)
        self.setFixedSize(600, 800)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        top = QHBoxLayout()
        top.addStretch()
        self.btn_edit_title = QPushButton("Editar título")
        self.btn_edit_title.clicked.connect(self.edit_title)
        top.addWidget(self.btn_edit_title)
        layout.addLayout(top)

        self.label = QLabel(
            "Vista previa completa. Presione 'Captura' o 'Exportar…' para guardar la memoria en PDF.")
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        self.text = QTextBrowser()
        layout.addWidget(self.text, 1)

        self._refresh_html()

        self.btn_capture = QPushButton("CAPTURA")
        self.btn_export = QPushButton("Exportar…")
        self.btn_menu = QPushButton("Menú")
        for btn in (self.btn_capture, self.btn_export, self.btn_menu):
            btn.setFixedWidth(90)
        self.btn_capture.clicked.connect(self._capture)
        self.btn_export.clicked.connect(self.export)
        self.btn_menu.clicked.connect(self.on_menu)

        btns = QHBoxLayout()
        btns.addStretch()
        btns.addWidget(self.btn_capture)
        btns.addWidget(self.btn_export)
        btns.addWidget(self.btn_menu)
        btns.addStretch()
        layout.addLayout(btns)

        if show_window:
            self.show()

    def _build_html(self) -> str:
        """Return an HTML representation of the stored data."""
        data_section = self.data.get("data_section", [])
        calc_sections = self.data.get("calc_sections", [])
        results = self.data.get("results", [])
        images = self.data.get("images", [])
        section_img = self.data.get("section_img")

        html = [f"<h1 style='text-align:center'>{self.windowTitle()}</h1>"]
        if section_img:
            html.append(f"<p style='text-align:center'><img src='file://{section_img}' style='max-width:60%;'/></p>")
        if data_section:
            html.append("<h2>DATOS</h2>")
            html.append("<table border='1' cellspacing='0' cellpadding='4' style='width:100%'>")
            for k, v in data_section:
                html.append(f"<tr><td><b>{k}</b></td><td>{v}</td></tr>")
            html.append("</table>")

        if calc_sections:
            html.append("<h2>CÁLCULOS</h2>")
            for subtitle, steps in calc_sections:
                html.append(f"<h3>{subtitle}</h3>")
                for step in steps:
                    html.append(formula_html(step))

        if results:
            html.append("<h2>Resultados</h2>")
            html.append("<ul>")
            for text, value in results:
                html.append(f"<li>{text}: {value}</li>")
            html.append("</ul>")

        for img in images:
            html.append("<p style='text-align:center'>")
            html.append(f"<img src='file://{img}' style='max-width:90%;'/>")
            html.append("</p>")

        return "\n".join(html)

    def _refresh_html(self):
        self.text.setHtml(self._build_html())

    def set_data(self, data: dict):
        self.data = data
        self._refresh_html()

    def _capture(self):
        self._generate()

    def export(self):
        self._generate()

    def _generate(self):
        datos = {k: v for k, v in self.data.get("data_section", [])}
        resultados = {
            "peralte": {"formula": self.data.get("formula_peralte"), "valor": self.data.get("d")},
            "b1": {"formula": self.data.get("formula_b1"), "valor": self.data.get("b1")},
            "pbal": {"formula": self.data.get("formula_pbal"), "valor": self.data.get("pbal")},
            "pmax": {"formula": self.data.get("formula_pmax"), "valor": self.data.get("pmax")},
            "as_min": {"formula": self.data.get("formula_asmin"), "valor": self.data.get("as_min")},
            "as_max": {"formula": self.data.get("formula_asmax"), "valor": self.data.get("as_max")},
        }
        generar_reporte_html(datos, resultados)

    def edit_title(self):
        title, ok = QInputDialog.getText(self, "Editar título", "Título:", text=self.windowTitle())
        if ok and title:
            self.setWindowTitle(title)
            self._refresh_html()

    def on_menu(self):
        if self.menu_callback:
            self.menu_callback()
