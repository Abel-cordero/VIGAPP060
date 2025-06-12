"""Entry point launching the beam design application."""

import logging
import sys
from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog
from src.moment_app import MomentApp
from src.activation import check_activation, activate


def main():
    """Start the Qt application."""
    logging.basicConfig(level=logging.ERROR)
    if not check_activation():
        key, ok = QInputDialog.getText(
            None, "Activar VIGAPP 060", "Ingrese la clave:")
        if not ok or not activate(key):
            QMessageBox.critical(None, "Licencia", "Clave inv\xE1lida")
            return

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # Keep a reference to the main window so it isn't garbage collected
    window = MomentApp()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

