from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtGui import QGuiApplication

from .activation import machine_code, activate, license_counter


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

        contact_btn = QPushButton("Contacto")
        copy_btn = QPushButton("Copiar ID")
        activate_btn = QPushButton("Activar")
        exit_btn = QPushButton("Salir")

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

