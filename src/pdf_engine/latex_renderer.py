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

    def _extract_from_data_section(label: str):
        for row in context.get("data_section", []):
            if isinstance(row, (list, tuple)) and row and str(row[0]).startswith(label):
                return row[1]
        return None

    def _format_num(val: Any, unit: str, *, mpa=False) -> str:
        try:
            num = float(val)
        except (TypeError, ValueError):
            return str(val)
        if mpa and num < 100:  # value given in MPa -> convert
            num *= 10.1972
        return f"{num:.2f} {unit}"

    # Map of desired context keys and their labels/units
    fix_map = {
        "base": ("b (cm)", "cm", False),
        "altura": ("h (cm)", "cm", False),
        "recubrimiento": ("r (cm)", "cm", False),
        "diam_estribo": ("ϕ estribo (cm)", "cm", False),
        "diam_varilla": ("ϕ varilla (cm)", "cm", False),
        "fc": ("f'c", "kgf/cm²", True),
        "fy": ("fy", "kgf/cm²", True),
    }

    for key, (label, unit, is_fc) in fix_map.items():
        val = context.get(key)
        if val is None:
            val = _extract_from_data_section(label)
        if val is not None:
            context[key] = _format_num(val, unit, mpa=is_fc)

    if "d" in context:
        context["d"] = _format_num(context["d"], "cm", False)

    for a_key in ("as_min", "as_max"):
        if a_key in context:
            context[a_key] = _format_num(context[a_key], "cm²", False)

    def _replace_units(text: str) -> str:
        return (text.replace("MPa", "kgf/cm²")
                    .replace("m^2", "cm^2")
                    .replace("m^{2}", "cm^{2}"))

    for key in [
        "formula_peralte", "formula_b1", "formula_pbal", "formula_rhobal",
        "formula_pmax", "formula_asmin", "formula_asmax",
    ]:
        if key in context and isinstance(context[key], str):
            context[key] = _replace_units(context[key])

    if "calc_sections" in context:
        new_sections = []
        for subtitle, steps in context["calc_sections"]:
            new_steps = [
                _replace_units(step) if isinstance(step, str) else step
                for step in steps
            ]
            new_sections.append((subtitle, new_steps))
        context["calc_sections"] = new_sections

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
