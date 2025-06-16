from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication, QFont

from .view3d_window import View3DWindow
from .memoria_window import MemoriaWindow
from ..models.constants import DIAM_CM, BAR_DATA
from ..models.utils import capture_widget_temp
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np


class DesignWindow(QMainWindow):
    """Ventana para la etapa de diseño de acero (solo interfaz gráfica)."""

    def __init__(self, mn_corr, mp_corr, parent=None, *, show_window=True,
                 next_callback=None, save_callback=None, menu_callback=None):
        """Create the design window using corrected moments."""
        super().__init__(parent)
        self.mn_corr = mn_corr
        self.mp_corr = mp_corr
        self.next_callback = next_callback
        self.save_callback = save_callback
        self.menu_callback = menu_callback
        self.setWindowTitle("Parte 2 – Diseño de Acero")
        self._build_ui()
        # Provide enough vertical space so scrolling is rarely needed
        self.resize(800, 1500)
        if show_window:
            self.show()

    def _calc_as_req(self, Mu, fc, b, d, fy, phi):
        """Calculate required steel area for a single moment."""
        Mu_kgcm = abs(Mu) * 100000  # convert TN·m to kg·cm
        term = 1.7 * fc * b * d / (2 * fy)
        root = (2.89 * (fc * b * d) ** 2) / (fy ** 2) - (
            6.8 * fc * b * Mu_kgcm
        ) / (phi * (fy ** 2))
        root = max(root, 0)
        return term - 0.5 * np.sqrt(root)

    def _required_areas(self):
        try:
            b = float(self.edits["b (cm)"].text())
            fc = float(self.edits["f'c (kg/cm²)"].text())
            fy = float(self.edits["fy (kg/cm²)"].text())
            phi = float(self.edits["φ"].text())
        except ValueError:
            return np.zeros(3), np.zeros(3)

        d = self.calc_effective_depth()

        self.as_min, self.as_max = self._calc_as_limits(fc, fy, b, d)
        self.as_min_label.setText(f"{self.as_min:.2f}")
        self.as_max_label.setText(f"{self.as_max:.2f}")

        as_n = [self._calc_as_req(m, fc, b, d, fy, phi) for m in self.mn_corr]
        as_p = [self._calc_as_req(m, fc, b, d, fy, phi) for m in self.mp_corr]

        as_n = np.clip(as_n, self.as_min, self.as_max)
        as_p = np.clip(as_p, self.as_min, self.as_max)

        return np.array(as_n), np.array(as_p)

    def _calc_as_limits(self, fc, fy, b, d):
        beta1 = 0.85 if fc <= 280 else 0.85 - ((fc - 280) / 70) * 0.05
        as_min = 0.7 * (np.sqrt(fc) / fy) * b * d
        pmax = 0.75 * ((0.85 * fc * beta1 / fy) * (6000 / (6000 + fy)))
        as_max = pmax * b * d
        return as_min, as_max

    def calc_effective_depth(self):
        """Return effective depth based on detected layers."""
        try:
            h = float(self.edits["h (cm)"].text())
            r = float(self.edits["r (cm)"].text())
            de = DIAM_CM.get(self.cb_estribo.currentText(), 0)
            db = DIAM_CM.get(self.cb_varilla.currentText(), 0)
        except ValueError:
            return 0.0

        layer_areas = {1: 0, 2: 0, 3: 0, 4: 0}
        layer_diams = {1: db, 2: db, 3: db, 4: db}
        for rows in self.rebar_rows:
            for row in rows:
                try:
                    n = int(row['qty'].currentText()) if row['qty'].currentText() else 0
                except ValueError:
                    n = 0
                dia_key = row['dia'].currentText()
                area = n * BAR_DATA.get(dia_key, 0)
                layer = int(row['capa'].currentText()) if row['capa'].currentText() else 1
                if area > layer_areas[layer]:
                    layer_areas[layer] = area
                    layer_diams[layer] = DIAM_CM.get(dia_key, 0)

        max_layer = 1
        for layer_num in range(1, 5):
            if layer_areas[layer_num] > 0:
                max_layer = max(max_layer, layer_num)
        self.layer_combo.setCurrentText(str(max_layer))

        db1 = layer_diams[1]
        d1 = h - r - de - 0.5 * db1
        if max_layer == 1:
            d = d1
        else:
            db2 = layer_diams[2]
            d2 = h - r - de - db1 - 2.5 - 0.5 * db2
            if max_layer == 2:
                As1 = layer_areas[1]
                As2 = layer_areas[2]
                d = (d1 * As1 + d2 * As2) / (As1 + As2) if (As1 + As2) else d1
            else:
                db3 = layer_diams[3]
                d3 = h - r - de - db1 - 2.5 - db2 - 2.5 - 0.5 * db3
                if max_layer == 3:
                    As1 = layer_areas[1]
                    As2 = layer_areas[2]
                    As3 = layer_areas[3]
                    s = As1 + As2 + As3
                    d = (d1*As1 + d2*As2 + d3*As3) / s if s else d1
                else:
                    d4 = d3 - 3
                    As1 = layer_areas[1]
                    As2 = layer_areas[2]
                    As3 = layer_areas[3]
                    As4 = layer_areas[4]
                    s = As1 + As2 + As3 + As4
                    d = (d1*As1 + d2*As2 + d3*As3 + d4*As4) / s if s else d1

        self.edits["d (cm)"].setText(f"{d:.2f}")
        return d

    def _build_ui(self):
        content = QWidget()
        layout = QGridLayout(content)
        layout.setVerticalSpacing(3)
        layout.setSizeConstraint(QLayout.SetMinimumSize)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setWidget(content)
        self.setCentralWidget(scroll)
        self.scroll_area = scroll

        labels = [
            ("b (cm)", "30"),
            ("h (cm)", "50"),
            ("r (cm)", "4"),
            ("d (cm)", ""),
            ("f'c (kg/cm²)", "210"),
            ("fy (kg/cm²)", "4200"),
            ("φ", "0.9"),
        ]

        small_font = QFont()
        small_font.setPointSize(8)
        # Font for the manual design widgets at the bottom
        self.row_font = QFont()
        self.row_font.setPointSize(8)

        self.edits = {}
        for row, (text, val) in enumerate(labels):
            lbl = QLabel(text)
            lbl.setFont(small_font)
            layout.addWidget(lbl, row, 0)
            ed = QLineEdit(val)
            ed.setFont(small_font)
            ed.setAlignment(Qt.AlignRight)
            ed.setFixedWidth(70)
            if text == "d (cm)":
                ed.setReadOnly(True)
            layout.addWidget(ed, row, 1)
            self.edits[text] = ed

        # Combos para diámetro de estribo y de varilla
        estribo_opts = ["8mm", "3/8\"", "1/2\""]
        lbl_estribo = QLabel("ϕ estribo")
        lbl_estribo.setFont(small_font)
        layout.addWidget(lbl_estribo, len(labels), 0)
        self.cb_estribo = QComboBox()
        self.cb_estribo.setFont(small_font)
        self.cb_estribo.addItems(estribo_opts)
        self.cb_estribo.setCurrentText('3/8"')
        layout.addWidget(self.cb_estribo, len(labels), 1)

        varilla_opts = ["1/2\"", "5/8\"", "3/4\"", "1\""]
        lbl_varilla = QLabel("ϕ varilla")
        lbl_varilla.setFont(small_font)
        layout.addWidget(lbl_varilla, len(labels)+1, 0)
        self.cb_varilla = QComboBox()
        self.cb_varilla.setFont(small_font)
        self.cb_varilla.addItems(varilla_opts)
        self.cb_varilla.setCurrentText('5/8"')
        layout.addWidget(self.cb_varilla, len(labels)+1, 1)

        lbl_capas = QLabel("N\u00b0 capas")
        lbl_capas.setFont(small_font)
        layout.addWidget(lbl_capas, len(labels)+2, 0)
        self.layer_combo = QComboBox()
        self.layer_combo.setFont(small_font)
        self.layer_combo.addItems(["1", "2", "3", "4"])
        layout.addWidget(self.layer_combo, len(labels)+2, 1)

        pos_labels = ["M1-", "M2-", "M3-", "M1+", "M2+", "M3+"]
        self.rebar_rows = [[] for _ in range(6)]
        self.rows_layouts = []

        self.combo_grid = QGridLayout()

        for i, label in enumerate(pos_labels):
            row = 0 if i < 3 else 1
            col = i % 3

            cell = QVBoxLayout()
            cell.addWidget(QLabel(label), alignment=Qt.AlignCenter)

            header = QGridLayout()

            lbl_qty = QLabel("cant.")
            lbl_qty.setFont(self.row_font)
            lbl_qty.setAlignment(Qt.AlignCenter)
            header.addWidget(lbl_qty, 0, 0)

            lbl_dia = QLabel("\u00f8")
            lbl_dia.setFont(self.row_font)
            lbl_dia.setAlignment(Qt.AlignCenter)
            header.addWidget(lbl_dia, 0, 1)

            lbl_ncapas = QLabel("capa")
            lbl_ncapas.setFont(self.row_font)
            lbl_ncapas.setAlignment(Qt.AlignCenter)
            header.addWidget(lbl_ncapas, 0, 2)

            lbl_capas = QLabel("capas")
            lbl_capas.setFont(self.row_font)
            lbl_capas.setAlignment(Qt.AlignCenter)
            header.addWidget(lbl_capas, 0, 3, 1, 2)
            cell.addLayout(header)

            rows_layout = QVBoxLayout()
            cell.addLayout(rows_layout)
            self.rows_layouts.append(rows_layout)

            self.combo_grid.addLayout(cell, row, col)

            self._add_rebar_row(i)

        row_start = len(labels) + 3

        info_layout = QHBoxLayout()
        info_layout.setSpacing(5)
        info_layout.setContentsMargins(0, 0, 0, 0)

        lbl_as_min = QLabel("As min (cm²):")
        lbl_as_min.setFont(small_font)
        self.as_min_label = QLabel("0.00")
        self.as_min_label.setFont(small_font)
        info_layout.addWidget(lbl_as_min)
        info_layout.addWidget(self.as_min_label)

        lbl_as_max = QLabel("As max (cm²):")
        lbl_as_max.setFont(small_font)
        self.as_max_label = QLabel("0.00")
        self.as_max_label.setFont(small_font)
        info_layout.addWidget(lbl_as_max)
        info_layout.addWidget(self.as_max_label)

        lbl_base_req = QLabel("Base req. (cm):")
        lbl_base_req.setFont(small_font)
        self.base_req_label = QLabel("-")
        self.base_req_label.setFont(small_font)
        info_layout.addWidget(lbl_base_req)
        info_layout.addWidget(self.base_req_label)

        self.base_msg_label = QLabel("")
        self.base_msg_label.setFont(small_font)
        info_layout.addWidget(self.base_msg_label)

        layout.addLayout(info_layout, row_start, 2, 1, 6)

        self.fig_sec, self.ax_sec = plt.subplots(figsize=(3, 3), constrained_layout=True)
        self.canvas_sec = FigureCanvas(self.fig_sec)
        layout.addWidget(self.canvas_sec, 0, 2, len(labels) + 3, 4)

        self.fig_dist, (self.ax_req, self.ax_des) = plt.subplots(
            2, 1, figsize=(5, 6), constrained_layout=True
        )
        self.canvas_dist = FigureCanvas(self.fig_dist)
        layout.addWidget(self.canvas_dist, row_start + 1, 0, 1, 8)

        layout.addLayout(self.combo_grid, row_start + 2, 0, 1, 8)

        self.btn_capture = QPushButton("CAPTURA")
        self.btn_memoria = QPushButton("REPORTES")
        self.btn_view3d = QPushButton("SECCIONES")
        self.btn_menu = QPushButton("Menú")

        self.btn_capture.clicked.connect(self._capture_design)
        self.btn_memoria.clicked.connect(self.show_memoria)
        self.btn_view3d.clicked.connect(self.on_next)
        self.btn_menu.clicked.connect(self.on_menu)

        layout.addWidget(self.btn_capture, row_start + 3, 0, 1, 2)
        layout.addWidget(self.btn_memoria, row_start + 3, 2, 1, 2)
        layout.addWidget(self.btn_view3d,  row_start + 3, 4, 1, 2)
        layout.addWidget(self.btn_menu,    row_start + 3, 6, 1, 2)

        for ed in self.edits.values():
            ed.editingFinished.connect(self._redraw)
        for cb in (self.cb_estribo, self.cb_varilla):
            cb.currentIndexChanged.connect(self._redraw)

        for rows in self.rebar_rows:
            for row in rows:
                for box in (row['qty'], row['dia'], row['capa']):
                    box.currentIndexChanged.connect(self.update_design_as)

        self.as_min = 0.0
        self.as_max = 0.0
        self.as_total = 0.0

        self.draw_section()
        self.draw_required_distribution()
        self.update_design_as()

    def _add_rebar_row(self, idx):
        if len(self.rebar_rows[idx]) >= 4:
            return
        qty_opts = [""] + [str(i) for i in range(1, 11)]
        dia_opts = ["", "1/2\"", "5/8\"", "3/4\"", "1\""]
        row_layout = QHBoxLayout()
        row_layout.setSpacing(2)
        row_layout.setContentsMargins(0, 0, 0, 0)

        q = QComboBox()
        q.addItems(qty_opts)
        q.setFont(self.row_font)
        q.setFixedWidth(50)
        q.setCurrentText("2")

        d = QComboBox()
        d.addItems(dia_opts)
        d.setFont(self.row_font)
        d.setFixedWidth(60)
        d.setCurrentText('1/2"')

        c = QComboBox()
        c.addItems(["1", "2", "3", "4"])
        c.setFont(self.row_font)
        c.setFixedWidth(50)
        c.setCurrentText("1")
        btn_add = QPushButton("+")
        btn_add.setFixedWidth(20)
        btn_rem = QPushButton("-")
        btn_rem.setFixedWidth(20)
        row_layout.addWidget(q)
        row_layout.addWidget(d)
        row_layout.addWidget(c)
        row_layout.addWidget(btn_add)
        row_layout.addWidget(btn_rem)
        widget = QWidget()
        widget.setLayout(row_layout)
        self.rows_layouts[idx].addWidget(widget)
        self.rebar_rows[idx].append({"qty": q, "dia": d, "capa": c, "widget": widget})
        btn_add.clicked.connect(lambda: self._add_rebar_row(idx))
        btn_rem.clicked.connect(lambda: self._remove_rebar_row(idx, widget))
        for box in (q, d, c):
            box.currentIndexChanged.connect(self.update_design_as)

    def _remove_rebar_row(self, idx, widget):
        if len(self.rebar_rows[idx]) <= 1:
            return
        widget.setParent(None)
        self.rebar_rows[idx] = [r for r in self.rebar_rows[idx] if r["widget"] != widget]
        self.update_design_as()

    def draw_section(self):
        """Draw a schematic beam section based on input dimensions."""
        try:
            b = float(self.edits["b (cm)"].text())
            h = float(self.edits["h (cm)"].text())
            r = float(self.edits["r (cm)"].text())
        except ValueError:
            return

        d = self.calc_effective_depth()
        y_d = h - d

        self.ax_sec.clear()
        self.ax_sec.set_aspect('equal')
        self.ax_sec.plot([0, b, b, 0, 0], [0, 0, h, h, 0], 'k-')
        self.ax_sec.plot([r, b - r, b - r, r, r], [r, r, h - r, h - r, r], 'r--')

        self.ax_sec.annotate('', xy=(0, -5), xytext=(b, -5),
                             arrowprops=dict(arrowstyle='<->'))
        self.ax_sec.text(
            b / 2,
            -6,
            f"b = {b:.0f} cm",
            ha='center',
            va='top',
            fontsize=8,
        )

        # Cota de peralte pegada a la viga
        self.ax_sec.annotate('', xy=(-5, h), xytext=(-5, y_d),
                             arrowprops=dict(arrowstyle='<->'))
        self.ax_sec.text(
            -6,
            (h + y_d) / 2,
            f"d = {d:.1f} cm",
            ha='right',
            va='center',
            rotation=90,
            fontsize=8,
        )

        # Cota de altura total hacia la izquierda
        self.ax_sec.annotate('', xy=(-12, 0), xytext=(-12, h),
                             arrowprops=dict(arrowstyle='<->'))
        self.ax_sec.text(
            -13,
            h / 2,
            f"h = {h:.0f} cm",
            ha='right',
            va='center',
            rotation=90,
            fontsize=8,
        )

        self.ax_sec.set_xlim(-15, b + 10)
        self.ax_sec.set_ylim(-10, h + 10)
        self.ax_sec.axis('off')
        self.canvas_sec.draw()

    def _redraw(self):
        self.draw_section()
        self.draw_required_distribution()
        self.update_design_as()

    def draw_required_distribution(self):
        """Plot the required steel areas along the beam length."""
        x_ctrl = [0.0, 0.5, 1.0]
        areas_n, areas_p = self._required_areas()

        self.ax_req.clear()
        self.ax_req.plot([0, 1], [0, 0], 'k-', lw=6)

        y_off = 0.1 * max(np.max(areas_n), np.max(areas_p), 1)
        label_off = 0.2 * y_off
        for idx, (x, a_n) in enumerate(zip(x_ctrl, areas_n), 1):
            self.ax_req.text(x, y_off, f"As- {a_n:.2f}", ha='center',
                             va='bottom', color='b', fontsize=9)
            self.ax_req.text(x, label_off, f"M{idx}-", ha='center',
                             va='bottom', fontsize=7)
        for idx, (x, a_p) in enumerate(zip(x_ctrl, areas_p), 1):
            self.ax_req.text(x, -y_off, f"As+ {a_p:.2f}", ha='center',
                             va='top', color='r', fontsize=9)
            self.ax_req.text(x, -label_off, f"M{idx}+", ha='center',
                             va='top', fontsize=7)

        self.ax_req.set_xlim(-0.05, 1.05)
        self.ax_req.set_ylim(-2*y_off, 2*y_off)
        self.ax_req.axis('off')
        self.canvas_dist.draw()

    def update_design_as(self):
        """Check selected reinforcement and update design area labels."""
        as_req_n, as_req_p = self._required_areas()
        as_reqs = list(as_req_n) + list(as_req_p)
        totals = []
        base_reqs = []

        for idx, rows in enumerate(self.rebar_rows):
            total = 0
            layers = {
                1: {"n": 0, "sum_d": 0.0},
                2: {"n": 0, "sum_d": 0.0},
            }

            for row in rows:
                try:
                    n = int(row["qty"].currentText()) if row["qty"].currentText() else 0
                except ValueError:
                    n = 0
                dia_key = row["dia"].currentText()
                dia = DIAM_CM.get(dia_key, 0)
                area = BAR_DATA.get(dia_key, 0)
                layer = int(row["capa"].currentText()) if row["capa"].currentText() else 1
                total += n * area
                if layer in layers:
                    layers[layer]["n"] += n
                    layers[layer]["sum_d"] += n * dia
            totals.append(total)

            try:
                r = float(self.edits["r (cm)"].text())
                de = DIAM_CM.get(self.cb_estribo.currentText(), 0)
            except ValueError:
                continue

            b_layers = []
            for ldata in layers.values():
                n_l = ldata["n"]
                spacing = max(n_l - 1, 0) * 2.5
                b_l = 2 * r + 2 * de + spacing + ldata["sum_d"]
                b_layers.append(b_l)
            base_reqs.append(max(b_layers))

        self.as_total = sum(totals)

        if base_reqs:
            max_base = max(base_reqs)
            self.base_req_label.setText(f"{max_base:.1f}")
            try:
                b_val = float(self.edits["b (cm)"].text())
            except ValueError:
                self.base_msg_label.setText("")
            else:
                self.base_msg_label.setText("OK" if max_base <= b_val else "Aumentar base o capa")

        statuses = ["OK" if t >= req else "NO OK" for t, req in zip(totals, as_reqs)]

        self.draw_design_distribution(totals, statuses)

    def draw_design_distribution(self, areas, statuses):
        """Plot chosen reinforcement distribution along the beam."""
        x_ctrl = [0.0, 0.5, 1.0]
        areas_n = areas[:3]
        areas_p = areas[3:]
        self.ax_des.clear()
        self.ax_des.plot([0, 1], [0, 0], 'k-', lw=6)
        y_off = 0.1 * max(max(areas_n, default=0), max(areas_p, default=0), 1)
        label_off = 0.2 * y_off
        for idx, (x, a, st) in enumerate(zip(x_ctrl, areas_n, statuses[:3]), 1):
            self.ax_des.text(x, y_off, f"Asd- {a:.2f} {st}", ha='center',
                             va='bottom', color='g', fontsize=9)
            self.ax_des.text(x, label_off, f"M{idx}-", ha='center',
                             va='bottom', fontsize=7)
        for idx, (x, a, st) in enumerate(zip(x_ctrl, areas_p, statuses[3:]), 1):
            self.ax_des.text(x, -y_off, f"Asd+ {a:.2f} {st}", ha='center',
                             va='top', color='g', fontsize=9)
            self.ax_des.text(x, -label_off, f"M{idx}+", ha='center',
                             va='top', fontsize=7)
        self.ax_des.set_xlim(-0.05, 1.05)
        self.ax_des.set_ylim(-2 * y_off, 2 * y_off)
        self.ax_des.axis('off')
        self.canvas_dist.draw()

    def _capture_design(self):
        widgets = [self.btn_capture, self.btn_memoria, self.btn_view3d, self.btn_menu]
        for w in widgets:
            w.hide()
        self.repaint()
        QApplication.processEvents()
        target = self.scroll_area.widget() if hasattr(self, "scroll_area") else self.centralWidget()
        pix = target.grab()
        QGuiApplication.clipboard().setPixmap(pix)
        for w in widgets:
            w.show()
        # Sin mensaje emergente

    def show_view3d(self):
        """Open a window with cross-section views."""
        self.view3d = View3DWindow(self)
        self.view3d.show()

    def show_memoria(self):
        """Show a detailed calculation window."""
        title, data = self._build_memoria()
        if title is None or data is None:
            return
        self.mem_win = MemoriaWindow(title, data)
        self.mem_win.show()

    def _build_memoria(self):
        """Return title and structured data for the calculation memory."""
        try:
            b = float(self.edits["b (cm)"].text())
            h = float(self.edits["h (cm)"].text())
            r = float(self.edits["r (cm)"].text())
            fc = float(self.edits["f'c (kg/cm²)"].text())
            fy = float(self.edits["fy (kg/cm²)"].text())
            phi = float(self.edits["φ"].text())
            de = DIAM_CM.get(self.cb_estribo.currentText(), 0)
            db = DIAM_CM.get(self.cb_varilla.currentText(), 0)
        except ValueError:
            QMessageBox.warning(self, "Error", "Datos numéricos inválidos")
            return None, None

        d = h - r - de - 0.5 * db
        beta1 = 0.85 if fc <= 280 else 0.85 - ((fc - 280) / 70) * 0.05
        as_min, as_max = self._calc_as_limits(fc, fy, b, d)

        as_n_raw = [self._calc_as_req(m, fc, b, d, fy, phi) for m in self.mn_corr]
        as_p_raw = [self._calc_as_req(m, fc, b, d, fy, phi) for m in self.mp_corr]
        as_n = np.clip(as_n_raw, as_min, as_max)
        as_p = np.clip(as_p_raw, as_min, as_max)

        title_text = f"Diseño a flexión de viga {int(b)}x{int(h)}"

        data_section = [
            ["b (cm)", f"{b}"],
            ["h (cm)", f"{h}"],
            ["r (cm)", f"{r}"],
            ["f'c (kg/cm²)", f"{fc}"],
            ["fy (kg/cm²)", f"{fy}"],
            ["φ", f"{phi}"],
            ["ϕ estribo (cm)", f"{de}"],
            ["ϕ varilla (cm)", f"{db}"],
        ]

        calc_sections = [
            ("Cálculo del peralte efectivo", [
                "d = h - r - ϕ estribo - 1/2 ϕ barra",
                f"d = {h} - {r} - {de} - 1/2 * {db}",
                f"d = {d:.2f} cm",
            ]),
            ("Coeficiente β1", [
                "β1 = 0.85" if fc <= 280 else f"β1 = 0.85 - 0.05*(({fc}-280)/70) = {beta1:.3f}",
            ]),
            ("As_min", [
                "As_min = 0.7 * sqrt(fc)/fy * b * d",
                f"As_min = 0.7 * sqrt({fc})/{fy} * {b} * {d:.2f}",
                f"As_min = {as_min:.2f} cm²",
            ]),
            ("As_max", [
                "As_max = 0.75*(0.85 fc β1 / fy)*(6000/(6000+fy))*b*d",
                f"As_max = {as_max:.2f} cm²",
            ]),
            ("Fórmula general para As", [
                "As = (1.7 fc b d)/(2 fy) - 1/2 sqrt((2.89 (fc b d)^2)/fy^2 - (6.8 fc b Mu)/(φ fy^2))",
            ]),
        ]

        labels = ["M1-", "M2-", "M3-", "M1+", "M2+", "M3+"]
        for lab, m, a_raw, a in zip(
            labels,
            list(self.mn_corr) + list(self.mp_corr),
            as_n_raw + as_p_raw,
            as_n.tolist() + as_p.tolist(),
        ):
            Mu_kgcm = abs(m) * 100000
            term = 1.7 * fc * b * d / (2 * fy)
            root = (
                (2.89 * (fc * b * d) ** 2) / (fy ** 2)
                - (6.8 * fc * b * Mu_kgcm) / (phi * (fy ** 2))
            )
            root = max(root, 0)
            calc = term - 0.5 * np.sqrt(root)
            calc_sections.append((
                f"As para {lab}",
                [
                    f"Mu = {m:.2f} TN·m = {Mu_kgcm:.0f} kg·cm",
                    f"As_calc = {calc:.2f} cm²",
                    f"As_req = {a:.2f} cm²",
                ],
            ))

        result_section = [
            ("As_min", f"{as_min:.2f} cm²"),
            ("As_max", f"{as_max:.2f} cm²"),
        ]
        for lab, val in zip(labels, as_n.tolist() + as_p.tolist()):
            result_section.append((f"As req {lab}", f"{val:.2f} cm²"))

        images = []
        img = capture_widget_temp(self.canvas_sec, "sec_")
        if img:
            images.append(img)
        try:
            view = View3DWindow(self, show_window=False)
            img_view = capture_widget_temp(view.canvas, "view3d_")
            view.close()
            if img_view:
                images.append(img_view)
        except Exception:
            pass

        title = title_text
        data = {
            "data_section": data_section,
            "calc_sections": calc_sections,
            "results": result_section,
            "images": images,
        }
        return title, data


    def on_next(self):
        if self.next_callback:
            self.next_callback()
        else:
            self.show_view3d()

    def on_save(self):
        if self.save_callback:
            self.save_callback()

    def on_menu(self):
        if self.menu_callback:
            self.menu_callback()

