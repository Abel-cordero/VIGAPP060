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
from PyQt5.QtGui import QPixmap, QIcon, QFont

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
        self._ico_dir = os.path.join(base_dir, "..", "ico")

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        self.setMinimumSize(700, 600)
        self.resize(700, 800)

        self.mn_corr = None
        self.mp_corr = None
        self.design_ready = False

        self._build_menu()

    # ------------------------------------------------------------------
    def _update_logo(self):
        pix = QPixmap(self._logo_path)
        if pix.isNull():
            return
        size = int(min(self.width(), 300) * 0.5)
        if size <= 0:
            size = 150
        self.label_icon.setPixmap(
            pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "label_icon"):
            self._update_logo()

    # ------------------------------------------------------------------
    def _build_menu(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)

        label_icon = QLabel()
        self.label_icon = label_icon
        self._update_logo()
        label_icon.setAlignment(Qt.AlignCenter)
        label_title = QLabel("VIGAPP060")
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setStyleSheet(
            "font-size:24pt;font-weight:bold;padding:10px;font-family:'Segoe UI';"
        )

        layout.addWidget(label_icon, alignment=Qt.AlignCenter)
        layout.addWidget(label_title)

        btn_flex = QPushButton("DISE\u00d1O POR FLEXI\u00d3N")
        btn_flex_extra = QPushButton("DISE\u00d1O POR TORSI\u00d3N")
        btn_cort = QPushButton("DISE\u00d1O POR CORTANTE")
        btn_mem = QPushButton("MEMORIA DE C\u00c1LCULO")
        btn_exit = QPushButton("SALIR")

        for btn, name in [
            (btn_flex, "DISE\u00d1O POR FLEXI\u00d3N"),
            (btn_flex_extra, "DISE\u00d1O POR TORSI\u00d3N"),
            (btn_cort, "DISE\u00d1O POR CORTANTE"),
            (btn_mem, "MEMORIA DE C\u00c1LCULO"),
        ]:
            icon_path = os.path.join(self._ico_dir, f"{name}.ico")
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
            btn.setCursor(Qt.PointingHandCursor)

        exit_icon = os.path.join(self._ico_dir, "SALIR.ico")
        if os.path.exists(exit_icon):
            btn_exit.setIcon(QIcon(exit_icon))
        btn_exit.setCursor(Qt.PointingHandCursor)

        button_box = QFrame()
        btn_layout = QVBoxLayout(button_box)
        btn_layout.setSpacing(15)
        btn_layout.setContentsMargins(40, 20, 40, 20)

        default_style = (
            "QPushButton {background-color:#3498db;color:white;font-size:16pt;"
            "padding:15px;border-radius:10px;font-family:'Segoe UI';}"
            "QPushButton:hover {background-color:#2980b9;transform:scale(1.02);}"
        )

        for b in (btn_flex, btn_flex_extra, btn_cort, btn_mem):
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            b.setStyleSheet(default_style)
            btn_layout.addWidget(b)

        exit_style = (
            "QPushButton {background-color:#e74c3c;color:white;font-size:16pt;"
            "padding:15px;border-radius:10px;font-family:'Segoe UI';}"
            "QPushButton:hover {background-color:#c0392b;}"
        )
        btn_exit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        btn_exit.setStyleSheet(exit_style)
        btn_layout.addSpacing(20)
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

