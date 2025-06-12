"""Window displaying detailed calculation steps."""

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit
from PyQt5.QtGui import QGuiApplication


class MemoriaWindow(QMainWindow):
    """Window showing detailed calculation memory."""

    def __init__(self, title: str, text: str):
        super().__init__()
        self.setWindowTitle(title)
        self.resize(700, 900)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFontFamily("Courier New")
        self.text.setFontPointSize(10)
        # Text is provided as HTML to allow richer formatting
        self.text.setHtml(text)
        layout.addWidget(self.text)

        self.btn_capture = QPushButton("Capturar Memoria")
        self.btn_capture.clicked.connect(self._capture)
        layout.addWidget(self.btn_capture)

    def _capture(self):
        pix = self.centralWidget().grab()
        QGuiApplication.clipboard().setPixmap(pix)
        # Sin mensaje emergente

