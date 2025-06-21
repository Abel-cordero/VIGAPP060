import os
import subprocess
import webbrowser
from typing import Any, Dict, List


def generar_reporte_html(
    datos: Dict[str, Any],
    resultados: Dict[str, Dict[str, Any]],
    tabla: List[List[str]] | None = None,
) -> None:
    """Genera un reporte HTML profesional usando MathJax y lo abre en el navegador."""
    os.makedirs("html_report", exist_ok=True)

    def _fmt(v: Any) -> str:
        try:
            num = float(v)
            return str(int(num)) if num.is_integer() else f"{num:g}"
        except Exception:
            return str(v)

    b = datos.get("b") or datos.get("b (cm)")
    h = datos.get("h") or datos.get("h (cm)")
    titulo = f"DISE\u00d1O A FLEXI\u00d3N DE VIGA {_fmt(b)}x{_fmt(h)}"

    html = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>Reporte</title>",
        "<script src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'></script>",
        "<style>",
        "body {\n  font-family: Arial, sans-serif;\n  background: #f0f0f0;\n  margin: 0;\n  padding: 0;\n}",
        ".page {\n  width: 21cm;\n  min-height: 29.7cm;\n  padding: 2.5cm 3cm;\n  margin: 1cm auto;\n  background: white;\n  box-shadow: 0 0 5px rgba(0,0,0,0.1);\n}",
        "h1, h2, h3 { text-align: left; margin-top: 1.5em; }",
        "table { border-collapse: collapse; width: 100%; margin-bottom: 1em; }",
        "td, th { border: 1px solid #000; padding: 5px 8px; }",
        ".formula, .reemplazo, .resultado { margin-left: 20px; font-size: 15px; }",
        ".imagen-centro { display: block; margin: 20px auto; max-width: 100%; }",
        "@media print { button { display: none; } body { background: white; } }",
        "</style>",
        "</head>",
        "<body>",
        "<div style='position:fixed; top:20px; right:20px;'><button onclick=\"window.print()\">Exportar a PDF</button></div>",
        "<div class='page'>",
        f"<h1 contenteditable='true'>{titulo}</h1>",
        "<div style='display:flex; gap:20px;'>",
        "<div style='flex:1;'>",
        "<table>",
    ]

    for k, v in datos.items():
        html.append(f"<tr><td><b>{k}</b></td><td>{_fmt(v)}</td></tr>")
    html.extend(
        [
            "</table>",
            "</div>",
            "<div style='flex:1; text-align:center;'>",
            "<img src='img_seccion_viga.png' class='imagen-centro' alt='Secci\u00f3n'>",
            "</div>",
            "</div>",
        ]
    )

    orden = [
        ("C\u00e1lculo de Peralte (ART.1.1 E060)", "peralte"),
        ("C\u00e1lculo de B1 (ART.1.1 E060)", "b1"),
        ("C\u00e1lculo de Pbal (ART.1.1 E060)", "pbal"),
        ("C\u00e1lculo de Pmax (ART.1.1 E060)", "pmax"),
        ("C\u00e1lculo de As m\u00edn (ART.1.1 E060)", "as_min"),
        ("C\u00e1lculo de As m\u00e1x (ART.1.1 E060)", "as_max"),
    ]

    html.append("<h2>C\u00c1LCULOS</h2>")
    for subt, key in orden:
        info = resultados.get(key, {})
        gen = info.get("general") or info.get("formula") or ""
        rep = info.get("reemplazo", "")
        res = info.get("resultado") or info.get("valor", "")
        if not (gen or rep or res):
            continue
        html.append(f"<h3>{subt}</h3>")
        if gen:
            html.append(f"<div class='formula'>$$ {gen} $$</div>")
        if rep:
            html.append(f"<div class='reemplazo'>$$ {rep} $$</div>")
        if res:
            html.append(f"<div class='resultado'>$$ {res} $$</div>")

    if tabla:
        html.append("<h2>Resumen de Verificaci\u00f3n</h2>")
        html.append("<table>")
        html.append(
            "<tr><th>Secci\u00f3n</th><th>As requerido</th><th>As dise\u00f1ado</th><th>Estado</th></tr>"
        )
        for sec, req, dis, est in tabla:
            html.append(
                f"<tr><td>{sec}</td><td>{req}</td><td>{dis}</td><td>{est}</td></tr>"
            )
        html.append("</table>")

    html.append("<img src='img_acero_m123.png' class='imagen-centro' alt='Acero'>")
    html.append("</div>")
    html.append("</body></html>")

    path = os.path.join("html_report", "reporte_flexion.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(html))

    abs_path = os.path.abspath(path)
    try:
        subprocess.run(["start", "chrome", abs_path], shell=True)
    except Exception:
        webbrowser.open(f"file://{abs_path}")
