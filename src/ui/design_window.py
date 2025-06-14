"""Wrapper for :mod:`vigapp.ui.design_window` with dynamic sizing fixes."""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLayout, QSizePolicy

# Import the original implementation
from ..vigapp.ui.design_window import DesignWindow as _BaseDesignWindow


class DesignWindow(QDialog):
    """Design window displayed inside a resizable scroll area."""

    def __init__(
        self,
        mn_corr,
        mp_corr,
        parent=None,
        *,
        show_window=True,
        next_callback=None,
        save_callback=None,
        menu_callback=None,
    ):
        super().__init__(parent)

        # Create the base window without showing it. The resulting scroll
        # area contains all widgets and layouts built in the original class.
        self._base = _BaseDesignWindow(
            mn_corr,
            mp_corr,
            None,
            show_window=False,
            next_callback=next_callback,
            save_callback=save_callback,
            menu_callback=menu_callback,
        )

        self._build_ui()
        self.setWindowTitle(self._base.windowTitle())
        # Start with a height large enough to reveal all content
        self.resize(750, 1250)
        if show_window:
            self.show()

    def _build_ui(self):
        """Re-parent the base content directly without scrollbars."""
        content = self._base.scroll_area.widget()
        content.setParent(self)

        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        layout.addWidget(content)
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(layout)

        content_layout = content.layout()
        if content_layout is not None:
            content_layout.setSizeConstraint(QLayout.SetMinimumSize)

        # Allow matplotlib canvases to expand with the window
        if hasattr(self._base, "canvas_sec"):
            self._base.canvas_sec.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if hasattr(self._base, "canvas_dist"):
            self._base.canvas_dist.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Ensure the window is large enough to show all widgets
        # self.setFixedSize(700, 1100)

    def __getattr__(self, name):
        """Delegate attribute access to the underlying window."""
        return getattr(self._base, name)
