import os
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QMessageBox,
    QSizePolicy,
    QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon

from .moment_app import MomentApp
from .design_window import DesignWindow
from .view3d_window import View3DWindow
from .memoria_window import MemoriaWindow


class MenuWindow(QMainWindow):
    """Main application window with a simple stacked menu."""

    def __init__(self):
        super().__init__()
        base_dir = os.path.dirname(__file__)
        icon_path = os.path.join(base_dir, "..", "icon", "vigapp060.png")
        pix = QPixmap(icon_path)
        if not pix.isNull():
            self.setWindowIcon(QIcon(pix))
        self._logo_path = os.path.join(base_dir, "..", "icon", "mi_logo.png")
        if not os.path.exists(self._logo_path):
            self._logo_path = icon_path

        self.setWindowTitle("VIGAPP060")

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        self.setMinimumSize(700, 600)
        self.resize(700, 800)

        self.mn_corr = None
        self.mp_corr = None
        self.design_ready = False

        self._build_menu()

    # ------------------------------------------------------------------
    def _build_menu(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        label_icon = QLabel()
        label_icon.setPixmap(QPixmap(self._logo_path).scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        label_icon.setAlignment(Qt.AlignCenter)
        label_title = QLabel("VIGAPP060")
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setStyleSheet("font-size:24pt;font-weight:bold;padding:10px;")

        layout.addWidget(label_icon, alignment=Qt.AlignCenter)
        layout.addWidget(label_title)

        btn_flex = QPushButton("Diseño por Flexión")
        btn_flex_extra = QPushButton("Otro Diseño")
        btn_cort = QPushButton("Diseño por Cortante")
        btn_mem = QPushButton("Memoria de Cálculo")
        btn_exit = QPushButton("Salir")

        button_box = QFrame()
        btn_layout = QVBoxLayout(button_box)
        btn_layout.setSpacing(15)
        btn_layout.setContentsMargins(40, 20, 40, 20)

        default_style = (
            "QPushButton {background-color:#3498db;color:white;font-size:16pt;"
            "padding:15px;border-radius:10px;}"
            "QPushButton:hover {background-color:#2980b9;}"
        )

        for b in (btn_flex, btn_flex_extra, btn_cort, btn_mem):
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            b.setStyleSheet(default_style)
            btn_layout.addWidget(b)

        exit_style = (
            "QPushButton {background-color:#e74c3c;color:white;font-size:16pt;"
            "padding:15px;border-radius:10px;}"
            "QPushButton:hover {background-color:#c0392b;}"
        )
        btn_exit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn_exit.setStyleSheet(exit_style)
        btn_layout.addWidget(btn_exit)

        layout.addWidget(button_box)

        btn_flex.clicked.connect(self.open_diagrama)
        btn_flex_extra.clicked.connect(self.show_cortante_msg)
        btn_cort.clicked.connect(self.show_cortante_msg)
        btn_mem.clicked.connect(self.open_memoria)
        btn_exit.clicked.connect(self.close)

        self.menu_page = page
        self.stacked.addWidget(page)
        self.stacked.setCurrentWidget(page)

    # ------------------------------------------------------------------
    def open_diagrama(self):
        if not hasattr(self, "diagram_page"):
            self.diagram_page = MomentApp(
                show_window=False,
                next_callback=self._diagram_next,
                menu_callback=self.show_menu,
            )
            self.stacked.addWidget(self.diagram_page)
        self.stacked.setCurrentWidget(self.diagram_page)

    def _diagram_next(self, mn, mp):
        self.mn_corr = mn
        self.mp_corr = mp
        self.design_ready = False
        self.open_diseno()

    # ------------------------------------------------------------------
    def open_diseno(self):
        if self.mn_corr is None or self.mp_corr is None:
            QMessageBox.warning(self, "Advertencia", "Primero defina el diagrama")
            return
        if not hasattr(self, "design_page"):
            self.design_page = DesignWindow(
                self.mn_corr,
                self.mp_corr,
                show_window=False,
                next_callback=self._design_next,
                menu_callback=self.show_menu,
            )
            self.stacked.addWidget(self.design_page)
        self.stacked.setCurrentWidget(self.design_page)

    def _design_next(self):
        self.design_ready = True
        self.open_desarrollo()

    def open_desarrollo(self):
        if not self.design_ready:
            QMessageBox.warning(self, "Advertencia", "Primero complete el diseño")
            return
        if not hasattr(self, "desarrollo_page"):
            self.desarrollo_page = View3DWindow(
                self.design_page,
                show_window=False,
                menu_callback=self.show_menu,
            )
            self.stacked.addWidget(self.desarrollo_page)
        self.stacked.setCurrentWidget(self.desarrollo_page)

    # ------------------------------------------------------------------
    def open_memoria(self):
        if not self.design_ready:
            QMessageBox.warning(self, "Advertencia", "Debe completar el diseño")
            return
        title, html = self.design_page._build_memoria()
        if title is None:
            return
        if not hasattr(self, "mem_page"):
            self.mem_page = MemoriaWindow(
                title,
                html,
                show_window=False,
                menu_callback=self.show_menu,
            )
            self.stacked.addWidget(self.mem_page)
        else:
            self.mem_page.setWindowTitle(title)
            self.mem_page.text.setHtml(html)
        self.stacked.setCurrentWidget(self.mem_page)

    def show_cortante_msg(self):
        QMessageBox.information(self, "En desarrollo", "Módulo en desarrollo")

    # ------------------------------------------------------------------
    def clear_data(self):
        self.mn_corr = None
        self.mp_corr = None
        self.design_ready = False
        QMessageBox.information(self, "Datos", "Datos limpiados")

    def show_menu(self):
        self.stacked.setCurrentWidget(self.menu_page)

