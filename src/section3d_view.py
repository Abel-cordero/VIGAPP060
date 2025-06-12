"""3D window rendering the beam model."""

from PyQt5.QtWidgets import QMainWindow


class Section3DView(QMainWindow):
    """Shows a transparent beam with its reinforcement."""

    def __init__(self, parent=None):
        super().__init__(parent)

