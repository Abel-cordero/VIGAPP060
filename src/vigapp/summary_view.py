"""Preview of the calculation memory in Markdown."""

from PyQt5.QtWidgets import QWidget


class SummaryView(QWidget):
    """Displays a dynamic HTML preview."""

    def __init__(self, parent=None):
        super().__init__(parent)

