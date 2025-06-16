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
)


def generate_memoria_pdf(title, data_section, calc_sections, result_section, path):
    """Create a calculation report as a PDF."""
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

    doc.build(story)
    return path
