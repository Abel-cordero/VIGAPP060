"""Wrapper for :mod:`vigapp.ui.design_window` with dynamic sizing fixes."""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QScrollArea, QLayout

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
        self.resize(self._base.size())
        if show_window:
            self.show()

    def _build_ui(self):
        # Re-parent the base scroll area to this dialog and ensure it is
        # resizable. Its internal layout is also configured to use the
        # minimum required size so the scroll bars appear when necessary.
        self.scroll_area = self._base.scroll_area
        self.scroll_area.setParent(self)
        self.scroll_area.setWidgetResizable(True)

        layout = QVBoxLayout(self)
        layout.setSizeConstraint(QLayout.SetMinimumSize)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)

        content_layout = self.scroll_area.widget().layout()
        if content_layout is not None:
            content_layout.setSizeConstraint(QLayout.SetMinimumSize)

    def __getattr__(self, name):
        """Delegate attribute access to the underlying window."""
        return getattr(self._base, name)
