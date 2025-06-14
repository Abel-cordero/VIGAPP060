"""Wrapper for :mod:`vigapp.ui.design_window` with window sizing fixes."""

from PyQt5.QtWidgets import QScrollArea

# Import the original implementation
from ..vigapp.ui.design_window import DesignWindow as _BaseDesignWindow


class DesignWindow(_BaseDesignWindow):
    """Design window with scrollable contents and dynamic sizing."""

    def _build_ui(self):
        super()._build_ui()

        # Ensure the central widget is a scroll area to allow vertical scrolling
        if not isinstance(self.centralWidget(), QScrollArea):
            content_widget = self.centralWidget()
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(content_widget)
            self.setCentralWidget(scroll)

        # Allow the window to be resized instead of fixing its size
        self.resize(700, 1000)

