"""Interactive 2D view of the beam section."""

from PyQt5.QtWidgets import QWidget


class Section2DView(QWidget):
    """Allows dragging and swapping of reinforcement bars."""

    def __init__(self, parent=None):
        super().__init__(parent)

