"""Window displaying detailed calculation steps."""

import os
import tempfile
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QTextEdit,
    QFileDialog,
)
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtPrintSupport import QPrinter


class MemoriaWindow(QMainWindow):
    """Window showing detailed calculation memory."""

    def __init__(self, title: str, text: str, parent=None, *, show_window=True,
                 menu_callback=None):
        super().__init__(parent)
        self.menu_callback = menu_callback
        self.setWindowTitle(title)
        self.setFixedSize(700, 900)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFontFamily("Times New Roman")
        self.text.setFontPointSize(11)
        # Text is provided as HTML to allow richer formatting
        self.text.setHtml(text)
        layout.addWidget(self.text)

        self.btn_capture = QPushButton("Capturar Memoria")
        self.btn_export = QPushButton("Exportar…")
        self.btn_capture.clicked.connect(self._capture)
        self.btn_export.clicked.connect(self.export)
        self.btn_menu = QPushButton("Menú")
        self.btn_menu.clicked.connect(self.on_menu)
        layout.addWidget(self.btn_capture)
        layout.addWidget(self.btn_export)
        layout.addWidget(self.btn_menu)

        if show_window:
            self.show()

    def _capture(self):
        pix = self.centralWidget().grab()
        QGuiApplication.clipboard().setPixmap(pix)
        # Sin mensaje emergente

    def export(self):
        """Save the memory view as PNG, PDF or DOCX."""
        pix = self.centralWidget().grab()
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
            pix.save(tmp.name)
            from docx import Document

            doc = Document()
            doc.add_picture(tmp.name)
            doc.save(path)
            os.unlink(tmp.name)
        elif ext == ".pdf":
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(path)
            self.text.document().print_(printer)
        else:
            pix.save(path)

    def on_menu(self):
        if self.menu_callback:
            self.menu_callback()
