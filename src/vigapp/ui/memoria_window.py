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
import re

from pdf_engine.latex_renderer import render_report
from ..models.utils import formula_html


class MemoriaWindow(QMainWindow):
    """Window used to export the calculation memory as a PDF."""

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

    # ------------------------------------------------------------------
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
        """Generate the PDF and ask for a save location."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar PDF",
            "memoria.pdf",
            "PDF (*.pdf)",
        )
        if path:
            self._generate(path)

    def export(self):
        """Generate the PDF and let the user select the destination."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar PDF",
            "memoria.pdf",
            "PDF (*.pdf)",
        )
        if path:
            self._generate(path)

    def _generate(self, path: str):
        """Internal helper that builds the PDF using stored data."""
        data = {
            "data_section": self.data.get("data_section", []),
            "calc_sections": self.data.get("calc_sections", []),
            "results": self.data.get("results", []),
            "images": self.data.get("images", []),
            "section_img": self.data.get("section_img"),
            "formula_images": [
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "resources",
                    "flexion",
                    "figures",
                    "peralte.png",
                ),
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "..",
                    "resources",
                    "flexion",
                    "figures",
                    "pb.png",
                ),
            ],
        }

        render_report(self.windowTitle(), data, path)

    def edit_title(self):
        """Allow user to manually edit the window and header title."""
        title, ok = QInputDialog.getText(self, "Editar título", "Título:", text=self.windowTitle())
        if ok and title:
            self.setWindowTitle(title)
            self._refresh_html()

    def on_menu(self):
        if self.menu_callback:
            self.menu_callback()


