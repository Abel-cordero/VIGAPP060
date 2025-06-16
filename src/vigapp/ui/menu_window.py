import os
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QStackedWidget,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QFrame,
    QGraphicsColorizeEffect,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon


class HoverIcon(QLabel):
    """Icon label that slightly enlarges and brightens on hover."""

    def __init__(self, icon_path: str, size: int = 64, parent=None):
        super().__init__(parent)
        self._pix = QPixmap(icon_path)
        self._base_size = size
        self._hover_size = int(size * 1.2)
        self.setFixedSize(self._hover_size, self._hover_size)
        self.setScaledContents(True)
        self._effect = QGraphicsColorizeEffect(self)
        self._effect.setStrength(0)
        self.setGraphicsEffect(self._effect)
        if not self._pix.isNull():
            self.setPixmap(
                self._pix.scaled(
                    self._base_size,
                    self._base_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

    def enterEvent(self, event):
        if not self._pix.isNull():
            self.setPixmap(
                self._pix.scaled(
                    self._hover_size,
                    self._hover_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        self._effect.setColor(Qt.white)
        self._effect.setStrength(0.2)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self._pix.isNull():
            self.setPixmap(
                self._pix.scaled(
                    self._base_size,
                    self._base_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        self._effect.setStrength(0)
        super().leaveEvent(event)


class BackgroundWidget(QWidget):
    """Widget that displays a scalable background image."""

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self._pix = QPixmap(image_path)
        self._label = QLabel(self)
        self._label.setScaledContents(True)
        self._label.lower()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background: transparent;")
        self._update_bg()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_bg()

    def _update_bg(self):
        if self._pix.isNull():
            self._label.hide()
            return
        self._label.show()
        self._label.setGeometry(0, 0, self.width(), self.height())
        self._label.setPixmap(
            self._pix.scaled(
                self.size(),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation,
            )
        )

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
        self._icon_dir = os.path.join(base_dir, "..", "icon")
        self._bg_path = os.path.join(base_dir, "..", "FONDO_MENU.png")
        if not os.path.exists(self._bg_path):
            self._bg_path = os.path.join(base_dir, "..", "icon", "fondo.png")

        self.stacked = QStackedWidget()
        self.setCentralWidget(self.stacked)

        self.setMinimumSize(700, 600)
        # Increase default height to provide more vertical space
        self.resize(700, 900)

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
        page = BackgroundWidget(self._bg_path)
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 20, 40, 20)

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
        btn_torsion = QPushButton("DISE\u00d1O POR TORSI\u00d3N")
        btn_cort = QPushButton("DISE\u00d1O POR CORTANTE")
        btn_mem = QPushButton("MEMORIA DE C\u00c1LCULO")
        btn_contact = QPushButton("CONTACTO")
        btn_exit = QPushButton("SALIR")
        btn_exit.setObjectName("Salir")

        btn_style = (
            "QPushButton {"
            "background-color: rgba(255, 255, 255, 0.75);"
            "border-radius: 10px;"
            "padding: 10px 20px;"
            "font-family: 'Segoe UI';"
            "font-size: 12pt;"
            "color: #000;"
            "}"
            "QPushButton:hover {"
            "background-color: rgba(255, 255, 255, 0.9);"
            "border: 1px solid rgba(0, 0, 0, 0.1);"
            "}"
        )
        exit_style = (
            "QPushButton#Salir {"
            "background-color: rgba(230, 57, 70, 0.9);"
            "color: white;"
            "}"
            "QPushButton#Salir:hover {"
            "background-color: rgba(200, 40, 50, 1.0);"
            "}"
        )

        full_style = btn_style + exit_style

        button_box = QFrame()
        btn_layout = QVBoxLayout(button_box)
        btn_layout.setSpacing(15)
        btn_layout.setContentsMargins(0, 0, 0, 0)

        def add_row(btn, name):
            icon_path = os.path.join(self._icon_dir, f"{name}.png")
            icon_lbl = HoverIcon(icon_path, 64)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setStyleSheet(full_style)
            btn.setMinimumHeight(50)
            btn.setMaximumWidth(300)
            row = QHBoxLayout()
            row.addWidget(icon_lbl)
            row.addWidget(btn)
            row.setAlignment(Qt.AlignLeft)
            row.setSpacing(10)
            btn_layout.addLayout(row)

        add_row(btn_flex, "DISE\u00d1O POR FLEXI\u00d3N")
        add_row(btn_torsion, "DISE\u00d1O POR TORSI\u00d3N")
        add_row(btn_cort, "DISE\u00d1O POR CORTANTE")
        add_row(btn_mem, "MEMORIA DE C\u00c1LCULO")
        add_row(btn_contact, "CONTACTO")
        btn_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        add_row(btn_exit, "SALIR")

        layout.addWidget(button_box)

        btn_flex.clicked.connect(self.open_diagrama)
        btn_torsion.clicked.connect(self.show_cortante_msg)
        btn_cort.clicked.connect(self.show_cortante_msg)
        btn_mem.clicked.connect(self.open_memoria)
        btn_contact.clicked.connect(self.show_contact)
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
                back_callback=self.show_design,
            )
            self.stacked.addWidget(self.desarrollo_page)
        self.stacked.setCurrentWidget(self.desarrollo_page)

    # ------------------------------------------------------------------
    def open_memoria(self):
        if not self.design_ready:
            QMessageBox.warning(self, "Advertencia", "Debe completar el diseño")
            return
        title, data = self.design_page._build_memoria()
        if title is None:
            return
        images = data.get("images", [])
        if hasattr(self, "diagram_page") and hasattr(self.diagram_page, "canvas"):
            from ..models.utils import capture_widget_temp
            img = capture_widget_temp(self.diagram_page.canvas, "diagram_")
            if img:
                images.append(img)
        data["images"] = images
        if not hasattr(self, "mem_page"):
            self.mem_page = MemoriaWindow(
                title,
                data,
                show_window=False,
                menu_callback=self.show_menu,
            )
            self.stacked.addWidget(self.mem_page)
        else:
            self.mem_page.setWindowTitle(title)
            self.mem_page.set_data(data)
        self.stacked.setCurrentWidget(self.mem_page)

    def show_design(self):
        if hasattr(self, "design_page"):
            self.stacked.setCurrentWidget(self.design_page)

    def show_cortante_msg(self):
        QMessageBox.information(self, "En desarrollo", "Módulo en desarrollo")

    def show_contact(self):
        QMessageBox.information(
            self,
            "Contacto",
            (
                "COMUNICARSE AL SIGUIENTE CORREO PARA SOLICTAR LA CLAVE DE "
                "ACTIVACION: abelcorderotineo99@gmail.com  cel y wsp : 922148420"
            ),
        )

    # ------------------------------------------------------------------
    def clear_data(self):
        self.mn_corr = None
        self.mp_corr = None
        self.design_ready = False
        QMessageBox.information(self, "Datos", "Datos limpiados")

    def show_menu(self):
        self.stacked.setCurrentWidget(self.menu_page)

