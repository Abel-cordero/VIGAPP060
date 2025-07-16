import os
import webbrowser
from typing import Any, Dict


def generar_reporte_cortante_html(datos: Dict[str, Any], result: Any, imagen: str | None = None) -> str:
    """Generate a simple HTML report for shear design."""
    os.makedirs("html_report", exist_ok=True)

    img_rel = None
    if imagen and os.path.isfile(imagen):
        dst = os.path.join("html_report", os.path.basename(imagen))
        os.replace(imagen, dst)
        img_rel = os.path.basename(dst)

    html = [
        "<!DOCTYPE html>",
        "<html>",
        "<head><meta charset='utf-8'><title>Reporte Corte</title>",
        "<style>body{font-family:Arial;}table{border-collapse:collapse;}td,th{border:1px solid #000;padding:4px;}h1{text-align:left;}</style>",
        "</head><body>",
        "<h1>DISEÑO POR CORTE</h1>",
        "<h2>Datos</h2>",
        "<table>",
    ]

    for k, v in datos.items():
        html.append(f"<tr><td><b>{k}</b></td><td>{v}</td></tr>")
    html.append("</table>")

    html.extend([
        "<h2>Resultados</h2>",
        "<table>",
        f"<tr><td>Vc (T)</td><td>{result.Vc:.2f}</td></tr>",
        f"<tr><td>Vs (T)</td><td>{result.Vs:.2f}</td></tr>",
        f"<tr><td>ϕVc</td><td>{result.phi_Vc:.2f}</td></tr>",
        f"<tr><td>ϕ(Vc+Vs)</td><td>{result.phi_Vc_Vs:.2f}</td></tr>",
        f"<tr><td>Separación SC</td><td>{result.S_sc:.2f} cm</td></tr>",
        f"<tr><td>Separación SR</td><td>{result.S_sr:.2f} cm</td></tr>",
        f"<tr><td>Cumple</td><td>{'SI' if result.ok else 'NO'}</td></tr>",
        "</table>",
    ])

    if img_rel:
        html.append(f"<img src='{img_rel}' style='width:90%;display:block;margin:auto'>")

    html.append("</body></html>")

    path = os.path.join("html_report", "reporte_cortante.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(html))

    webbrowser.open(f"file://{os.path.abspath(path)}")
    return path

