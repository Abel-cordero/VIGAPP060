"""Widget creation helpers for DesignWindow."""
from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QLayout,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import os


def build_ui(win) -> None:
    """Populate ``win`` with all widgets."""
    content = QWidget()
    layout = QGridLayout(content)
    layout.setVerticalSpacing(3)
    layout.setSizeConstraint(QLayout.SetMinimumSize)
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setWidget(content)
    win.setCentralWidget(scroll)
    win.scroll_area = scroll

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
    win.row_font = QFont()
    win.row_font.setPointSize(8)

    win.edits = {}
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
        win.edits[text] = ed

    estribo_opts = ["8mm", '3/8"', '1/2"']
    lbl_estribo = QLabel("ϕ estribo")
    lbl_estribo.setFont(small_font)
    layout.addWidget(lbl_estribo, len(labels), 0)
    win.cb_estribo = QComboBox()
    win.cb_estribo.setFont(small_font)
    win.cb_estribo.addItems(estribo_opts)
    win.cb_estribo.setCurrentText('3/8"')
    layout.addWidget(win.cb_estribo, len(labels), 1)

    varilla_opts = ['1/2"', '5/8"', '3/4"', '1"']
    lbl_varilla = QLabel("ϕ varilla")
    lbl_varilla.setFont(small_font)
    layout.addWidget(lbl_varilla, len(labels) + 1, 0)
    win.cb_varilla = QComboBox()
    win.cb_varilla.setFont(small_font)
    win.cb_varilla.addItems(varilla_opts)
    win.cb_varilla.setCurrentText('5/8"')
    layout.addWidget(win.cb_varilla, len(labels) + 1, 1)

    lbl_capas = QLabel("N\u00b0 capas")
    lbl_capas.setFont(small_font)
    layout.addWidget(lbl_capas, len(labels) + 2, 0)
    win.layer_combo = QComboBox()
    win.layer_combo.setFont(small_font)
    win.layer_combo.addItems(["1", "2", "3", "4"])
    layout.addWidget(win.layer_combo, len(labels) + 2, 1)

    pos_labels = ["M1-", "M2-", "M3-", "M1+", "M2+", "M3+"]
    win.rebar_rows = [[] for _ in range(6)]
    win.rows_layouts = []

    win.combo_grid = QGridLayout()

    for i, label in enumerate(pos_labels):
        row = 0 if i < 3 else 1
        col = i % 3
        cell = QVBoxLayout()
        cell.addWidget(QLabel(label), alignment=Qt.AlignCenter)
        header = QGridLayout()
        lbl_qty = QLabel("cant.")
        lbl_qty.setFont(win.row_font)
        lbl_qty.setAlignment(Qt.AlignCenter)
        header.addWidget(lbl_qty, 0, 0)
        lbl_dia = QLabel("\u00f8")
        lbl_dia.setFont(win.row_font)
        lbl_dia.setAlignment(Qt.AlignCenter)
        header.addWidget(lbl_dia, 0, 1)
        lbl_ncapas = QLabel("capa")
        lbl_ncapas.setFont(win.row_font)
        lbl_ncapas.setAlignment(Qt.AlignCenter)
        header.addWidget(lbl_ncapas, 0, 2)
        lbl_capas = QLabel("capas")
        lbl_capas.setFont(win.row_font)
        lbl_capas.setAlignment(Qt.AlignCenter)
        header.addWidget(lbl_capas, 0, 3, 1, 2)
        cell.addLayout(header)
        rows_layout = QVBoxLayout()
        cell.addLayout(rows_layout)
        win.rows_layouts.append(rows_layout)
        win.combo_grid.addLayout(cell, row, col)
        win._add_rebar_row(i)

    row_start = len(labels) + 3
    info_layout = QHBoxLayout()
    info_layout.setSpacing(5)
    info_layout.setContentsMargins(0, 0, 0, 0)
    lbl_as_min = QLabel("As min (cm²):")
    lbl_as_min.setFont(small_font)
    win.as_min_label = QLabel("0.00")
    win.as_min_label.setFont(small_font)
    info_layout.addWidget(lbl_as_min)
    info_layout.addWidget(win.as_min_label)
    lbl_as_max = QLabel("As max (cm²):")
    lbl_as_max.setFont(small_font)
    win.as_max_label = QLabel("0.00")
    win.as_max_label.setFont(small_font)
    info_layout.addWidget(lbl_as_max)
    info_layout.addWidget(win.as_max_label)
    lbl_base_req = QLabel("Base req. (cm):")
    lbl_base_req.setFont(small_font)
    win.base_req_label = QLabel("-")
    win.base_req_label.setFont(small_font)
    info_layout.addWidget(lbl_base_req)
    info_layout.addWidget(win.base_req_label)
    win.base_msg_label = QLabel("")
    win.base_msg_label.setFont(small_font)
    info_layout.addWidget(win.base_msg_label)
    layout.addLayout(info_layout, row_start, 2, 1, 6)

    win.fig_sec, win.ax_sec = plt.subplots(figsize=(3, 3), constrained_layout=True)
    win.canvas_sec = FigureCanvas(win.fig_sec)
    layout.addWidget(win.canvas_sec, 0, 2, len(labels) + 3, 4)

    win.fig_dist, (win.ax_req, win.ax_des) = plt.subplots(2, 1, figsize=(5, 6), constrained_layout=True)
    win.canvas_dist = FigureCanvas(win.fig_dist)
    layout.addWidget(win.canvas_dist, row_start + 1, 0, 1, 8)

    layout.addLayout(win.combo_grid, row_start + 2, 0, 1, 8)

    icon_path = os.path.join(os.path.dirname(__file__), "..", "..", "icon", "botones", "captura", "capture.png")
    win.btn_capture = QPushButton()
    win.btn_capture.setIcon(QIcon(icon_path))
    win.btn_capture.setFixedWidth(30)
    win.btn_memoria = QPushButton("Reportes")
    win.btn_view3d = QPushButton("Secciones")
    win.btn_menu = QPushButton("Menú")
    win.btn_back = QPushButton("Atrás")
    win.btn_back.setFixedWidth(80)
    layout.addWidget(win.btn_capture, row_start + 3, 0, 1, 1)
    layout.addWidget(win.btn_memoria, row_start + 3, 1, 1, 2)
    layout.addWidget(win.btn_view3d, row_start + 3, 3, 1, 2)
    layout.addWidget(win.btn_menu, row_start + 3, 5, 1, 2)
    layout.addWidget(win.btn_back, row_start + 3, 7, 1, 1)

