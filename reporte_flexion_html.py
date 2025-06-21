import os
from typing import Dict, Any

def generar_reporte_html(datos: Dict[str, Any], resultados: Dict[str, Dict[str, Any]]) -> None:
    """Genera un archivo HTML mostrando el diseño a flexión con fórmulas MathJax."""
    os.makedirs("html_report", exist_ok=True)
    b = datos.get("b")
    h = datos.get("h")
    titulo = f"DISE\u00d1O A FLEXI\u00d3N DE VIGA {b}x{h}"

    html = [
        "<!DOCTYPE html>",
        "<html><head>",
        "<meta charset='utf-8'>",
        "<script src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'></script>",
        "<style>body{font-family:Arial,sans-serif;margin:20px;}h1{text-align:center;}table{border-collapse:collapse;margin:auto;}td,th{border:1px solid #000;padding:4px;}h2{margin-top:1.2em;}</style>",
        "</head><body>",
        f"<h1>{titulo}</h1>",
        "<h2>DATOS</h2>",
        "<table>"
    ]
    for k, v in datos.items():
        html.append(f"<tr><td><b>{k}</b></td><td>{v}</td></tr>")
    html.append("</table>")

    orden = [
        ("Peralte", "peralte"),
        ("B1", "b1"),
        ("Pbal", "pbal"),
        ("Pmax", "pmax"),
        ("As min", "as_min"),
        ("As max", "as_max"),
    ]
    for titulo_sec, key in orden:
        info = resultados.get(key, {})
        formula = info.get("formula", "")
        valor = info.get("valor", "")
        html.append(f"<h2>{titulo_sec}</h2>")
        if formula:
            html.append(f"<p>$$ {formula} $$</p>")
        if valor != "":
            html.append(f"<p><b>Resultado:</b> {valor}</p>")

    html.append("</body></html>")

    path = os.path.join("html_report", "reporte_flexion.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(html))
    print(f"Reporte guardado en {path}")
