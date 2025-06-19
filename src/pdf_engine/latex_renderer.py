import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict
from jinja2 import Environment, FileSystemLoader

TEMPLATE_NAME = "reporte_flexion.tex"

def render_report(title: str, data: Dict[str, Any], output_path: str = "reporte_diseño_flexion.pdf") -> str:
    """Renderiza una plantilla .tex y compila un PDF usando MiKTeX portátil."""

    base_dir = Path(__file__).resolve().parents[2]
    pdflatex_path = base_dir / "latex_runtime" / "texmfs" / "install" / "miktex" / "bin" / "x64" / "pdflatex.exe"

    if not pdflatex_path.exists() or not pdflatex_path.is_file():
        system_pdflatex = shutil.which("pdflatex")
        if system_pdflatex:
            pdflatex_path = Path(system_pdflatex)
        else:
            raise FileNotFoundError("No se encontró pdflatex. Instala LaTeX o colócalo en el PATH.")

    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
        autoescape=False,
    )
    template = env.get_template(TEMPLATE_NAME)
    context = dict(data)
    context.setdefault("formula_images", [])
    context["title"] = title.upper()

    for key in [
        "section_img", "peralte_img", "b1_img", "pbal_img",
        "rhobal_img", "pmax_img", "asmin_img", "asmax_img"
    ]:
        value = context.get(key)
        if value and isinstance(value, str) and value.strip():
            normalized = value.replace("\\", "/")
            context[key] = normalized
        else:
            context[key] = None

    debug_tex = base_dir / "debug_report.tex"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Copiar imagen y ajustar ruta antes de renderizar
        section_img_path = context.get("section_img")
        if section_img_path and os.path.isfile(section_img_path):
            destino_img = os.path.join(tmpdir, "section.png")
            shutil.copy(section_img_path, destino_img)
            context["section_img"] = "section.png"

            # 🔍 Verificación de imagen copiada
            print("### Verificando imagen copiada:")
            print("Ruta:", destino_img)
            print("Existe:", os.path.exists(destino_img))
            print("Tamaño:", os.path.getsize(destino_img), "bytes")

        # Renderizar .tex ya con ruta corregida
        tex_source = template.render(context)

        with open(debug_tex, "w", encoding="utf-8") as f_debug:
            f_debug.write(tex_source)

        tex_file = os.path.join(tmpdir, "report.tex")
        with open(tex_file, "w", encoding="utf-8") as fh:
            fh.write(tex_source)

        try:
            subprocess.run(
                [str(pdflatex_path), "-interaction=nonstopmode", tex_file],
                cwd=tmpdir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as exc:
            raise RuntimeError("La compilación del PDF falló. Revisa debug_report.tex.") from exc

        pdf_src = os.path.join(tmpdir, "report.pdf")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        shutil.move(pdf_src, output_path)

    return output_path
