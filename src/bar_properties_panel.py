"""Dialog showing detailed bar properties."""

from PyQt5.QtWidgets import QDialog


class BarPropertiesPanel(QDialog):
    """Displays diameter, layer and length for a bar."""

    def __init__(self, parent=None):
        super().__init__(parent)
