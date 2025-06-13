"""Entry point launching the beam design application."""

import logging
import os
import sys
import ctypes

from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer

from src.menu_window import MenuWindow
from local_activation.activacion import run_activation




def main():
    """Start the Qt application."""
    logging.basicConfig(level=logging.ERROR)

    app = QApplication(sys.argv)

    if os.name == "nt":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VigApp060")
    icon_path = os.path.join(
        os.path.dirname(__file__), "icon", "vigapp060.png")
    if os.path.exists(icon_path):
        pix = QPixmap(icon_path).scaled(
            256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        app.setWindowIcon(QIcon(pix))


    app.setStyle("Fusion")

    if not run_activation():
        return

    splash = QSplashScreen(QPixmap(icon_path).scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    splash.show()

    def show_main():
        splash.close()
        main_win = MenuWindow()
        main_win.show()
        app._window = main_win

    QTimer.singleShot(2000, show_main)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

