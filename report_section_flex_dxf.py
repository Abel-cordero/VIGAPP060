"""Simple DXF generator for beam section cuts.

This module contains ``exportar_cortes_a_dxf`` which receives a list of
sections with bar coordinates and writes a DXF drawing similar to a
basic AutoCAD output.
"""

from __future__ import annotations

from typing import Iterable, Dict, List, Tuple

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
    if isinstance(color, int):
        return int(color)
    return _COLOR_MAP.get(str(color).lower(), 7)


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
        - ``as_min``: As mínimo de diseño
        - ``as_req_neg`` y ``as_req_pos``: As requerido en cm²
    """
    doc = ezdxf.new()
    msp = doc.modelspace()

    secciones = list(secciones)
    if not secciones:
        doc.saveas(filename)
        return

    sep = 10.0
    legend: List[float] = []

    for idx, sec in enumerate(secciones):
        b = float(sec.get("b", 0))
        h = float(sec.get("h", 0))
        r = float(sec.get("r", 0))
        de = float(sec.get("estribo_diam", 0))
        bars = sec.get("bars", [])
        offx = idx * (b + sep)

        # Contorno
        msp.add_lwpolyline(
            [
                (offx, 0),
                (offx + b, 0),
                (offx + b, h),
                (offx, h),
                (offx, 0),
            ],
            dxfattribs={"color": 5},
        )

        # Estribo
        inner = r + de
        msp.add_lwpolyline(
            [
                (offx + inner, inner),
                (offx + b - inner, inner),
                (offx + b - inner, h - inner),
                (offx + inner, h - inner),
                (offx + inner, inner),
            ],
            dxfattribs={"color": 6},
        )

        for bar in bars:
            x = offx + float(bar.get("x", 0))
            y = float(bar.get("y", 0))
            d = float(bar.get("diam", 0))
            msp.add_circle((x, y), d / 2, dxfattribs={"color": 5})
            txt = msp.add_text(f"\u2300{bar.get('label', d)}", dxfattribs={"height": 2.5})
            txt.dxf.insert = (x + d, y)
            txt.dxf.halign = 0
            txt.dxf.valign = 1
            if d not in legend:
                legend.append(d)

        # Nombre del corte
        txt = msp.add_text(sec.get("nombre", ""), dxfattribs={"height": 4})
        txt.dxf.insert = (offx + b / 2, h + 8)
        txt.dxf.halign = 1
        txt.dxf.valign = 2

        # Dimensiones
        _draw_dimension(msp, (offx, 0), (offx + b, 0), -4, f"{b} cm")
        _draw_dimension(msp, (offx, 0), (offx, h), -4, f"{h} cm", vertical=True)

    # Leyenda de diámetros
    if legend:
        base_x = 0.0
        y = -12.0
        for i, d in enumerate(sorted(legend)):
            x = base_x + i * 20.0
            msp.add_circle((x, y), d / 2, dxfattribs={"color": 5})
            t = msp.add_text(f"\u2300{d}", dxfattribs={"height": 2.5})
            t.dxf.insert = (x + d, y)
            t.dxf.halign = 0
            t.dxf.valign = 1

    title = secciones[0].get("viga", "SECCION DE VIGA")
    t = msp.add_text(title, dxfattribs={"height": 5})
    t.dxf.insert = (0, -20)
    t.dxf.halign = 0
    t.dxf.valign = 1

    doc.saveas(filename)

