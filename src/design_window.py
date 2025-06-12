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
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication

from .view3d_window import View3DWindow
from .memoria_window import MemoriaWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import numpy as np

# Tabla de diámetros y áreas (cm²) para barras de refuerzo
BAR_DATA = {
    '6mm': 0.28,
    '8mm': 0.50,
    '3/8"': 0.71,
    '12mm': 1.13,
    '1/2"': 1.29,
    '5/8"': 1.99,
    '3/4"': 2.84,
    '1"': 5.10,
}

# Diámetros equivalentes en centímetros para las mismas claves que BAR_DATA
DIAM_CM = {
    '6mm': 0.6,
    '8mm': 0.8,
    '3/8"': 0.95,
    '12mm': 1.2,
    '1/2"': 1.27,
    '5/8"': 1.59,
    '3/4"': 1.91,
    '1"': 2.54,
}

class DesignWindow(QMainWindow):
    """Ventana para la etapa de diseño de acero (solo interfaz gráfica)."""

    def __init__(self, mn_corr, mp_corr, length=1.0):
        """Create the design window using corrected moments."""
        super().__init__()
        self.mn_corr = mn_corr
        self.mp_corr = mp_corr
        self.length = length
        self.setWindowTitle("Parte 2 – Diseño de Acero")
        self._build_ui()
        self.resize(700, 900)

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
            h = float(self.edits["h (cm)"].text())
            r = float(self.edits["r (cm)"].text())
            fc = float(self.edits["f'c (kg/cm²)"].text())
            fy = float(self.edits["fy (kg/cm²)"].text())
            phi = float(self.edits["φ"].text())
            de = DIAM_CM.get(self.cb_estribo.currentText(), 0)
            db = DIAM_CM.get(self.cb_varilla.currentText(), 0)
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
        for l in range(1, 5):
            if layer_areas[l] > 0:
                max_layer = max(max_layer, l)
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

    def _on_length_changed(self):
        """Update stored length when the user edits the L field."""
        try:
            self.length = float(self.edits["L (m)"].text())
        except ValueError:
            self.length = 1.0

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QGridLayout(central)

        labels = [
            ("L (m)", str(self.length)),
            ("b (cm)", "30"),
            ("h (cm)", "50"),
            ("r (cm)", "4"),
            ("d (cm)", ""),
            ("f'c (kg/cm²)", "210"),
            ("fy (kg/cm²)", "4200"),
            ("φ", "0.9"),
        ]

        self.edits = {}
        for row, (text, val) in enumerate(labels):
            layout.addWidget(QLabel(text), row, 0)
            ed = QLineEdit(val)
            ed.setAlignment(Qt.AlignRight)
            ed.setFixedWidth(70)
            if text == "d (cm)":
                ed.setReadOnly(True)
            layout.addWidget(ed, row, 1)
            self.edits[text] = ed
            if text == "L (m)":
                ed.editingFinished.connect(self._on_length_changed)

        # Combos para diámetro de estribo y de varilla
        estribo_opts = ["8mm", "3/8\"", "1/2\""]
        layout.addWidget(QLabel("ϕ estribo"), len(labels), 0)
        self.cb_estribo = QComboBox(); self.cb_estribo.addItems(estribo_opts)
        self.cb_estribo.setCurrentText('3/8"')
        layout.addWidget(self.cb_estribo, len(labels), 1)

        varilla_opts = ["1/2\"", "5/8\"", "3/4\"", "1\""]
        layout.addWidget(QLabel("ϕ varilla"), len(labels)+1, 0)
        self.cb_varilla = QComboBox(); self.cb_varilla.addItems(varilla_opts)
        self.cb_varilla.setCurrentText('5/8"')
        layout.addWidget(self.cb_varilla, len(labels)+1, 1)

        layout.addWidget(QLabel("N\u00b0 capas"), len(labels)+2, 0)
        self.layer_combo = QComboBox(); self.layer_combo.addItems(["1", "2", "3", "4"])
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
            header.addWidget(QLabel("cant."), 0, 0, alignment=Qt.AlignCenter)
            header.addWidget(QLabel("\u00f8''"), 0, 1, alignment=Qt.AlignCenter)
            header.addWidget(QLabel("n\u00b0 capas"), 0, 2, alignment=Qt.AlignCenter)
            header.addWidget(QLabel("capas"), 0, 3, alignment=Qt.AlignCenter)
            cell.addLayout(header)

            rows_layout = QVBoxLayout()
            cell.addLayout(rows_layout)
            self.rows_layouts.append(rows_layout)

            self.combo_grid.addLayout(cell, row, col)

            self._add_rebar_row(i)

        row_start = len(labels) + 3

        layout.addWidget(QLabel("As min (cm²):"), row_start, 2)
        self.as_min_label = QLabel("0.00")
        layout.addWidget(self.as_min_label, row_start, 3)

        layout.addWidget(QLabel("As max (cm²):"), row_start + 1, 2)
        self.as_max_label = QLabel("0.00")
        layout.addWidget(self.as_max_label, row_start + 1, 3)

        layout.addWidget(QLabel("Base req. (cm):"), row_start, 4)
        self.base_req_label = QLabel("-")
        layout.addWidget(self.base_req_label, row_start, 5)
        self.base_msg_label = QLabel("")
        layout.addWidget(self.base_msg_label, row_start + 1, 4, 1, 2)

        self.fig_sec, self.ax_sec = plt.subplots(figsize=(3, 3), constrained_layout=True)
        self.canvas_sec = FigureCanvas(self.fig_sec)
        layout.addWidget(self.canvas_sec, 0, 2, len(labels) + 3, 4)

        self.fig_dist, (self.ax_req, self.ax_des) = plt.subplots(
            2, 1, figsize=(5, 6), constrained_layout=True
        )
        self.canvas_dist = FigureCanvas(self.fig_dist)
        layout.addWidget(self.canvas_dist, row_start + 2, 0, 1, 8)

        layout.addLayout(self.combo_grid, row_start + 3, 0, 1, 8)

        self.btn_capture = QPushButton("Capturar Diseño")
        self.btn_memoria = QPushButton("Memoria de Cálculo")
        self.btn_view3d = QPushButton("Vista 3D")
        self.btn_salir = QPushButton("Salir")

        self.btn_capture.clicked.connect(self._capture_design)
        self.btn_memoria.clicked.connect(self.show_memoria)
        self.btn_view3d.clicked.connect(self.show_view3d)
        self.btn_salir.clicked.connect(QApplication.instance().quit)

        layout.addWidget(self.btn_capture, row_start + 4, 0, 1, 2)
        layout.addWidget(self.btn_memoria, row_start + 4, 2, 1, 2)
        layout.addWidget(self.btn_view3d, row_start + 4, 4, 1, 2)
        layout.addWidget(self.btn_salir,   row_start + 4, 6, 1, 2)

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
        q = QComboBox(); q.addItems(qty_opts); q.setCurrentText("2")
        d = QComboBox(); d.addItems(dia_opts); d.setCurrentText('1/2"')
        c = QComboBox(); c.addItems(["1", "2", "3", "4"]); c.setCurrentText("1")
        btn_add = QPushButton("+")
        btn_rem = QPushButton("-")
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
            de = DIAM_CM.get(self.cb_estribo.currentText(), 0)
            db = DIAM_CM.get(self.cb_varilla.currentText(), 0)
        except ValueError:
            return

        d = self.calc_effective_depth()
        y_d = h - d

        self.ax_sec.clear()
        self.ax_sec.set_aspect('equal')
        self.ax_sec.plot([0, b, b, 0, 0], [0, 0, h, h, 0], 'k-')
        self.ax_sec.plot([r, b - r, b - r, r, r], [r, r, h - r, h - r, r], 'r--')

        self.ax_sec.annotate('', xy=(0, -5), xytext=(b, -5), arrowprops=dict(arrowstyle='<->'))
        self.ax_sec.text(b / 2, -6, 'b', ha='center', va='top')

        # Cota de peralte pegada a la viga
        self.ax_sec.annotate('', xy=(-5, h), xytext=(-5, y_d),
                             arrowprops=dict(arrowstyle='<->'))
        self.ax_sec.text(-6, (h + y_d) / 2, 'd', ha='right', va='center', rotation=90)

        # Cota de altura total hacia la izquierda
        self.ax_sec.annotate('', xy=(-12, 0), xytext=(-12, h),
                             arrowprops=dict(arrowstyle='<->'))
        self.ax_sec.text(-13, h / 2, 'h', ha='right', va='center', rotation=90)

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
            n_tot = 0
            dia_max = 0
            for row in rows:
                try:
                    n = int(row['qty'].currentText()) if row['qty'].currentText() else 0
                except ValueError:
                    n = 0
                dia_key = row['dia'].currentText()
                dia = DIAM_CM.get(dia_key, 0)
                area = BAR_DATA.get(dia_key, 0)
                layer = int(row['capa'].currentText()) if row['capa'].currentText() else 1
                total += n * area
                n_tot += n
                dia_max = max(dia_max, dia)
            totals.append(total)

            try:
                r = float(self.edits["r (cm)"].text())
                de = DIAM_CM.get(self.cb_estribo.currentText(), 0)
                b_val = float(self.edits["b (cm)"].text())
            except ValueError:
                continue
            spacing = max(n_tot - 1, 0) * 2.5
            base_req = 2 * r + 2 * de + n_tot * dia_max + spacing
            base_reqs.append(base_req)

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
        self.repaint()
        QApplication.processEvents()
        pix = self.grab()
        QGuiApplication.clipboard().setPixmap(pix)
        # Sin mensaje emergente

    def show_view3d(self):
        """Open a simple 2D/3D visualization window."""
        self.view3d = View3DWindow(self)
        self.view3d.show()

    def show_memoria(self):
        """Show a detailed calculation window."""
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
            QMessageBox.warning(self, "Error", "Datos num\u00e9ricos inv\u00e1lidos")
            return

        d = h - r - de - 0.5 * db
        beta1 = 0.85 if fc <= 280 else 0.85 - ((fc - 280) / 70) * 0.05
        as_min, as_max = self._calc_as_limits(fc, fy, b, d)

        as_n_raw = [self._calc_as_req(m, fc, b, d, fy, phi) for m in self.mn_corr]
        as_p_raw = [self._calc_as_req(m, fc, b, d, fy, phi) for m in self.mp_corr]
        as_n = np.clip(as_n_raw, as_min, as_max)
        as_p = np.clip(as_p_raw, as_min, as_max)

        lines = [
            "DATOS INGRESADOS:",
            f"b = {b} cm",
            f"h = {h} cm",
            f"r = {r} cm",
            f"f'c = {fc} kg/cm²",
            f"fy = {fy} kg/cm²",
            f"φ = {phi}",
            f"ϕ estribo = {de} cm",
            f"ϕ varilla = {db} cm",
            "",
            "C\u00c1LCULOS:",
            f"d = h - r - ϕ_estribo - 0.5 ϕ_barra = {h} - {r} - {de} - 0.5*{db} = {d:.2f} cm",
            f"β1 = {beta1:.3f}",
            f"As_min = 0.7*√fc/fy*b*d = 0.7*√{fc}/{fy}*{b}*{d:.2f} = {as_min:.2f} cm²",
            f"As_max = 0.75*(0.85*fc*β1/fy)*(6000/(6000+fy))*b*d = {as_max:.2f} cm²",
            "",
            "F\u00d3RMULA GENERAL PARA As:",
            "As = 1.7*fc*b*d/(2*fy) - 0.5*√((2.89*(fc*b*d)^2)/fy^2 - (6.8*fc*b*Mu)/(φ*fy^2))",
            "",
            "DETALLE DEL C\u00c1LCULO DE As POR MOMENTO:",
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
            lines.extend(
                [
                    f"{lab}: Mu = {m:.2f} TN·m = {Mu_kgcm:.0f} kg·cm",
                    f"    As_calc = {term:.2f} - 0.5*√({root:.2f}) = {calc:.2f} cm²",
                    f"    As_req = {a:.2f} cm²",
                ]
            )

        lines.append("")

        title = f"DISE\u00d1O DE VIGA {int(b)}X{int(h)}"
        text = "\n".join(lines)
        self.mem_win = MemoriaWindow(title, text)
        self.mem_win.show()

