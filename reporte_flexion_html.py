import os
import subprocess
import webbrowser
from typing import Any, Dict

def generar_reporte_html(datos: Dict[str, Any], resultados: Dict[str, Dict[str, Any]]) -> None:
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
        "body{font-family:Arial,sans-serif;margin:20px auto;max-width:900px;}",
        "h1{text-align:center;}",
        "h2,h3{text-align:left;}",
        "table{border-collapse:collapse;width:100%;margin-bottom:20px;}",
        "td,th{border:1px solid #999;padding:4px 8px;}",
        ".formula{margin-left:20px;margin-top:4px;}",
        ".reemplazo{margin-left:20px;color:#555;margin-top:2px;}",
        ".resultado{margin-left:20px;font-weight:bold;margin-top:2px;}",
        "button{display:block;margin:20px auto;}",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>{titulo}</h1>",
        "<h2>DATOS</h2>",
        "<table>",
    ]

    for k, v in datos.items():
        html.append(f"<tr><td><b>{k}</b></td><td>{_fmt(v)}</td></tr>")
    html.append("</table>")

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

    html.append("<button onclick=\"window.print()\">Exportar a PDF</button>")
    html.append("</body></html>")

    path = os.path.join("html_report", "reporte_flexion.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(html))

    abs_path = os.path.abspath(path)
    try:
        subprocess.run(["start", "chrome", abs_path], shell=True)
    except Exception:
        webbrowser.open(f"file://{abs_path}")
