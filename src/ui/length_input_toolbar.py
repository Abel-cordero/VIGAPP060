"""Toolbar with quick length input shortcuts."""

from PyQt5.QtWidgets import QToolBar, QLineEdit, QAction


class LengthInputToolbar(QToolBar):
    """Provides L input and buttons for L/3, L/2 and L."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.input = QLineEdit()
        self.addWidget(self.input)
        self.addAction(QAction("L/3", self))
        self.addAction(QAction("L/2", self))
        self.addAction(QAction("L", self))
