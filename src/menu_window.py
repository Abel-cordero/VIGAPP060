from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QStackedWidget,
    QMessageBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import os

from .moment_app import MomentApp
from .design_window import DesignWindow
from .view3d_window import View3DWindow
from .memoria_window import MemoriaWindow


class MenuWindow(QMainWindow):
    """Main container window with navigation."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("VIGAPP060")
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Menu page -----------------------------------------------------
        self.menu_page = QWidget()
        menu_layout = QVBoxLayout(self.menu_page)
        menu_layout.setAlignment(Qt.AlignCenter)
        icon_path = os.path.join(os.path.dirname(__file__), "..", "icon", "vigapp060.png")
        if os.path.exists(icon_path):
            lbl_icon = QLabel()
            pix = QPixmap(icon_path).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            lbl_icon.setPixmap(pix)
            lbl_icon.setAlignment(Qt.AlignCenter)
            menu_layout.addWidget(lbl_icon)
        title = QLabel("VIGAPP060")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20pt; font-weight: bold;")
        menu_layout.addWidget(title)
        self.btn_diag = QPushButton("Diagrama de Momentos")
        self.btn_design = QPushButton("Diseño de Acero")
        self.btn_ref = QPushButton("Desarrollo de Refuerzo")
        self.btn_mem = QPushButton("Memoria de Cálculo")
        self.btn_clear = QPushButton("Limpiar Datos")
        for b in (self.btn_diag, self.btn_design, self.btn_ref, self.btn_mem, self.btn_clear):
            menu_layout.addWidget(b)
        self.btn_diag.clicked.connect(self.show_diagrama)
        self.btn_design.clicked.connect(self.show_design)
        self.btn_ref.clicked.connect(self.show_refuerzo)
        self.btn_mem.clicked.connect(self.show_memoria)
        self.btn_clear.clicked.connect(self._clear_data)
        self.stack.addWidget(self.menu_page)

        # Pages ---------------------------------------------------------
        self.moment_page = MomentApp(main=self)
        self.moment_page.setParent(self)
        self.moment_page.setWindowFlags(Qt.Widget)
        self.stack.addWidget(self.moment_page)

        self.design_page = DesignWindow([], [], main=self)
        self.design_page.setParent(self)
        self.design_page.setWindowFlags(Qt.Widget)
        self.stack.addWidget(self.design_page)

        self.view3d_page = None
        self.memoria_page = None

        self.mn_corr = None
        self.mp_corr = None
        self.design_done = False
        self.ref_done = False

        self.show_menu()

    # Navigation helpers -----------------------------------------------
    def show_menu(self):
        self.stack.setCurrentWidget(self.menu_page)

    def show_diagrama(self):
        self.stack.setCurrentWidget(self.moment_page)

    def open_design(self, mn_corr, mp_corr):
        self.mn_corr = mn_corr
        self.mp_corr = mp_corr
        self.design_page.set_moments(mn_corr, mp_corr)
        self.stack.setCurrentWidget(self.design_page)

    def show_design(self):
        if self.mn_corr is None:
            QMessageBox.warning(self, "Advertencia", "Defina primero el diagrama")
            return
        self.design_page.set_moments(self.mn_corr, self.mp_corr)
        self.stack.setCurrentWidget(self.design_page)

    def open_refuerzo(self, design):
        if not self.design_done:
            QMessageBox.warning(self, "Advertencia", "Guarde el diseño primero")
            return
        if self.view3d_page is None:
            self.view3d_page = View3DWindow(design, main=self)
            self.view3d_page.setParent(self)
            self.view3d_page.setWindowFlags(Qt.Widget)
            self.stack.addWidget(self.view3d_page)
        self.stack.setCurrentWidget(self.view3d_page)

    def show_refuerzo(self):
        if not self.design_done:
            QMessageBox.warning(self, "Advertencia", "Guarde el diseño primero")
            return
        if self.view3d_page is None:
            self.view3d_page = View3DWindow(self.design_page, main=self)
            self.view3d_page.setParent(self)
            self.view3d_page.setWindowFlags(Qt.Widget)
            self.stack.addWidget(self.view3d_page)
        self.stack.setCurrentWidget(self.view3d_page)

    def open_memoria(self, title, text):
        if self.memoria_page is None:
            self.memoria_page = MemoriaWindow(title, text, main=self)
            self.memoria_page.setParent(self)
            self.memoria_page.setWindowFlags(Qt.Widget)
            self.stack.addWidget(self.memoria_page)
        else:
            self.memoria_page.text.setHtml(text)
            self.memoria_page.setWindowTitle(title)
        self.stack.setCurrentWidget(self.memoria_page)

    def open_memoria_from_refuerzo(self):
        if self.memoria_page:
            self.stack.setCurrentWidget(self.memoria_page)

    def show_memoria(self):
        if not self.design_done:
            QMessageBox.warning(self, "Advertencia", "Guarde el diseño primero")
            return
        if self.memoria_page:
            self.stack.setCurrentWidget(self.memoria_page)

    # Callbacks from pages ---------------------------------------------
    def diagram_saved(self, mn_corr, mp_corr):
        self.mn_corr = mn_corr
        self.mp_corr = mp_corr

    def design_saved(self):
        self.design_done = True

    def refuerzo_saved(self):
        self.ref_done = True

    # Utilities --------------------------------------------------------
    def _clear_data(self):
        self.mn_corr = None
        self.mp_corr = None
        self.design_done = False
        self.ref_done = False
        self.moment_page.reset_fields()
        self.design_page.saved = False
        if self.view3d_page:
            self.view3d_page.saved = False
        if self.memoria_page:
            self.memoria_page.text.clear()
        QMessageBox.information(self, "Listo", "Datos limpiados")
