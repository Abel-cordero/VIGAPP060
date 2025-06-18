import os
import subprocess
import shutil
import tempfile
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

TEMPLATE_NAME = "reporte_flexion.tex"

def render_report(title: str, data: Dict[str, Any], output_path: str = "reporte_diseño_flexion.pdf") -> str:
    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
        autoescape=False,
    )
    template = env.get_template(TEMPLATE_NAME)
    context = dict(data)
    context.setdefault("formula_images", [])
    context["title"] = title.upper()
    tex_source = template.render(context)

    # 🧩 Ruta al pdflatex portable
    pdflatex_path = os.path.join(
        os.getcwd(), "latex_runtime", "miktex", "bin", "x64", "pdflatex.exe"
    )

    if not os.path.exists(pdflatex_path):
        raise FileNotFoundError("No se encontró pdflatex en latex_runtime. Verifica que MiKTeX portátil esté instalado correctamente.")

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_file = os.path.join(tmpdir, "report.tex")
        with open(tex_file, "w", encoding="utf-8") as fh:
            fh.write(tex_source)

        try:
            subprocess.run(
                [pdflatex_path, "-interaction=nonstopmode", tex_file],
                cwd=tmpdir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as exc:
            raise RuntimeError("La compilación del PDF falló. Revisa el contenido del .tex.") from exc

        pdf_src = os.path.join(tmpdir, "report.pdf")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        shutil.move(pdf_src, output_path)

    return output_path
