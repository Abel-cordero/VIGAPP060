"""Simple DXF generator for beam section cuts.

This module contains ``exportar_cortes_a_dxf`` which receives a list of
sections with bar coordinates and writes a DXF drawing similar to a
basic AutoCAD output.
"""

from __future__ import annotations

from typing import Iterable, Dict, List, Tuple

from PyQt5.QtWidgets import QFileDialog, QMessageBox
from vigapp.models.constants import DIAM_CM

import ezdxf


_COLOR_MAP = {
    "red": 1,
    "yellow": 2,
    "green": 3,
    "cyan": 4,
    "blue": 5,
    "magenta": 6,
    "white": 7,
}


def _color_index(color: str | int) -> int:
    """Return a valid DXF color index for ``color``."""
    if isinstance(color, int):
        return int(color)
    return _COLOR_MAP.get(str(color).lower(), 7)


# Mapping of bar diameter keys to primary colors (red, blue, yellow)
_COLOR_ORDER = ["red", "blue", "yellow"]
DIAM_COLOR = {
    key: _COLOR_ORDER[i % len(_COLOR_ORDER)]
    for i, key in enumerate(DIAM_CM.keys())
}
DIAM_COLOR_IDX = {k: _color_index(c) for k, c in DIAM_COLOR.items()}


def _bars_summary(bars: Iterable[Dict]) -> str:
    """Return a short description of bars grouped by diameter."""
    counts: Dict[str, int] = {}
    for bar in bars:
        key = bar.get("label")
        if not key:
            continue
        counts[key] = counts.get(key, 0) + 1
    parts = [f"{n}\u2300{key}" for key, n in counts.items()]
    return " + ".join(parts)


def dibujar_varillas(msp: ezdxf.layouts.Modelspace, bars: Iterable[Dict], offx: float = 0.0,
                     legend: List[str] | None = None) -> None:
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
    """Add basic horizontal and vertical dimensions with arrows."""
    _draw_dimension(msp, (offx, 0), (offx + b, 0), -4, f"b = {b} cm")
    _draw_dimension(msp, (offx, 0), (offx, h), -4, f"h = {h} cm", vertical=True)


def _draw_dimension(
    msp: ezdxf.layouts.Modelspace,
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    offset: float,
    text: str,
    *,
    vertical: bool = False,
) -> None:
    """Draw a very small dimension line with arrows and centred text."""
    if vertical:
        dx, dy = 0, offset
        text_pos = ((p1[0] + p2[0]) / 2 + offset, (p1[1] + p2[1]) / 2)
    else:
        dx, dy = offset, 0
        text_pos = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + offset)

    msp.add_line((p1[0], p1[1]), (p1[0] + dx, p1[1] + dy), dxfattribs={"color": 7})
    msp.add_line((p2[0], p2[1]), (p2[0] + dx, p2[1] + dy), dxfattribs={"color": 7})
    a1 = (p1[0] + dx, p1[1] + dy)
    a2 = (p2[0] + dx, p2[1] + dy)
    msp.add_line(a1, a2, dxfattribs={"color": 7})
    size = 1.5
    if vertical:
        for y in [a1[1], a2[1]]:
            x = a1[0]
            msp.add_line((x, y), (x - size, y + size), dxfattribs={"color": 7})
            msp.add_line((x, y), (x + size, y + size), dxfattribs={"color": 7})
    else:
        for x in [a1[0], a2[0]]:
            y = a1[1]
            msp.add_line((x, y), (x - size, y - size), dxfattribs={"color": 7})
            msp.add_line((x, y), (x - size, y + size), dxfattribs={"color": 7})
    txt = msp.add_text(text, dxfattribs={"height": 2.5})
    txt.dxf.insert = text_pos
    txt.dxf.halign = 1
    txt.dxf.valign = 1


def exportar_cortes_a_dxf(secciones: Iterable[Dict], filename: str) -> None:
    """Create a DXF file with the given sections.

    Each element of ``secciones`` should contain:
        - ``nombre``: etiqueta del corte
        - ``b`` y ``h``: dimensiones de la viga en cm
        - ``r``: recubrimiento
        - ``estribo_diam``: diámetro del estribo en cm
        - ``bars``: lista de dicts ``{"x", "y", "diam", "label"}``
    """
    doc = ezdxf.new()
    msp = doc.modelspace()

    secciones = list(secciones)
    if not secciones:
        doc.saveas(filename)
        return

    sep = 20.0
    legend: List[str] = []
    offset_x = 0.0

    for idx, sec in enumerate(secciones):
        b = float(sec.get("b", 0))
        h = float(sec.get("h", 0))
        r = float(sec.get("r", 0))
        de = float(sec.get("estribo_diam", 0))
        bars = sec.get("bars", [])
        nombre = sec.get("nombre", "")

        # Geometry
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

        desc = _bars_summary(bars)
        txt = msp.add_text(f"{nombre} - ({desc})", dxfattribs={"height": 4})
        txt.dxf.insert = (offset_x + b / 2, h + 8)
        txt.dxf.halign = 1
        txt.dxf.valign = 2

        offset_x += b + sep

    if legend:
        base_x = 0.0
        y = -12.0
        for i, key in enumerate(legend):
            d = DIAM_CM.get(key, 0)
            color = DIAM_COLOR_IDX.get(key, 7)
            x = base_x + i * 20.0
            msp.add_circle((x, y), d / 2, dxfattribs={"color": color})
            hatch = msp.add_hatch(color=color)
            path = hatch.paths.add_edge_path()
            path.add_arc((x, y), d / 2, 0, 360)
            t = msp.add_text(f"\u2300{key}", dxfattribs={"height": 2.5})
            t.dxf.insert = (x + d, y)
            t.dxf.halign = 0
            t.dxf.valign = 1

    total_width = offset_x - sep
    max_h = max(float(sec.get("h", 0)) for sec in secciones)
    title = secciones[0].get("viga", "SECCION DE VIGA")
    t = msp.add_text(title, dxfattribs={"height": 5})
    t.dxf.insert = (total_width / 2, max_h + 20)
    t.dxf.halign = 1
    t.dxf.valign = 2

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
        bars = []
        pos = pos_layers[idx]
        neg = neg_layers[idx]

        pos_counts = [len(pos.get(l, [])) for l in sorted(pos)]
        neg_counts = [len(neg.get(l, [])) for l in sorted(neg)]

        pos_y = view._layer_positions_bottom(pos, r, de)
        neg_y = view._layer_positions_top(neg, r, de, h)

        start = 0
        orders = view.pos_orders[idx]
        for layer in sorted(pos):
            keys = orders[start:start + pos_counts.pop(0)] or [k for _, k in pos[layer]]
            diams = [DIAM_CM.get(k, 0) for k in keys]
            xs = view._distribute_x(diams, b, r, de)
            y = pos_y.get(layer, r + de)
            for x, k in zip(xs, keys):
                d = DIAM_CM.get(k, 0)
                bars.append({"x": x, "y": y, "diam": d, "label": k})
            start += len(keys)

        start = 0
        orders = view.neg_orders[idx]
        for layer in sorted(neg):
            keys = orders[start:start + neg_counts.pop(0)] or [k for _, k in neg[layer]]
            diams = [DIAM_CM.get(k, 0) for k in keys]
            xs = view._distribute_x(diams, b, r, de)
            y = neg_y.get(layer, h - (r + de))
            for x, k in zip(xs, keys):
                d = DIAM_CM.get(k, 0)
                bars.append({"x": x, "y": y, "diam": d, "label": k})
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

