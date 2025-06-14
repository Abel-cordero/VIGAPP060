"""Dock widget listing rebar elements for quick editing."""

from PyQt5.QtWidgets import QDockWidget


class RebarEditorWidget(QDockWidget):
    """Panel with a list of rebars and fast property editing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Barras")
