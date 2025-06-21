import os
import subprocess
import webbrowser
from typing import Any, Dict, List


def generar_reporte_html(
    datos: Dict[str, Any],
    resultados: Dict[str, Dict[str, Any]],
    tabla: List[List[str]] | None = None,
    imagenes: List[str] | None = None,
    seccion: str | None = None,
    calc_sections: List[Any] | None = None,
) -> None:
    """Genera un reporte HTML profesional usando MathJax y lo abre en el navegador."""
    os.makedirs("html_report", exist_ok=True)
    import shutil

    img_views: List[str] = []
    if imagenes:
        for i, path in enumerate(imagenes, 1):
            if os.path.isfile(path):
                dst = os.path.join("html_report", f"img_view{i}.png")
                shutil.copy(path, dst)
                img_views.append(os.path.basename(dst))

    section_rel = None
    if seccion and os.path.isfile(seccion):
        dst = os.path.join("html_report", "img_seccion_viga.png")
        shutil.copy(seccion, dst)
        section_rel = os.path.basename(dst)

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
        "<script>function toggleEdit(btn,id){var e=document.getElementById(id);if(!e)return;var ed=e.getAttribute('contenteditable')==='true';e.setAttribute('contenteditable', ed?'false':'true');btn.textContent=ed?'Editar':'Listo';}</script>",
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
            f"<img src='{section_rel or 'img_seccion_viga.png'}' class='imagen-centro' alt='Secci\u00f3n'>",
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

    html.append("<h2>CALCULOS</h2>")
    sec_id = 0
    for subt, key in orden:
        info = resultados.get(key, {})
        gen = info.get("general") or info.get("formula") or ""
        rep = info.get("reemplazo", "")
        res = info.get("resultado") or info.get("valor", "")
        if not (gen or rep or res):
            continue
        sec_id += 1
        hid = f"h{sec_id}"
        html.append(
            f"<h3 id='{hid}' contenteditable='false'>{subt} <button onclick=\"toggleEdit(this,'{hid}')\">Editar</button></h3>"
        )
        if gen:
            fid = f"f{sec_id}"
            html.append(
                f"<div id='{fid}' class='formula' contenteditable='false'>$$ {gen} $$ <button onclick=\"toggleEdit(this,'{fid}')\">Editar</button></div>"
            )
        if rep:
            rid = f"r{sec_id}"
            html.append(
                f"<div id='{rid}' class='reemplazo' contenteditable='false'>$$ {rep} $$ <button onclick=\"toggleEdit(this,'{rid}')\">Editar</button></div>"
            )
        if res:
            sid = f"s{sec_id}"
            html.append(
                f"<div id='{sid}' class='resultado' contenteditable='false'>$$ {res} $$ <button onclick=\"toggleEdit(this,'{sid}')\">Editar</button></div>"
            )

    if calc_sections:
        html.append("<h2>DESARROLLO AS REQUERIDO</h2>")
        for tit, formulas in calc_sections:
            sec_id += 1
            hid = f"h{sec_id}"
            html.append(
                f"<h3 id='{hid}' contenteditable='false'>{tit} <button onclick=\"toggleEdit(this,'{hid}')\">Editar</button></h3>"
            )
            for frm in formulas:
                sid = f"x{sec_id}_{formulas.index(frm)}"
                html.append(
                    f"<div id='{sid}' class='formula' contenteditable='false'>$$ {frm} $$ <button onclick=\"toggleEdit(this,'{sid}')\">Editar</button></div>"
                )

    if tabla or img_views:
        html.append("</div><div class='page'>")

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

    for img in img_views:
        html.append(f"<img src='{img}' class='imagen-centro' alt='Corte'>")

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
