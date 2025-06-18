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

    # Ruta base segura al proyecto (sube 2 niveles desde /pdf_engine/)
    base_dir = Path(__file__).resolve().parents[2]
    pdflatex_path = base_dir / "latex_runtime" / "texmfs" / "install" / "miktex" / "bin" / "x64" / "pdflatex.exe"

    if not pdflatex_path.exists():
        raise FileNotFoundError("No se encontró pdflatex en latex_runtime. Verifica que MiKTeX portátil esté instalado correctamente.")

    # Preparar entorno Jinja2
    env = Environment(
        loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
        autoescape=False,
    )
    template = env.get_template(TEMPLATE_NAME)
    context = dict(data)
    context.setdefault("formula_images", [])
    context["title"] = title.upper()

    # Validar rutas de imágenes: eliminar las vacías o inválidas, y estandarizar separadores
    for key in [
        "section_img", "peralte_img", "b1_img", "pbal_img",
        "rhobal_img", "pmax_img", "asmin_img", "asmax_img"
    ]:
        value = context.get(key)
        if not value or not value.strip():
            context[key] = None
        else:
            context[key] = value.replace("\\", "/")

    # Renderizar .tex
    tex_source = template.render(context)

    # Guardar .tex generado para depuración
    debug_tex = base_dir / "debug_report.tex"
    with open(debug_tex, "w", encoding="utf-8") as f_debug:
        f_debug.write(tex_source)

    # Compilar con pdflatex portátil en carpeta temporal
    with tempfile.TemporaryDirectory() as tmpdir:
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
            raise RuntimeError("La compilación del PDF falló. Revisa el contenido del archivo debug_report.tex.") from exc

        # Mover el PDF generado al destino final
        pdf_src = os.path.join(tmpdir, "report.pdf")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        shutil.move(pdf_src, output_path)

    return output_path
