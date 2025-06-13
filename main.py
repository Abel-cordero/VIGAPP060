"""Entry point launching the beam design application."""

import logging
import os
import sys
import ctypes
import subprocess
import hashlib

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

from src.moment_app import MomentApp


SECRET = "MI_SECRETO_2024"


def obtener_serial() -> str:
    """Return the first disk serial number on Windows."""
    if os.name != "nt":
        return ""
    try:
        out = subprocess.check_output(
            ["wmic", "diskdrive", "get", "SerialNumber"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        lines = [line.strip() for line in out.splitlines() if line.strip()][1:]
        return lines[0] if lines else ""
    except Exception:
        return ""


def _base36(val: int) -> str:
    """Return ``val`` encoded in base36."""
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if val == 0:
        return "0"
    digits = []
    while val:
        val, rem = divmod(val, 36)
        digits.append(chars[rem])
    return "".join(reversed(digits))


def validar_licencia() -> bool:
    """Prompt the user for a license and validate it."""
    serial = obtener_serial()
    if not serial:
        print("No se pudo obtener el serial del disco.")
        return False

    print(f"ID de activacion: {serial}")
    digest = hashlib.sha256((serial + SECRET).encode()).hexdigest()
    expected = _base36(int(digest, 16))[:6].upper()

    clave = input("Ingrese la clave de activacion: ").strip().upper()
    if clave == expected:
        print("Licencia valida.\n")
        return True

    print("Clave incorrecta.")
    return False


def main():
    """Start the Qt application."""
    logging.basicConfig(level=logging.ERROR)
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
    if validar_licencia():
        main()

