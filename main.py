"""Entry point launching the beam design application."""

import logging
import sys
from PyQt5.QtWidgets import QApplication
from src.moment_app import MomentApp


def main():
    """Start the Qt application."""
    logging.basicConfig(level=logging.ERROR)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    MomentApp()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

