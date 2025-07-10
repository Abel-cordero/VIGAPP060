"""Helper functions for drawing and exporting sections."""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

import ezdxf
from ezdxf.enums import TextEntityAlignment
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from ..models.constants import DIAM_CM

# Clearance (cm) so bars do not overlap stirrups
CLEARANCE = 0.2


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def distribute_x(diams: List[float], b: float, r: float, de: float) -> List[float]:
    """Return X coordinates ensuring bars stay inside stirrups."""
    n = len(diams)
    if n == 1:
        return [b / 2]

    left = r + de + diams[0] / 2 + CLEARANCE
    right = b - (r + de) - diams[-1] / 2 - CLEARANCE
    if n == 2:
        return [left, right]

    width = right - left
    spacing = width / (n - 1)
    return [left + i * spacing for i in range(n)]


def layer_positions_bottom(layers: Dict[int, List[Tuple[float, str]]], r: float, de: float, offset: float = 0.0) -> Dict[int, float]:
    """Return Y positions of each layer from the bottom."""
    positions: Dict[int, float] = {}
    base = r + de + CLEARANCE + offset
    prev_d = 0.0
    for layer in sorted(layers):
        diam_layer = max(d for d, _ in layers[layer])
        base += prev_d + (2.5 if layer > 1 else 0)
        positions[layer] = base + diam_layer / 2
        prev_d = diam_layer
    return positions


def layer_positions_top(layers: Dict[int, List[Tuple[float, str]]], r: float, de: float, h: float, offset: float = 0.0) -> Dict[int, float]:
    """Return Y positions of each layer from the top."""
    positions: Dict[int, float] = {}
    base = h - (r + de + CLEARANCE + offset)
    prev_d = 0.0
    for layer in sorted(layers):
        diam_layer = max(d for d, _ in layers[layer])
        base -= prev_d + (2.5 if layer > 1 else 0)
        positions[layer] = base - diam_layer / 2
        prev_d = diam_layer
    return positions


def bars_summary(layers: Dict[int, List[Tuple[float, str]]]) -> str:
    """Return a short text description of bars in all layers."""
    counts: Dict[str, int] = {}
    for bars in layers.values():
        for _, key in bars:
            counts[key] = counts.get(key, 0) + 1
    parts = [f"{n}\u00f8{key}" for key, n in counts.items()]
    return " + ".join(parts)


# ---------------------------------------------------------------------------
# DXF export helpers
# ---------------------------------------------------------------------------

_COLOR_MAP = {
    "red": 1,
    "yellow": 2,
    "green": 3,
    "cyan": 4,
    "blue": 5,
    "magenta": 6,
    "white": 7,
}

# Common text heights
TITLE_HT = 2.0
SUBTITLE_HT = 1.5
SMALL_HT = 1.0


def _color_index(color: str | int) -> int:
    """Return a valid DXF color index for ``color``."""
    if isinstance(color, int):
        return int(color)
    return _COLOR_MAP.get(str(color).lower(), 7)


_COLOR_ORDER = ["red", "blue", "yellow"]
DIAM_COLOR = {key: _COLOR_ORDER[i % len(_COLOR_ORDER)] for i, key in enumerate(DIAM_CM.keys())}
DIAM_COLOR_IDX = {k: _color_index(c) for k, c in DIAM_COLOR.items()}
_COLOR_NAME_ES = {
    "red": "Rojo",
    "yellow": "Amarillo",
    "green": "Verde",
    "cyan": "Cian",
    "blue": "Azul",
    "magenta": "Magenta",
    "white": "Blanco",
}


def _bars_summary_export(bars: Iterable[Dict], face: str | None = None) -> str:
    """Return a short description of bars grouped by diameter."""
    counts: Dict[str, int] = {}
    for bar in bars:
        if face is not None and bar.get("face") != face:
            continue
        key = bar.get("label")
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    parts = [f"{n} \u00F8{key}" for key, n in counts.items()]
    return " + ".join(parts)


def dibujar_varillas(msp: ezdxf.layouts.Modelspace, bars: Iterable[Dict], offx: float = 0.0, legend: List[str] | None = None) -> None:
    """Draw bars as coloured circles with solid fill."""
    for bar in bars:
        x = offx + float(bar.get("x", 0))
        y = float(bar.get("y", 0))
        label = bar.get("label", "")
        d = float(bar.get("diam", 0))
        color = DIAM_COLOR_IDX.get(label, 7)
        msp.add_circle((x, y), d / 2, dxfattribs={"color": color})
        hatch = msp.add_hatch(color=color)
        path = hatch.paths.add_edge_path()
        path.add_arc((x, y), d / 2, 0, 360)
        if legend is not None and label and label not in legend:
            legend.append(label)


