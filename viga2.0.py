"""Legacy wrapper for GUI classes."""

from src.moment_app import MomentApp
from src.design_window import DesignWindow, View3DWindow, MemoriaWindow


__all__ = [
    "MomentApp",
    "DesignWindow",
    "View3DWindow",
    "MemoriaWindow",
]

if __name__ == "__main__":
    import logging
    from PyQt5.QtWidgets import QApplication
    import sys

    logging.basicConfig(level=logging.ERROR)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    MomentApp()
    sys.exit(app.exec_())

