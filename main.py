"""Entry point launching the beam design application."""

import logging
import os
import sys
import ctypes

# Allow importing the ``vigapp`` package from the ``src`` directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer

from vigapp.ui.menu_window import MenuWindow
from vigapp.activation.tk_dialog import run_activation

# Toggle for enabling or disabling the license check. Set to ``True`` to
# require activation again.
ACTIVATION_ENABLED = False
# Toggle the splash screen shown at startup. Set to ``False`` to
# open the main window immediately.
SPLASH_ENABLED = False




def main():
    """Start the Qt application."""
    logging.basicConfig(level=logging.ERROR)

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))

    if os.name == "nt":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VigApp060")
    icon_path = os.path.join(
        os.path.dirname(__file__), "icon", "vigapp060.png")
    if os.path.exists(icon_path):
        pix = QPixmap(icon_path).scaled(
            256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        app.setWindowIcon(QIcon(pix))


    app.setStyle("Fusion")
    if ACTIVATION_ENABLED and not run_activation():
        return

    if SPLASH_ENABLED:
        splash = QSplashScreen(QPixmap(icon_path).scaled(
            256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        splash.show()

        def show_main():
            splash.close()
            main_win = MenuWindow()
            main_win.show()
            app._window = main_win

        QTimer.singleShot(2000, show_main)
    else:
        main_win = MenuWindow()
        main_win.show()
        app._window = main_win

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

