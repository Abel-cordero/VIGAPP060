import os
import subprocess
import webbrowser
from typing import Dict, Any

def generar_reporte_html(datos: Dict[str, Any], resultados: Dict[str, Dict[str, Any]]) -> None:
    """Genera un archivo HTML mostrando el diseño a flexión con fórmulas MathJax."""
    os.makedirs("html_report", exist_ok=True)
    def _get_num(key: str):
        """Return a numeric value if possible."""
        val = datos.get(key)
        try:
            val_f = float(val)
            return int(val_f) if val_f.is_integer() else val_f
        except Exception:
            return val

    b = _get_num("b") or _get_num("b (cm)")
    h = _get_num("h") or _get_num("h (cm)")

    def _format_val(value: Any) -> str:
        try:
            num = float(value)
            if num.is_integer():
                return str(int(num))
            return f"{num:g}"
        except Exception:
            return str(value)

    titulo = f"DISE\u00d1O A FLEXI\u00d3N DE VIGA {_format_val(b)}x{_format_val(h)}"

    html = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>Diseño a Flexión de Viga</title>",
        "<script src='https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'></script>",
        "<style>",
        "body{font-family:Arial,sans-serif;background:#fff;margin:20px auto;max-width:800px;}",
        "h1{text-align:center;}",
        "h2,h3{text-align:left;}",
        "table{border-collapse:collapse;margin:auto;width:100%;text-align:left;}",
        "td,th{border:1px solid #000;padding:2px 4px;}",
        "button{display:block;margin:20px auto;}",
        "img{display:block;margin:auto;max-width:90%;}",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>{titulo}</h1>",
        "<h2>DATOS</h2>",
        "<table>"
    ]
    header_map = {
        "alto": "h (cm)",
        "alto (cm)": "h (cm)",
        "base": "b (cm)",
        "ancho": "b (cm)",
        "fy": "fy (kg/cm²)",
        "fc": "f'c (kg/cm²)",
        "phi": "φ",
        "de": "ϕ estribo (cm)",
        "db": "ϕ varilla (cm)",
    }

    for k, v in datos.items():
        k = header_map.get(k, k)
        html.append(f"<tr><td><b>{k}</b></td><td>{_format_val(v)}</td></tr>")
    html.append("</table>")

    html.append("<h2>CÁLCULOS</h2>")

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
        html.append(f"<h3>{titulo_sec}</h3>")
        if formula:
            html.append(f"<div style='text-align:left'>$$ {formula} $$</div>")
        if valor != "":
            html.append(f"<div><b>Resultado:</b> {valor}</div>")

    html.append("<button onclick=\"window.print()\">Exportar a PDF</button>")
    html.append("</body></html>")

    path = os.path.join("html_report", "reporte_flexion.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(html))
    print(f"Reporte guardado en {path}")

    abs_path = os.path.abspath(path)
    try:
        subprocess.run(["start", "chrome", abs_path], shell=True)
    except Exception:
        webbrowser.open(f"file://{abs_path}")
