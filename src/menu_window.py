import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QStackedWidget,
    QMessageBox
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
        icon_path = os.path.join(os.path.dirname(__file__), "..", "icon", "vigapp060.png")
        pix = QPixmap(icon_path)
        if not pix.isNull():
            self.setWindowIcon(QIcon(pix))

        self.setWindowTitle("VIGAPP060")

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        self.mn_corr = None
        self.mp_corr = None
        self.design_ready = False

        self._build_menu(icon_path)

    # ------------------------------------------------------------------
    def _build_menu(self, icon_path):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        label_icon = QLabel()
        label_icon.setPixmap(QPixmap(icon_path).scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        label_title = QLabel("VIGAPP060")
        label_title.setAlignment(Qt.AlignCenter)
        label_title.setStyleSheet("font-size:20pt;font-weight:bold;")
        layout.addWidget(label_icon, alignment=Qt.AlignCenter)
        layout.addWidget(label_title)

        btn_diag = QPushButton("Diagrama de Momentos")
        btn_design = QPushButton("Diseño de Acero")
        btn_dev = QPushButton("Desarrollo de Refuerzo")
        btn_mem = QPushButton("Memoria de Cálculo")
        btn_clear = QPushButton("Limpiar Datos")

        layout.addWidget(btn_diag)
        layout.addWidget(btn_design)
        layout.addWidget(btn_dev)
        layout.addWidget(btn_mem)
        layout.addWidget(btn_clear)

        btn_diag.clicked.connect(self.open_diagrama)
        btn_design.clicked.connect(self.open_diseno)
        btn_dev.clicked.connect(self.open_desarrollo)
        btn_mem.clicked.connect(self.open_memoria)
        btn_clear.clicked.connect(self.clear_data)

        self.menu_page = page
        self.stacked.addWidget(page)
        self.stacked.setCurrentWidget(page)

    # ------------------------------------------------------------------
    def open_diagrama(self):
        if not hasattr(self, "diagram_page"):
            self.diagram_page = MomentApp(
                show_window=False,
                next_callback=self._diagram_next,
                save_callback=self._save_diagram,
                menu_callback=self.show_menu,
            )
            self.stacked.addWidget(self.diagram_page)
        self.stacked.setCurrentWidget(self.diagram_page)

    def _diagram_next(self, mn, mp):
        self.mn_corr = mn
        self.mp_corr = mp
        self.design_ready = False
        self.open_diseno()

    def _save_diagram(self, mn, mp):
        self.mn_corr = mn
        self.mp_corr = mp
        QMessageBox.information(self, "Guardado", "Momentos guardados")

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
                save_callback=self._save_design,
                menu_callback=self.show_menu,
            )
            self.stacked.addWidget(self.design_page)
        self.stacked.setCurrentWidget(self.design_page)

    def _design_next(self):
        self.design_ready = True
        self.open_desarrollo()

    def _save_design(self):
        self.design_ready = True
        QMessageBox.information(self, "Guardado", "Diseño guardado")

    # ------------------------------------------------------------------
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
        if not hasattr(self, "mem_page"):
            try:
                title = self.design_page.windowTitle()
            except Exception:
                title = "Memoria"
            self.mem_page = MemoriaWindow(
                title,
                "",
                show_window=False,
                menu_callback=self.show_menu,
            )
            self.stacked.addWidget(self.mem_page)
        self.stacked.setCurrentWidget(self.mem_page)

    # ------------------------------------------------------------------
    def clear_data(self):
        self.mn_corr = None
        self.mp_corr = None
        self.design_ready = False
        QMessageBox.information(self, "Datos", "Datos limpiados")

    def show_menu(self):
        self.stacked.setCurrentWidget(self.menu_page)

