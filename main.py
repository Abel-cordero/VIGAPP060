"""Entry point launching the beam design application."""

import logging
import os
import sys
import ctypes

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

from src.moment_app import MomentApp
from src.activation_dialog import run_activation




def main():
    """Start the Qt application."""
    logging.basicConfig(level=logging.ERROR)

    if not run_activation():
        return

    if os.name == "nt":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VigApp060")
    app = QApplication(sys.argv)
    icon_path = os.path.join(
        os.path.dirname(__file__), "icon", "vigapp060.png")
    if os.path.exists(icon_path):
        pix = QPixmap(icon_path).scaled(
            256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        app.setWindowIcon(QIcon(pix))


    app.setStyle("Fusion")

    # Keep a reference to the main window so it isn't garbage collected
    _window = MomentApp()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

