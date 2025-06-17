import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader

_LATEX_ESCAPE_MAP = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}


def _tex_escape(value: Any) -> str:
    """Escape LaTeX special characters in ``value``."""
    if value is None:
        return ""
    text = str(value)
    return "".join(_LATEX_ESCAPE_MAP.get(c, c) for c in text)


def _existing(path: str | None) -> str | None:
    """Return ``path`` only if it exists."""
    if path and os.path.exists(path):
        return path
    return None



TEMPLATE_NAME = "reporte_flexion.tex"
FIGURE_FILES = {
    "peralte_img": "peralte.png",
    "b1_img": "b1.png",
    "pbal_img": "pbal.png",
    "rhobal_img": "rhobal.png",
    "pmax_img": "pmax.png",
    "asmin_img": "asmin.png",
    "asmax_img": "asmax.png",
}

DEFAULT_FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "resources", "flexion", "figures")


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
    env.filters["escape"] = _tex_escape
    template = env.get_template(TEMPLATE_NAME)
    context = dict(data)
    context.setdefault("formula_images", [])
    context["title"] = title.upper()
    # Validate image paths to prevent LaTeX compilation errors
    context["images"] = [p for p in context.get("images", []) if _existing(p)]
    context["formula_images"] = [p for p in context.get("formula_images", []) if _existing(p)]
    context["section_img"] = _existing(context.get("section_img"))
    for key, fname in FIGURE_FILES.items():
        context[key] = _existing(
            context.get(key) or os.path.join(DEFAULT_FIG_DIR, fname)
        )
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
        except FileNotFoundError as exc:  # pragma: no cover - pdflatex not installed
            raise RuntimeError(
                "pdflatex executable not found. Please ensure LaTeX is installed and in PATH."
            ) from exc
        except subprocess.CalledProcessError as exc:  # pragma: no cover - LaTeX error
            output = (exc.stdout or b"") + (exc.stderr or b"")
            output = output.decode(errors="ignore")
            raise RuntimeError(f"pdflatex execution failed:\n{output}") from exc

        pdf_src = os.path.join(tmpdir, "report.pdf")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        shutil.move(pdf_src, output_path)
    return output_path
