import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

TEMPLATE_NAME = "reporte_flexion.tex"


def render_report(title: str, data: Dict[str, Any], output_path: str = "reporte_dise\xf1o_flexion.pdf") -> str:
    """Render a LaTeX template and compile it to a PDF.

    Parameters
    ----------
    title: str
        Document title.
    data: dict
        Dictionary with keys like ``data_section`` or ``calc_sections``.
    output_path: str
        Destination path for the generated PDF.

    Returns
    -------
    str
        Path to the generated PDF file.
    """
    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
        autoescape=False,
    )
    template = env.get_template(TEMPLATE_NAME)
    context = dict(data)
    context.setdefault("formula_images", [])
    context["title"] = title.upper()
    tex_source = template.render(context)

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = os.path.join(tmpdir, "report.tex")
        with open(tex_file, "w", encoding="utf-8") as fh:
            fh.write(tex_source)

        try:
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file],
                cwd=tmpdir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as exc:  # pragma: no cover - pdflatex might not be present during tests
            raise RuntimeError("pdflatex execution failed") from exc

        pdf_src = os.path.join(tmpdir, "report.pdf")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        shutil.move(pdf_src, output_path)
    return output_path
