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
        ".norma { font-size: 0.8em; color: #555; }",
        "table { border-collapse: collapse; width: 280px; margin-bottom: 1em; }",
        "td, th { border: 1px solid #000; padding: 5px 8px; }",
        ".formula, .reemplazo, .resultado { margin-left: 20px; font-size: 15px; }",
        ".imagen-centro { display: block; margin: 20px auto; max-width: 100%; }",
        "@media print { button { display: none; } body { background: white; } }",
        "</style>",
        "<script>function toggleEdit(btn,id){var e=document.getElementById(id);if(!e)return;var ed=e.getAttribute('contenteditable')==='true';e.setAttribute('contenteditable', ed?'false':'true');btn.textContent=ed?'Editar':'Listo';}",
        "function exportWord(){var html=document.documentElement.outerHTML;var blob=new Blob(['\ufeff',html],{type:'application/msword'});var url=URL.createObjectURL(blob);var a=document.createElement('a');a.href=url;a.download='reporte.doc';a.click();URL.revokeObjectURL(url);}</script>",
        "</head>",
        "<body>",
        "<div style='position:fixed; top:20px; right:20px;'><button onclick=\"window.print()\">Exportar a PDF</button> <button onclick=\"exportWord()\">Exportar a Word</button></div>",
        "<div class='page'>",
        f"<h1 contenteditable='true'>{titulo}</h1>",
        "<div style='display:flex; align-items:stretch; gap:20px; height:auto; min-height:270px;'>",
        "<div style='flex:1; display:flex; align-items:center;'>",
        "<table style='margin: 0;'>",
    ]

    for k, v in datos.items():
        html.append(f"<tr><td><b>{k}</b></td><td>{_fmt(v)}</td></tr>")
    html.extend(
        [
            "</table>",
            "</div>",
            "<div style='flex:1; text-align:center; display:flex; align-items:center; justify-content:center;'>",
            f'<img src="{section_rel or "img_seccion_viga.png"}" style="height:350px; width:auto; object-fit:contain; display:block; margin:auto;" alt="Sección">',
            "</div>",
            "</div>",
        ]
    )

    orden = [
        ("Cal. de Peralte <span class='norma'>(E060 Art. 17.5.2)</span>", "peralte"),
        ("Cal. de \u00df1 <span class='norma'>(E060 Art. 10.2.7.3)</span>", "b1"),
        ("C\u03c1<sub>bal</sub> <span class='norma'>(E060 Art. 10.3.32)</span>", "pbal"),
        ("C\u03c1<sub>max</sub> <span class='norma'>(E060 Art. 10.3.4)</span>", "pmax"),
        ("Cal. de As m\u00edn <span class='norma'>(E060 Art. 10.5.2)</span>", "as_min"),
        ("Cal. de As m\u00e1x <span class='norma'>(E060 Art. 10.3.4)</span>", "as_max"),
    ]

    html.append("<h2>CALUCLOS</h2>")
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
        as_min = float(resultados.get("as_min", {}).get("valor", 0))  # Asegúrate de tenerlo definido

        for sec, req, dis, est in tabla:
            try:
                req_val = float(req)
            except (ValueError, TypeError):
                req_val = 0

            # Si As requerido es menor que As mínimo, usar As mínimo
            req_mostrar = max(req_val, as_min)
            req_fmt = f"{req_mostrar:.2f}"

            html.append(
                f"<tr><td>{sec}</td><td>{req_fmt}</td><td>{dis}</td><td>{est}</td></tr>"
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