def agregar_cotas(msp: ezdxf.layouts.Modelspace, offx: float, b: float, h: float) -> None:
    """Add basic horizontal and vertical dimensions."""
    _draw_dimension(msp, (offx, 0), (offx + b, 0), -5, f"b = {b:.1f} cm")
    _draw_dimension(msp, (offx, 0), (offx, h), -5, f"h = {h:.1f} cm", vertical=True)


def _draw_legend_table(msp: ezdxf.layouts.Modelspace, labels: List[str], base_y: float) -> None:
    """Draw a simple colour legend table."""
    if not labels:
        return
    row_h = 3.0
    width = 40.0
    top_y = base_y + row_h / 2
    bottom_y = base_y - row_h * (len(labels) + 0.5)
    msp.add_line((0, top_y), (width, top_y), dxfattribs={"color": 7})
    for i, key in enumerate(labels):
        y = base_y - row_h * (i + 1)
        color = DIAM_COLOR_IDX.get(key, 7)
        name = _COLOR_NAME_ES.get(DIAM_COLOR.get(key, ""), DIAM_COLOR.get(key, "").capitalize())
        msp.add_text(
            "\u25CF",
            dxfattribs={"height": SMALL_HT, "style": "Arial", "color": color},
        ).set_placement((1, y), align=TextEntityAlignment.MIDDLE_LEFT)
        msp.add_text(
            f"{name} \u00F8{key}",
            dxfattribs={"height": SMALL_HT, "style": "Arial"},
        ).set_placement((4, y), align=TextEntityAlignment.MIDDLE_LEFT)
    msp.add_line((0, bottom_y), (width, bottom_y), dxfattribs={"color": 7})


def _draw_dimension(
    msp: ezdxf.layouts.Modelspace,
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    offset: float,
    text: str,
    *,
    vertical: bool = False,
) -> None:
    """Place dimension text without guide or arrow lines."""
    if vertical:
        text_pos = ((p1[0] + p2[0]) / 2 + offset, (p1[1] + p2[1]) / 2)
        attribs = {"height": SMALL_HT, "style": "Arial", "rotation": 90}
    else:
        text_pos = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + offset)
        attribs = {"height": SMALL_HT, "style": "Arial"}

    txt = msp.add_text(text, dxfattribs=attribs)
    txt.set_placement(text_pos, align=TextEntityAlignment.MIDDLE_CENTER)


def exportar_cortes_a_dxf(secciones: Iterable[Dict], filename: str) -> None:
    """Create a DXF file with the given sections."""
    doc = ezdxf.new()
    doc.styles.new("Arial", dxfattribs={"font": "arial.ttf"})
    msp = doc.modelspace()

    secciones = list(secciones)
    if not secciones:
        doc.saveas(filename)
        return

    sep = 20.0
    legend: List[str] = []
    offset_x = 0.0

    for sec in secciones:
        b = float(sec.get("b", 0))
        h = float(sec.get("h", 0))
        r = float(sec.get("r", 0))
        de = float(sec.get("estribo_diam", 0))
        bars = sec.get("bars", [])
        nombre = sec.get("nombre", "")

        msp.add_lwpolyline(
            [
                (offset_x, 0),
                (offset_x + b, 0),
                (offset_x + b, h),
                (offset_x, h),
                (offset_x, 0),
            ],
            dxfattribs={"color": 5},
        )

        inner = r + de
        msp.add_lwpolyline(
            [
                (offset_x + inner, inner),
                (offset_x + b - inner, inner),
                (offset_x + b - inner, h - inner),
                (offset_x + inner, h - inner),
                (offset_x + inner, inner),
            ],
            dxfattribs={"color": 6},
        )

        dibujar_varillas(msp, bars, offset_x, legend)
        agregar_cotas(msp, offset_x, b, h)

        desc_neg = _bars_summary_export(bars, "neg")
        desc_pos = _bars_summary_export(bars, "pos")

        txt_neg = msp.add_text(
            f"{nombre}- ({desc_neg})",
            dxfattribs={"height": SUBTITLE_HT, "style": "Arial"},
        )
        txt_neg.set_placement(
            (offset_x + b / 2, h + 2), align=TextEntityAlignment.MIDDLE_CENTER
        )

        txt_pos = msp.add_text(
            f"{nombre}+ ({desc_pos})",
            dxfattribs={"height": SUBTITLE_HT, "style": "Arial"},
        )
        txt_pos.set_placement(
            (offset_x + b / 2, -2), align=TextEntityAlignment.MIDDLE_CENTER
        )

        offset_x += b + sep

    if legend:
        _draw_legend_table(msp, legend, -12.0)

    total_width = offset_x - sep
    max_h = max(float(sec.get("h", 0)) for sec in secciones)
    b0 = secciones[0].get("b", 0)
    h0 = secciones[0].get("h", 0)
    title = f"SECCION DE VIGA {int(b0)}x{int(h0)}"
    t = msp.add_text(title, dxfattribs={"height": TITLE_HT, "style": "Arial"})
    t.set_placement((total_width / 2, max_h + 10), align=TextEntityAlignment.TOP_CENTER)

    doc.saveas(filename)


