from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QComboBox,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
)
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QGuiApplication

from .view3d_window import View3DWindow
from reporte_flexion_html import generar_reporte_html
from ..models.constants import DIAM_CM, BAR_DATA
from ..models.utils import capture_widget_temp
from .design import (
    build_ui,
    calc_as_limits,
    calc_as_req,
    draw_section,
    plot_design,
    plot_required,
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np


class DesignWindow(QMainWindow):
    """Ventana para la etapa de diseño de acero (solo interfaz gráfica)."""

    def __init__(
        self,
        mn_corr,
        mp_corr,
        parent=None,
        *,
        show_window=True,
        next_callback=None,
        save_callback=None,
        menu_callback=None,
        back_callback=None,
    ):
        """Create the design window using corrected moments."""
        super().__init__(parent)
        self.mn_corr = mn_corr
        self.mp_corr = mp_corr
        self.next_callback = next_callback
        self.save_callback = save_callback
        self.menu_callback = menu_callback
        self.setWindowTitle("Parte 2 – Diseño de Acero")
        self.back_callback = back_callback
        self._build_ui()
        # Provide enough vertical space so scrolling is rarely needed
        self.resize(800, 1500)
        if show_window:
            self.show()

    def update_moments(self, mn_corr, mp_corr):
        """Update the design moments and redraw plots."""
        self.mn_corr = mn_corr
        self.mp_corr = mp_corr
        self._redraw()


    def _required_areas(self):
        try:
            b = float(self.edits["b (cm)"].text())
            fc = float(self.edits["f'c (kg/cm²)"].text())
            fy = float(self.edits["fy (kg/cm²)"].text())
            phi = float(self.edits["φ"].text())
        except ValueError:
            return np.zeros(3), np.zeros(3)

        d = self.calc_effective_depth()

        self.as_min, self.as_max = calc_as_limits(fc, fy, b, d)
        self.as_min_label.setText(f"{self.as_min:.2f}")
        self.as_max_label.setText(f"{self.as_max:.2f}")

        # Raw areas computed directly from the general formula
        as_n_raw = [calc_as_req(m, fc, b, d, fy, phi) for m in self.mn_corr]
        as_p_raw = [calc_as_req(m, fc, b, d, fy, phi) for m in self.mp_corr]

        # Store raw values for potential debugging/reporting purposes
        self.as_n_raw = np.array(as_n_raw)
        self.as_p_raw = np.array(as_p_raw)

        # Enforce minimum and maximum reinforcement limits
        as_n = np.clip(self.as_n_raw, self.as_min, self.as_max)
        as_p = np.clip(self.as_p_raw, self.as_min, self.as_max)

        return as_n, as_p

    def _design_areas(self):
        """Return current design steel areas for each section."""
        totals = []
        for rows in self.rebar_rows:
            total = 0.0
            for row in rows:
                try:
                    n = int(row["qty"].currentText()) if row["qty"].currentText() else 0
                except ValueError:
                    n = 0
                dia_key = row["dia"].currentText()
                area = BAR_DATA.get(dia_key, 0)
                total += n * area
            totals.append(total)
        return totals


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
                    n = int(row["qty"].currentText()) if row["qty"].currentText() else 0
                except ValueError:
                    n = 0
                dia_key = row["dia"].currentText()
                area = n * BAR_DATA.get(dia_key, 0)
                layer = (
                    int(row["capa"].currentText()) if row["capa"].currentText() else 1
                )
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
                    d = (d1 * As1 + d2 * As2 + d3 * As3) / s if s else d1
                else:
                    d4 = d3 - 3
                    As1 = layer_areas[1]
                    As2 = layer_areas[2]
                    As3 = layer_areas[3]
                    As4 = layer_areas[4]
                    s = As1 + As2 + As3 + As4
                    d = (d1 * As1 + d2 * As2 + d3 * As3 + d4 * As4) / s if s else d1

        self.edits["d (cm)"].setText(f"{d:.2f}")
        return d

    def _build_ui(self):
        """Create widgets and connect signals."""
        build_ui(self)

        self.btn_capture.clicked.connect(self._capture_design)
        self.btn_memoria.clicked.connect(self.show_memoria)
        self.btn_view3d.clicked.connect(self.on_next)
        self.btn_menu.clicked.connect(self.on_menu)
        self.btn_back.clicked.connect(self.on_back)

        for ed in self.edits.values():
            ed.editingFinished.connect(self._redraw)
        for cb in (self.cb_estribo, self.cb_varilla):
            cb.currentIndexChanged.connect(self._redraw)

        for rows in self.rebar_rows:
            for row in rows:
                for box in (row["qty"], row["dia"], row["capa"]):
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
        dia_opts = ["", '1/2"', '5/8"', '3/4"', '1"']
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
        self.rebar_rows[idx] = [
            r for r in self.rebar_rows[idx] if r["widget"] != widget
        ]
        self.update_design_as()

    def draw_section(self):
        """Draw the beam section based on current inputs."""
        try:
            b = float(self.edits["b (cm)"].text())
            h = float(self.edits["h (cm)"].text())
            r = float(self.edits["r (cm)"].text())
        except ValueError:
            return

        d = self.calc_effective_depth()
        draw_section(self.ax_sec, b, h, r, d)
        self.canvas_sec.draw()

    def _redraw(self):
        self.draw_section()
        self.draw_required_distribution()
        self.update_design_as()

    def draw_required_distribution(self):
        """Plot the required steel areas along the beam length."""
        areas_n, areas_p = self._required_areas()
        plot_required(self.ax_req, areas_n, areas_p)
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
                layer = (
                    int(row["capa"].currentText()) if row["capa"].currentText() else 1
                )
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
                self.base_msg_label.setText(
                    "OK" if max_base <= b_val else "Aumentar base o capa"
                )

        statuses = ["OK" if t >= req else "NO OK" for t, req in zip(totals, as_reqs)]

        self.draw_design_distribution(totals, statuses)

    def draw_design_distribution(self, areas, statuses):
        """Plot chosen reinforcement distribution along the beam."""
        plot_design(self.ax_des, areas, statuses)
        self.canvas_dist.draw()

    def _capture_design(self):
        widgets = [
            self.btn_capture,
            self.btn_memoria,
            self.btn_view3d,
            self.btn_menu,
            self.btn_back,
        ]
        for w in widgets:
            w.hide()
        self.repaint()
        QApplication.processEvents()
        target = (
            self.scroll_area.widget()
            if hasattr(self, "scroll_area")
            else self.centralWidget()
        )
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
        """Generate the HTML report directly."""
        _, data = self._build_memoria()
        if data is None:
            return
        datos = {k: v for k, v in data.get("data_section", [])}
        calc_sections = data.get("calc_sections", [])
        keys = ["peralte", "b1", "pbal", "pmax", "as_min", "as_max"]
        resultados = {}
        for key, sec in zip(keys, calc_sections[:6]):
            forms = [f.strip("$") for f in sec[1]]
            resultados[key] = {
                "general": forms[0] if len(forms) > 0 else "",
                "reemplazo": forms[1] if len(forms) > 1 else "",
                "resultado": forms[2] if len(forms) > 2 else "",
            }
        tabla = data.get("verif_table", [])
        imagenes = data.get("images", [])
        seccion = data.get("section_img")
        dev_as = calc_sections[6:]
        generar_reporte_html(datos, resultados, tabla, imagenes, seccion, dev_as)

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
        as_min, as_max = calc_as_limits(fc, fy, b, d)
        p_bal = (0.85 * fc * beta1 / fy) * (6000 / (6000 + fy))
        p_max = 0.75 * p_bal

        as_n_raw = [calc_as_req(m, fc, b, d, fy, phi) for m in self.mn_corr]
        as_p_raw = [calc_as_req(m, fc, b, d, fy, phi) for m in self.mp_corr]
        as_n = np.clip(as_n_raw, as_min, as_max)
        as_p = np.clip(as_p_raw, as_min, as_max)

        # Main title uses actual beam dimensions without truncating decimals
        title_text = f"DISEÑO A FLEXIÓN DE VIGA {b:g}x{h:g}"

        data_section = [
            ["b (cm)", f"{b}"],
            ["h (cm)", f"{h}"],
            ["d (cm)", f"{d:.2f}"],
            ["r (cm)", f"{r}"],
            ["f'c (kg/cm²)", f"{fc}"],
            ["fy (kg/cm²)", f"{fy}"],
            ["φ", f"{phi}"],
            ["ϕ estribo (cm)", f"{de}"],
            ["ϕ varilla (cm)", f"{db}"],
        ]

        calc_sections = [
            (
                "Peralte efectivo: d <span class='norma'>(E060 Art. 17.5.2)</span>",
                [
                    r"$d = h - d_e - \frac{1}{2} d_b - r$",
                    rf"$d = {h} - {de} - \frac{{1}}{{2}} {db} - {r}$",
                    rf"$d = {d:.2f}\,\text{{cm}}$",
                ],
            ),
            (
                "Coeficiente B1 <span class='norma'>(E060 Art. 10.2.7.3)</span>",
                [
                    (
                        r"$\beta_1 = 0.85$"
                        if fc <= 280
                        else rf"$\beta_1 = 0.85 - 0.05\times\frac{{{fc}-280}}{{70}} = {beta1:.3f}$"
                    ),
                ],
            ),
            (
                "\u03c1<sub>bal</sub> <span class='norma'>(E060 Art. 10.3.32)</span>",
                [
                    r"$\rho_{bal}=\left(\frac{0.85 f_c \beta_1}{f_y}\right)\,\frac{6000}{6000+f_y}$",
                    rf"$\rho_{{bal}}=\left(\frac{{0.85\,{fc}\,{beta1:.3f}}}{{{fy}}}\right)\,\frac{{6000}}{{6000+{fy}}}$",
                    rf"$\rho_{{bal}} = {p_bal:.4f}$",
                ],
            ),
            (
                "\u03c1<sub>max</sub> <span class='norma'>(E060 Art. 10.3.4)</span>",
                [
                    r"$\rho_{max}=0.75\,\rho_{bal}$",
                    rf"$\rho_{{max}}=0.75\times{p_bal:.4f}$",
                    rf"$\rho_{{max}} = {p_max:.4f}$",
                ],
            ),
            (
                'As mín <span class="norma">(E060 Art. 10.5.2)</span>',
                [
                    r"$A_s^{\text{min}} = 0.7\,\frac{\sqrt{f_c}}{f_y}\, b\, d$",
                    rf"$A_s^{{\text{{min}}}} = 0.7\,\frac{{\sqrt{{{fc}}}}}{{{fy}}}\,{b}\,{d:.2f}$",
                    rf"$A_s^{{\text{{min}}}} = {as_min:.2f}\,\text{{cm}}^2$",
                ],
            ),
            (
                'As máx <span class="norma">(E060 Art. 10.3.4)</span>',
                [
                    r"$A_s^{\text{max}} = 0.75\,\left(\frac{0.85 f_c \beta_1}{f_y}\right)\,\left(\frac{6000}{6000+f_y}\right)\,b\,d$",
                    rf"$A_s^{{\text{{max}}}} = {as_max:.2f}\,\text{{cm}}^2$",
                ],
            ),
            (
                "Fórmula general del A_s",
                [
                    r"$A_s = \frac{1.7 f_c b d}{2 f_y} - \frac{1}{2} \sqrt{\frac{2.89(f_c b d)^2}{f_y^2} - \frac{6.8 f_c b M_u}{\phi f_y^2}}$",
                ],
            ),
        ]

        labels = ["M1-", "M2-", "M3-", "M1+", "M2+", "M3+"]
        design_totals = self._design_areas()
        verif_table = []
        for lab, m, a_raw, a, des in zip(
            labels,
            list(self.mn_corr) + list(self.mp_corr),
            as_n_raw + as_p_raw,
            as_n.tolist() + as_p.tolist(),
            design_totals,
        ):
            Mu_kgcm = abs(m) * 100000
            term = 1.7 * fc * b * d / (2 * fy)
            root = (2.89 * (fc * b * d) ** 2) / (fy**2) - (6.8 * fc * b * Mu_kgcm) / (
                phi * (fy**2)
            )
            root = max(root, 0)
            calc = term - 0.5 * np.sqrt(root)
            calc_sections.append(
                (
                    f"Calculo para {lab}",
                    [
                        rf"$M_u = {m:.2f}\,\text{{TN·m}} = {Mu_kgcm:.0f}\,\text{{kg·cm}}$",
                        rf"$A_s^{{\text{{calc}}}} = {calc:.2f}\,\text{{cm}}^2$",
                        rf"$A_s^{{\text{{req}}}} = {a:.2f}\,\text{{cm}}^2$",
                    ],
                )
            )
            estado = "\u2714 Cumple" if des >= a else "\u2716 No cumple"
            verif_table.append([lab, f"{a:.2f}", f"{des:.2f}", estado])

        result_section = [
            ("As_min", f"{as_min:.2f} cm²"),
            ("As_max", f"{as_max:.2f} cm²"),
        ]
        for lab, val in zip(labels, as_n.tolist() + as_p.tolist()):
            result_section.append((f"As req {lab}", f"{val:.2f} cm²"))

        images = []
        try:
            view = View3DWindow(self, show_window=False)
            img_view = capture_widget_temp(view.canvas, "view3d_")
            view.close()
            if img_view:
                images.append(img_view)
        except Exception:
            pass

        from ..models.utils import draw_beam_section_png
        import tempfile

        tmp = tempfile.NamedTemporaryFile(
            prefix="section_pdf_", suffix=".png", delete=False
        )
        tmp.close()
        section_img = draw_beam_section_png(b, h, r, de, db, tmp.name)

        title = title_text
        data = {
            "data_section": data_section,
            "calc_sections": calc_sections,
            "results": result_section,
            "images": images,
            "section_img": section_img,
            "verif_table": verif_table,
            # Valores clave para el reporte LaTeX
            "d": d,
            "b1": beta1,
            "pbal": p_bal,
            "pmax": p_max,
            "as_min": as_min,
            "as_max": as_max,
            # Fórmulas principales en formato LaTeX
            "formula_peralte": calc_sections[0][1][0].strip("$"),
            "formula_b1": calc_sections[1][1][0].strip("$"),
            "formula_pbal": calc_sections[2][1][0].strip("$"),
            "formula_pmax": calc_sections[3][1][0].strip("$"),
            "formula_asmin": calc_sections[4][1][0].strip("$"),
            "formula_asmax": calc_sections[5][1][0].strip("$"),
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

    def on_back(self):
        """Go back to the previous window."""
        if self.back_callback:
            self.back_callback()
        else:
            self.close()
            parent = self.parent()
            if parent:
                parent.show()
