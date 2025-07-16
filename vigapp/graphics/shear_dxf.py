from __future__ import annotations

from typing import Iterable

from .utilities import _require_ezdxf

try:  # pragma: no cover
    import ezdxf  # type: ignore
except Exception:  # pragma: no cover
    ezdxf = None


def _structure_points(ln: float, h: float, beam_type: str) -> list[tuple[float, float]]:
    support_w = 0.5
    column_h = 2.0
    y0 = 0.0
    if beam_type == "volado":
        return [
            (-support_w, y0 - column_h),
            (0, y0 - column_h),
            (0, y0),
            (ln, y0),
            (ln, y0 + h),
            (0, y0 + h),
            (-support_w, y0 + h),
        ]
    return [
        (-support_w, y0 - column_h),
        (0, y0 - column_h),
        (0, y0),
        (ln, y0),
        (ln, y0 - column_h),
        (ln + support_w, y0 - column_h),
        (ln + support_w, y0 + h),
        (ln, y0 + h),
        (0, y0 + h),
        (-support_w, y0 + h),
    ]


def export_shear_dxf(filename: str, Vu: float, ln: float, d: float, h: float, beam_type: str) -> None:
    """Export shear scheme to a DXF file."""
    _require_ezdxf()
    doc = ezdxf.new()
    msp = doc.modelspace()

    for name, color in {
        "Estructura": 7,
        "Cargas": 1,
        "Diagrama": 5,
        "Texto": 7,
        "Cotas": 7,
    }.items():
        if name not in doc.layers:
            doc.layers.new(name, dxfattribs={"color": color})

    pts = _structure_points(ln, h, beam_type)
    msp.add_lwpolyline(pts, dxfattribs={"layer": "Estructura", "closed": True})

    if beam_type == "volado":
        msp.add_line((0, h), (ln, 0), dxfattribs={"layer": "Diagrama"})
        x = d
        msp.add_line((x, h), (x, h - d), dxfattribs={"layer": "Cargas"})
        msp.add_text("Vu", dxfattribs={"height": 0.2, "layer": "Texto"}).set_placement((x, h + 0.2))
    else:
        msp.add_line((0, 0), (ln, h), dxfattribs={"layer": "Diagrama"})
        for x in (d, ln - d):
            msp.add_line((x, h), (x, h - d), dxfattribs={"layer": "Cargas"})
            msp.add_text("Vu", dxfattribs={"height": 0.2, "layer": "Texto"}).set_placement((x, h + 0.2))

    doc.saveas(filename)
