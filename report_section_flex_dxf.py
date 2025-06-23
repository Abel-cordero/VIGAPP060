"""DXF export of beam sections for the flexure report.

This module is independent from any GUI framework and only depends on
``ezdxf``. It provides a single function ``exportar_a_dxf`` used to
generate a DXF file containing one or more beam sections aligned
horizontally.
"""

from __future__ import annotations

from typing import Iterable, Tuple, Dict

import ezdxf

# Basic mapping of color names to AutoCAD color indexes
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
    """Return a DXF color index for ``color``."""
    if isinstance(color, int):
        return int(color)
    return _COLOR_MAP.get(str(color).lower(), 7)


def exportar_a_dxf(lista_de_secciones: Iterable[Dict], filename: str) -> None:
    """Exporta las secciones de viga en ``lista_de_secciones`` a ``filename``.

    Cada sección debe ser un diccionario con al menos los campos
    ``nombre``, ``b``, ``h`` y ``diam``. Las listas ``varillas_sup`` y
    ``varillas_inf`` contienen pares ``(x, y)`` con las posiciones de las
    varillas en centímetros.
    """
    doc = ezdxf.new()
    msp = doc.modelspace()

    if not lista_de_secciones:
        doc.saveas(filename)
        return

    max_b = max(sec.get("b", 0) for sec in lista_de_secciones)
    spacing = 20.0  # espacio entre secciones en cm

    legend_entries: set[Tuple[float, str | int]] = set()

    for idx, sec in enumerate(lista_de_secciones):
        b = float(sec.get("b", 0))
        h = float(sec.get("h", 0))
        nombre = sec.get("nombre", f"S{idx + 1}")
        diam = float(sec.get("diam", 0))
        color = sec.get("color", 7)
        var_sup = sec.get("varillas_sup", [])
        var_inf = sec.get("varillas_inf", [])

        offx = idx * (max_b + spacing)

        # Contorno externo de la viga
        msp.add_lwpolyline(
            [
                (offx, 0),
                (offx + b, 0),
                (offx + b, h),
                (offx, h),
                (offx, 0),
            ],
            dxfattribs={"color": 7},
        )

        # Estribo interno con un offset sencillo relacionado al diámetro
        off = diam + 2
        msp.add_lwpolyline(
            [
                (offx + off, off),
                (offx + b - off, off),
                (offx + b - off, h - off),
                (offx + off, h - off),
                (offx + off, off),
            ],
            dxfattribs={"color": 1},
        )

        # Dibujo de varillas superiores e inferiores
        for x, y in list(var_sup) + list(var_inf):
            msp.add_circle(
                (offx + float(x), float(y)),
                diam / 2,
                dxfattribs={"color": _color_index(color)},
            )
            legend_entries.add((diam, color))

        # Nombre de la sección centrado sobre la viga
        txt = msp.add_text(nombre, dxfattribs={"height": 5})
        txt.dxf.insert = (offx + b / 2, h + 10)
        txt.dxf.halign = 1  # CENTER
        txt.dxf.valign = 2  # TOP

    # Leyenda de colores y diámetros
    if legend_entries:
        y_leg = -10.0
        x_start = 0.0
        sep = 25.0
        for i, (d, col) in enumerate(sorted(legend_entries)):
            x = x_start + i * sep
            msp.add_circle((x, y_leg), d / 2, dxfattribs={"color": _color_index(col)})
            t = msp.add_text(f"\u2300{d:g} {col}", dxfattribs={"height": 3})
            t.dxf.insert = (x + d, y_leg)
            t.dxf.halign = 0  # LEFT
            t.dxf.valign = 1  # MIDDLE

    doc.saveas(filename)