def exportar_cad(view) -> None:
    """Collect data from a :class:`View3DWindow` and export a DXF file."""
    try:
        b = float(view.design.edits["b (cm)"].text())
        h = float(view.design.edits["h (cm)"].text())
        r = float(view.design.edits["r (cm)"].text())
    except Exception:
        QMessageBox.warning(view, "Exportar CAD", "Datos de secci\u00f3n inv\u00e1lidos")
        return

    path, _ = QFileDialog.getSaveFileName(
        view,
        "Guardar DXF",
        "",
        "Archivos DXF (*.dxf)",
    )
    if not path:
        return
    if not path.lower().endswith(".dxf"):
        path += ".dxf"

    de = DIAM_CM.get(view.design.cb_estribo.currentText(), 0)
    as_n, as_p = view.design._required_areas()
    as_min = getattr(view.design, "as_min", 0)

    neg_layers = [view._collect_bars(i) for i in range(3)]
    pos_layers = [view._collect_bars(i + 3) for i in range(3)]

    if not view.neg_orders:
        view.neg_orders = [view._collect_order(i) for i in range(3)]
    if not view.pos_orders:
        view.pos_orders = [view._collect_order(i + 3) for i in range(3)]

    titles = ["M1", "M2", "M3"]
    lista = []

    for idx in range(3):
        bars: List[Dict] = []
        pos = pos_layers[idx]
        neg = neg_layers[idx]

        pos_counts = [len(pos.get(l, [])) for l in sorted(pos)]
        neg_counts = [len(neg.get(l, [])) for l in sorted(neg)]

        pos_y = layer_positions_bottom(pos, r, de)
        neg_y = layer_positions_top(neg, r, de, h)

        start = 0
        orders = view.pos_orders[idx]
        for layer in sorted(pos):
            keys = orders[start:start + pos_counts.pop(0)] or [k for _, k in pos[layer]]
            diams = [DIAM_CM.get(k, 0) for k in keys]
            xs = distribute_x(diams, b, r, de)
            y = pos_y.get(layer, r + de)
            for x, k in zip(xs, keys):
                d = DIAM_CM.get(k, 0)
                bars.append({"x": x, "y": y, "diam": d, "label": k, "face": "pos"})
            start += len(keys)

        start = 0
        orders = view.neg_orders[idx]
        for layer in sorted(neg):
            keys = orders[start:start + neg_counts.pop(0)] or [k for _, k in neg[layer]]
            diams = [DIAM_CM.get(k, 0) for k in keys]
            xs = distribute_x(diams, b, r, de)
            y = neg_y.get(layer, h - (r + de))
            for x, k in zip(xs, keys):
                d = DIAM_CM.get(k, 0)
                bars.append({"x": x, "y": y, "diam": d, "label": k, "face": "neg"})
            start += len(keys)

        sec = {
            "nombre": titles[idx],
            "b": b,
            "h": h,
            "r": r,
            "estribo_diam": de,
            "bars": bars,
            "as_min": as_min,
            "as_req_neg": as_n[idx],
            "as_req_pos": as_p[idx],
            "viga": view.title_edit.text().upper(),
        }
        lista.append(sec)

    try:
        exportar_cortes_a_dxf(lista, path)
        QMessageBox.information(view, "Exportar CAD", f"Archivo guardado: {path}")
    except Exception as exc:
        QMessageBox.warning(view, "Exportar CAD", f"No se pudo guardar el DXF: {exc}")

