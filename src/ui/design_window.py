"""Wrapper for :mod:`vigapp.ui.design_window` with dynamic sizing fixes."""

from PyQt5.QtWidgets import QScrollArea

# Import the original implementation
from ..vigapp.ui.design_window import DesignWindow as _BaseDesignWindow


class DesignWindow(_BaseDesignWindow):
    """Design window with scrollable contents and dynamic sizing."""

    def _build_ui(self):
        super()._build_ui()

        # Ensure the central widget is wrapped in a scroll area to allow
        # vertical scrolling when the contents exceed the available height.
        if not isinstance(self.centralWidget(), QScrollArea):
            content_widget = self.centralWidget()
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(content_widget)
            self.setCentralWidget(scroll)

        # Do not force any fixed size for the window. The base implementation
        # may have resized the window, but here we avoid calling ``resize`` or
        # ``setFixedSize`` so that the geometry adapts naturally to the
        # available space and scrolls when required.

