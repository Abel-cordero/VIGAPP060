"""PDF generation utilities using ReportLab."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
import tempfile
from .models.utils import parse_formula, latex_to_png
import sympy as sp


def _formula_img(latex: str, max_width: float) -> Image:
    """Return a ReportLab Image with LaTeX rendered at small size."""
    tmp = tempfile.NamedTemporaryFile(prefix="form_", suffix=".png", delete=False)
    tmp.close()
    latex_to_png(latex, tmp.name, fontsize=7)
    img = Image(tmp.name)
    img.hAlign = "CENTER"
    if img.drawWidth > max_width:
        scale = max_width / img.drawWidth
        img.drawWidth *= scale
        img.drawHeight *= scale
    return img


def generate_memoria_pdf(title, data_section, calc_sections, result_section, path, images=None, section_img=None):
    """Create a calculation report as a PDF.

    Parameters
    ----------
    title : str
        Título del documento.
    data_section : list
        Tabla con los datos de entrada.
    calc_sections : list
        Pasos de cálculo descritos como listas de texto.
    result_section : list
        Resultados finales del diseño.
    path : str
        Ruta donde se guardará el PDF.
    images : list[str] | None
        Rutas de imágenes (fórmulas o capturas) a insertar en el reporte.
    section_img : str | None
        Ruta de la imagen de la sección a mostrar junto a la tabla de datos.
    """
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Titulo", fontName="Helvetica-Bold", fontSize=12, alignment=1))
    styles.add(ParagraphStyle(name="Seccion", fontName="Helvetica-Bold", fontSize=11))
    styles.add(ParagraphStyle(name="Sub", fontName="Helvetica", fontSize=10))
    styles.add(ParagraphStyle(name="Tabla", fontName="Helvetica", fontSize=11))
    doc = SimpleDocTemplate(path, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)

    story = [Paragraph(title, styles["Titulo"]), Spacer(1, 12)]

    if data_section:
        story.append(Paragraph("DATOS", styles["Seccion"]))
        table = Table(data_section, hAlign="LEFT", style=TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 11),
        ]))
        elems = [table]
        if section_img:
            img = Image(section_img)
            img.hAlign = "CENTER"
            max_w = doc.width * 0.45
            if img.drawWidth > max_w:
                scale = max_w / img.drawWidth
                img.drawWidth *= scale
                img.drawHeight *= scale
            elems.append(img)
            data_table = Table([[elems[0], elems[1]]], colWidths=[doc.width*0.55, doc.width*0.45])
            data_table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP")]))
            story.append(data_table)
        else:
            story.append(table)
        story.append(Spacer(1, 12))

    if calc_sections:
        story.append(Paragraph("CÁLCULOS", styles["Seccion"]))
        for subtitle, steps in calc_sections:
            story.append(Paragraph(subtitle, styles["Sub"]))
            for step in steps:
                if isinstance(step, str) and step.startswith("$") and step.endswith("$"):
                    story.append(_formula_img(step.strip("$"), doc.width * 0.7))
                else:
                    eq = parse_formula(step)
                    if eq is not None:
                        story.append(_formula_img(sp.latex(eq), doc.width * 0.7))
                    else:
                        story.append(Paragraph(step, styles["Sub"]))
            story.append(Spacer(1, 6))

    if result_section:
        story.append(Paragraph("Resultados", styles["Seccion"]))
        for text, value in result_section:
            story.append(Paragraph(f"{text}: {value}", styles["Normal"]))

    if images:
        for img_path in images:
            story.append(Spacer(1, 12))
            img = Image(img_path)
            img.hAlign = "CENTER"
            max_w = doc.width
            if img.drawWidth > max_w:
                scale = max_w / img.drawWidth
                img.drawWidth *= scale
                img.drawHeight *= scale
            story.append(img)
            story.append(Spacer(1, 12))

    doc.build(story)
    return path
