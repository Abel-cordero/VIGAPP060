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
)
import re

from ..pdf_report import generate_memoria_pdf


class MemoriaWindow(QMainWindow):
    """Window used to export the calculation memory as a PDF."""

    def __init__(self, title: str, data: dict, parent=None, *, show_window=True,
                 menu_callback=None):
        super().__init__(parent)
        self.menu_callback = menu_callback
        self.data = data
        self.setWindowTitle(title)
        self.setFixedSize(500, 200)

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
            "Presione 'Captura' o 'Exportar…' para guardar la memoria en PDF.")
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

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
        generate_memoria_pdf(
            self.windowTitle(),
            self.data.get("data_section", []),
            self.data.get("calc_sections", []),
            self.data.get("results", []),
            path,
        )

    def edit_title(self):
        """Allow user to manually edit the window and header title."""
        title, ok = QInputDialog.getText(self, "Editar título", "Título:", text=self.windowTitle())
        if ok and title:
            self.setWindowTitle(title)

    def on_menu(self):
        if self.menu_callback:
            self.menu_callback()


