"""PDF generation utilities using ReportLab."""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Preformatted,
    Image,
)


def generate_memoria_pdf(title, data_section, calc_sections, result_section, path, images=None):
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
    """
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(path, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=40, bottomMargin=40)

    story = [Paragraph(title, styles["Title"]), Spacer(1, 12)]

    if data_section:
        story.append(Paragraph("Datos del proyecto", styles["Heading2"]))
        table = Table(data_section, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

    if calc_sections:
        story.append(Paragraph("Cálculos", styles["Heading2"]))
        for subtitle, steps in calc_sections:
            story.append(Paragraph(subtitle, styles["Heading3"]))
            for step in steps:
                story.append(Preformatted(step, styles["Code"]))
            story.append(Spacer(1, 6))

    if result_section:
        story.append(Paragraph("Resultados", styles["Heading2"]))
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
