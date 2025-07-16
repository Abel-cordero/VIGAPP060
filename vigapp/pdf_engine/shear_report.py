from __future__ import annotations

import os
from typing import Any, Dict

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image


def generate_shear_pdf(data: Dict[str, Any], result: Any, fig_path: str, output_path: str) -> str:
    """Generate a simple shear design PDF report."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    flow = [Paragraph("DISE\u00d1O POR CORTE", styles["Heading1"])]

    # Input table
    table_data = [["Par\u00e1metro", "Valor"]]
    for k, v in data.items():
        table_data.append([k, str(v)])
    tbl = Table(table_data, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
    ]))
    flow.extend([tbl, Spacer(1, 0.5 * cm)])

    # Result table
    res_data = [
        ["Vc (T)", f"{result.Vc:.2f}"],
        ["\u03c6Vc (T)", f"{result.phi_Vc:.2f}"],
        ["\u03c6(Vc+Vs) (T)", f"{result.phi_Vc_Vs:.2f}"],
        ["Cumple", "SI" if result.ok else "NO"],
    ]
    tbl2 = Table(res_data, hAlign="LEFT")
    tbl2.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
    flow.extend([tbl2, Spacer(1, 0.5 * cm)])

    if os.path.isfile(fig_path):
        flow.append(Image(fig_path, width=14 * cm, height=6 * cm))

    doc.build(flow)
    return output_path
