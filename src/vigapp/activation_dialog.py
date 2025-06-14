from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
import os
from PyQt5.QtGui import QGuiApplication, QIcon
from PyQt5.QtCore import Qt

from .activation import machine_code, activate, check_activation, license_counter


class ActivationDialog(QDialog):
    """Simple dialog requesting the activation key."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Activar VIGAPP 060")
        self.setModal(True)
        self._code = machine_code()
        counter = license_counter()
        msg = (
            f"ID de equipo: {self._code}\n"
            f"Contador: {counter}\n\n"
            "Comparta este codigo al contacto para solicitar su clave de "
            "activacion. Si ya la tiene, ingrese la clave y presione Activar."
        )
        label = QLabel(msg)
        label.setWordWrap(True)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Clave de activacion")

        icon_dir = os.path.join(os.path.dirname(__file__), "..", "ico")

        contact_btn = QPushButton("CONTACTO")
        copy_btn = QPushButton("COPIAR ID")
        activate_btn = QPushButton("ACTIVAR")
        exit_btn = QPushButton("SALIR")

        for btn, name in [
            (contact_btn, "CONTACTO"),
            (exit_btn, "SALIR"),
        ]:
            ico = os.path.join(icon_dir, f"{name}.ico")
            if os.path.exists(ico):
                btn.setIcon(QIcon(ico))
            btn.setCursor(Qt.PointingHandCursor)

        style = (
            "QPushButton {background-color:#3498db;color:white;font-size:10pt;"
            "padding:8px;border-radius:5px;font-family:'Segoe UI';}"
            "QPushButton:hover {background-color:#2980b9;}"
        )
        exit_style = (
            "QPushButton {background-color:#e74c3c;color:white;font-size:10pt;"
            "padding:8px;border-radius:5px;font-family:'Segoe UI';}"
            "QPushButton:hover {background-color:#c0392b;}"
        )

        for b in (contact_btn, copy_btn, activate_btn):
            b.setStyleSheet(style)
        exit_btn.setStyleSheet(exit_style)

        contact_btn.clicked.connect(self._show_contact)
        copy_btn.clicked.connect(self._copy_id)
        activate_btn.clicked.connect(self._on_activate)
        exit_btn.clicked.connect(self.reject)

        btn_row = QHBoxLayout()
        btn_row.addWidget(contact_btn)
        btn_row.addWidget(copy_btn)
        btn_row.addWidget(activate_btn)
        btn_row.addWidget(exit_btn)

        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.input)
        layout.addLayout(btn_row)

    def _show_contact(self):
        QMessageBox.information(
            self,
            "Contacto",
            (
                "COMUNICARSE AL SIGUIENTE CORREO PARA SOLICTAR LA CLAVE DE "
                "ACTIVACION: abelcorderotineo99@gmail.com  cel y wsp : 922148420"
            ),
        )

    def _on_activate(self):
        key = self.input.text().strip()
        if activate(key):
            QMessageBox.information(self, "Licencia", "Programa activado correctamente!")
            self.accept()
        else:
            QMessageBox.warning(self, "Licencia", "Clave invalida. Verifique e intente nuevamente.")

    def _copy_id(self):
        QGuiApplication.clipboard().setText(self._code)
        QMessageBox.information(self, "Copiar ID", "ID copiado al portapapeles")


def run_activation(parent=None) -> bool:
    """Return ``True`` if the application is activated."""
    if check_activation():
        return True
    dialog = ActivationDialog(parent)
    return dialog.exec_() == QDialog.Accepted

