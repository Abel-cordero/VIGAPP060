import logging
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QButtonGroup,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline
import mplcursors

from vigapp.ui.design_window import DesignWindow


class MomentApp(QMainWindow):
    """Ventana principal para ingresar momentos y graficar diagramas."""

    def __init__(self, parent=None, *, show_window=True, next_callback=None,
                 save_callback=None, menu_callback=None):
        super().__init__(parent)
        self.next_callback = next_callback
        self.save_callback = save_callback
        self.menu_callback = menu_callback
        self.setWindowTitle("Parte 1 – Momentos y Diagramas (NTP E.060)")
        self.mn_corr = None
        self.mp_corr = None
        self._build_ui()
        self.setFixedSize(700, 900)
        if show_window:
            self.show()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QGridLayout(central)

        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(10)
        layout.setColumnStretch(6, 1)

        self.m_neg_edits, self.m_pos_edits = [], []
        for row, labels in enumerate([("M1–", "M2–", "M3–"), ("M1+", "M2+", "M3+")]):
            for i, text in enumerate(labels):
                layout.addWidget(QLabel(text), row, 2 * i)
                ed = QLineEdit("0.0")
                ed.setAlignment(Qt.AlignRight)
                ed.setFixedWidth(80)
                layout.addWidget(ed, row, 2 * i + 1)
                if row == 0:
                    self.m_neg_edits.append(ed)
                else:
                    self.m_pos_edits.append(ed)

        self.rb_dual1 = QRadioButton("Dual 1")
        self.rb_dual2 = QRadioButton("Dual 2")
        self.rb_dual2.setChecked(True)
        bg = QButtonGroup(self)
        bg.addButton(self.rb_dual1)
        bg.addButton(self.rb_dual2)
        layout.addWidget(QLabel("Sistema:"), 2, 0)
        layout.addWidget(self.rb_dual1, 2, 1)
        layout.addWidget(self.rb_dual2, 2, 2)

        btn_calc = QPushButton("Calcular Diagramas")
        btn_next = QPushButton("Ir a Diseño de Acero")
        btn_capture = QPushButton("Capturar Diagramas")
        btn_menu = QPushButton("Ir al Menú")

        btn_calc.clicked.connect(self.on_calculate)
        btn_next.clicked.connect(self.on_next)
        btn_capture.clicked.connect(self._capture_diagram)
        btn_menu.clicked.connect(self.on_menu)

        layout.addWidget(btn_calc, 3, 2)
        layout.addWidget(btn_next, 3, 3)
        layout.addWidget(btn_capture, 3, 4)
        layout.addWidget(btn_menu, 3, 5)

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(6, 5), constrained_layout=True)
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas, 4, 0, 1, 6)

        self.plot_original()

    def get_moments(self):
        """Return entered moments enforcing expected sign convention."""
        try:
            mn = []
            mp = []
            for ed in self.m_neg_edits:
                val = float(ed.text())
                mn.append(-abs(val))
            for ed in self.m_pos_edits:
                val = float(ed.text())
                mp.append(abs(val))
            return np.array(mn), np.array(mp)
        except ValueError:
            QMessageBox.warning(self, "Error", "Ingrese valores numéricos válidos.")
            raise

    def get_length(self):
        return 1.0

    def plot_original(self):
        mn, mp = self.get_moments()
        L = self.get_length()
        x_ctrl = np.array([0, 0.5, 1.0])
        xs = np.linspace(0, L, 200)
        csn = CubicSpline(x_ctrl, -mn)
        csp = CubicSpline(x_ctrl, -mp)

        self.ax1.clear()
        self.ax2.clear()
        for ax in (self.ax1, self.ax2):
            ax.plot([0, L], [0, 0], 'k-', lw=6)

        self.ax1.plot(xs, csn(xs), 'b-', lw=1.5, label='Neg original')
        self.ax1.fill_between(xs, csn(xs), 0, color='b', alpha=0.25, hatch='//', edgecolor='b')
        self.ax1.plot(xs, csp(xs), 'r-', lw=1.5, label='Pos original')
        self.ax1.fill_between(xs, csp(xs), 0, color='r', alpha=0.25, hatch='\\', edgecolor='r')
        self._draw_verticals(self.ax1, csn, csp, x_ctrl)
        self._label_points(self.ax1, csn, csp, x_ctrl)
        self._enable_hover(self.ax1, csn, csp)
        self._format(self.ax1)
        self.canvas.draw()

    def plot_corrected(self, mn_corr, mp_corr, mn_orig=None, mp_orig=None):
        L = self.get_length()
        x_ctrl = np.array([0, 0.5, 1.0])
        xs = np.linspace(0, L, 200)
        csn = CubicSpline(x_ctrl, -mn_corr)
        csp = CubicSpline(x_ctrl, -mp_corr)

        self.ax2.clear()
        self.ax2.plot(xs, csn(xs), 'b-', lw=1.5, label='Neg corregido')
        self.ax2.fill_between(xs, csn(xs), 0, color='b', alpha=0.25, hatch='//', edgecolor='b')
        self.ax2.plot(xs, csp(xs), 'r-', lw=1.5, label='Pos corregido')
        self.ax2.fill_between(xs, csp(xs), 0, color='r', alpha=0.25, hatch='\\', edgecolor='r')

        if mn_orig is not None and mp_orig is not None:
            csn_o = CubicSpline(x_ctrl, -mn_orig)
            csp_o = CubicSpline(x_ctrl, -mp_orig)
            self.ax2.plot(xs, csn_o(xs), 'b--', alpha=0.5)
            self.ax2.plot(xs, csp_o(xs), 'r--', alpha=0.5)
            self._draw_verticals(self.ax2, csn_o, csp_o, x_ctrl, dashed=True)

        self._draw_verticals(self.ax2, csn, csp, x_ctrl)
        self._label_points(self.ax2, csn, csp, x_ctrl)
        self._enable_hover(self.ax2, csn, csp)
        self._format(self.ax2)
        self.canvas.draw()

    def _draw_verticals(self, ax, csn, csp, x_ctrl, dashed=False):
        style = ':' if dashed else '-'
        for x in x_ctrl:
            ax.plot([x, x], [csn(x), 0], 'k' + style, lw=1)
            ax.plot([x, x], [csp(x), 0], 'k' + style, lw=1)

    def _label_points(self, ax, csn, csp, x_ctrl):
        for x in x_ctrl:
            ax.annotate(f"{-csn(x):.2f}", (x, csn(x)), xytext=(5, 5), textcoords='offset points')
            ax.annotate(f"{abs(csp(x)):.2f}", (x, csp(x)), xytext=(5, -15), textcoords='offset points')

    def _enable_hover(self, ax, csn, csp):
        cursor = mplcursors.cursor(ax.lines[:2], hover=True)

        @cursor.connect("add")
        def _(sel):
            y = sel.target[1]
            val = y if y < 0 else -y
            sel.annotation.set(text=f"{val:.2f}")

    def _format(self, ax):
        ax.set_xlabel('Longitud (m)')
        ax.set_ylabel('Momento (T·m)')
        ax.legend(loc='best')
        ax.grid(True)

    @staticmethod
    def correct_moments(mn, mp, sys_t):
        """Return moments corrected by face and global rules.

        The positive moments at the beam ends (M1+ and M3+) must be at
        least a fraction of the negative moment at that face. Dual 1
        uses 1/3 while Dual 2 uses 1/2. Additionally, all moments must
        not fall below one quarter of the largest face moment.
        """
        mn = np.asarray(mn, dtype=float)
        mp = np.asarray(mp, dtype=float)

        f = 1 / 3 if sys_t.lower() == "dual1" else 1 / 2

        min_face_pos = np.zeros(3)
        min_face_pos[[0, 2]] = f * np.abs(mn[[0, 2]])
        m_max = max(np.max(np.abs(mn)), np.max(np.abs(mp)))
        min_global = m_max / 4.0

        mp_corr = np.maximum.reduce([
            np.abs(mp),
            min_face_pos,
            np.full(3, min_global),
        ])

        mn_corr = -np.maximum(np.abs(mn), min_global)

        return mn_corr, mp_corr

    def on_calculate(self):
        try:
            mn, mp = self.get_moments()
        except ValueError:
            return
        except Exception:
            logging.exception("Unexpected error while obtaining moments")
            return
        sys_t = 'dual2' if self.rb_dual2.isChecked() else 'dual1'
        mn_c, mp_c = MomentApp.correct_moments(mn, mp, sys_t)
        self.plot_original()
        self.plot_corrected(mn_c, mp_c, mn_orig=mn, mp_orig=mp)
        self.mn_corr = mn_c
        self.mp_corr = mp_c

    def on_next(self):
        if self.mn_corr is None or self.mp_corr is None:
            QMessageBox.warning(self, 'Advertencia', 'Primero calcule los momentos corregidos')
            return
        if self.next_callback:
            self.next_callback(self.mn_corr, self.mp_corr)
        else:
            self.design_win = DesignWindow(self.mn_corr, self.mp_corr)
            self.design_win.show()

    def on_save(self):
        if self.save_callback:
            self.save_callback(self.mn_corr, self.mp_corr)

    def on_menu(self):
        if self.menu_callback:
            self.menu_callback()

    def _capture_diagram(self):
        self.canvas.repaint()
        QApplication.processEvents()
        pix = self.canvas.grab()
        QGuiApplication.clipboard().setPixmap(pix)
        # Sin mensaje emergente

