from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import os

from .moment_app import MomentApp
from .design_window import DesignWindow
from .view3d_window import View3DWindow
from .memoria_window import MemoriaWindow


class MenuWindow(QMainWindow):
    """Main menu window with navigation buttons."""

    def __init__(self, icon_path: str):
        super().__init__()
        self.setWindowTitle("VIGAPP060")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.icon_path = icon_path
        self.moment_win = None
        self.design_win = None
        self.view3d_win = None
        self.mem_win = None
        self._build_ui()

    # ------------------------------------------------------------------
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(10)

        self.btn_moment = QPushButton("Diagrama de Momentos")
        self.btn_design = QPushButton("Diseño de Acero")
        self.btn_view3d = QPushButton("Desarrollo de Refuerzo")
        self.btn_memoria = QPushButton("Memoria de Cálculo")
        self.btn_clear = QPushButton("Limpiar Datos")

        for btn in (
            self.btn_moment,
            self.btn_design,
            self.btn_view3d,
            self.btn_memoria,
            self.btn_clear,
        ):
            btn.setMinimumHeight(40)
            layout.addWidget(btn)

        self.btn_moment.clicked.connect(self.open_moment)
        self.btn_design.clicked.connect(self.open_design)
        self.btn_view3d.clicked.connect(self.open_view3d)
        self.btn_memoria.clicked.connect(self.open_memoria)
        self.btn_clear.clicked.connect(self.clear_data)

    # ------------------------------------------------------------------
    def open_moment(self):
        if not self.moment_win:
            self.moment_win = MomentApp()
            self.moment_win.menu_requested.connect(self.show_menu)
        self.hide()
        self.moment_win.show()

    def open_design(self):
        if not self.moment_win or self.moment_win.mn_corr is None:
            QMessageBox.warning(self, "Advertencia", "Defina primero el diagrama de momentos")
            return
        if not self.design_win:
            self.design_win = DesignWindow(self.moment_win.mn_corr, self.moment_win.mp_corr)
            self.design_win.menu_requested.connect(self.show_menu)
        self.hide()
        self.design_win.show()

    def open_view3d(self):
        if not self.design_win:
            QMessageBox.warning(self, "Advertencia", "Defina primero el diseño de acero")
            return
        if not self.view3d_win:
            self.view3d_win = View3DWindow(self.design_win)
            self.view3d_win.menu_requested.connect(self.show_menu)
        self.hide()
        self.view3d_win.show()

    def open_memoria(self):
        if not self.design_win:
            QMessageBox.warning(self, "Advertencia", "Defina primero el diseño de acero")
            return
        self.design_win.show_memoria()
        self.mem_win = self.design_win.mem_win
        if self.mem_win:
            self.mem_win.menu_requested.connect(self.show_menu)
            self.hide()
            self.mem_win.show()

    def clear_data(self):
        for win in (self.moment_win, self.design_win, self.view3d_win, self.mem_win):
            if win:
                win.close()
        self.moment_win = None
        self.design_win = None
        self.view3d_win = None
        self.mem_win = None
        QMessageBox.information(self, "Datos", "Se han limpiado los datos")

    def show_menu(self):
        for win in (self.moment_win, self.design_win, self.view3d_win, self.mem_win):
            if win:
                win.hide()
        self.show()
