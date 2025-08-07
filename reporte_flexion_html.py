import os
import subprocess
import webbrowser
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader


def generar_reporte_html(
    datos: Dict[str, Any],
    resultados: Dict[str, Dict[str, Any]],
    tabla: List[List[str]] | None = None,
    imagenes: List[str] | None = None,
    seccion: str | None = None,
    calc_sections: List[Any] | None = None,
) -> None:
    """Genera un reporte HTML profesional usando una plantilla Jinja2."""
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

    datos_items = []
    for k, v in datos.items():
        label = "h" if k in ("h (cm)", "Altura (h)", "Alto", "ALTO") else k
        datos_items.append({"label": label, "value": _fmt(v)})

    orden = [
        ("Calculo de Peralte <span class='norma'>(E060 Art. 17.5.2)</span>", "peralte"),
        ("Calculo de β1 <span class='norma'>(E060 Art. 10.2.7.3)</span>", "b1"),
        ("\u03c1<sub>bal</sub> <span class='norma'>(E060 Art. 10.3.32)</span>", "pbal"),
        ("\u03c1<sub>max</sub> <span class='norma'>(E060 Art. 10.3.4)</span>", "pmax"),
        ("Calculo de As m\u00edn <span class='norma'>(E060 Art. 10.5.2)</span>", "as_min"),
        ("Calculo de As m\u00e1x <span class='norma'>(E060 Art. 10.3.4)</span>", "as_max"),
    ]

    blocks: List[Dict[str, Any]] = []
    sec_id = 0
    for subt, key in orden:
        info = resultados.get(key, {})
        gen = info.get("general") or info.get("formula") or ""
        rep = info.get("reemplazo", "")
        res = info.get("resultado") or info.get("valor", "")
        if not (gen or rep or res):
            continue
        sec_id += 1
        block: Dict[str, Any] = {"hid": f"h{sec_id}", "subt": subt}
        if gen:
            block["fid"] = f"f{sec_id}"
            block["gen"] = gen
        if rep:
            block["rid"] = f"r{sec_id}"
            block["rep"] = rep
        if res:
            block["sid"] = f"s{sec_id}"
            block["res"] = res
        blocks.append(block)

    calc_blocks: List[Dict[str, Any]] = []
    if calc_sections:
        for tit, formulas in calc_sections:
            sec_id += 1
            cblock = {"hid": f"h{sec_id}", "title": tit, "formulas": []}
            for idx, frm in enumerate(formulas):
                cblock["formulas"].append({"id": f"x{sec_id}_{idx}", "expr": frm})
            calc_blocks.append(cblock)

    tabla_rows: List[Dict[str, str]] = []
    if tabla:
        as_min = float(resultados.get("as_min", {}).get("valor", 0))
        for sec, req, dis, est in tabla:
            try:
                req_val = float(req)
            except (ValueError, TypeError):
                req_val = 0
            req_mostrar = max(req_val, as_min)
            tabla_rows.append(
                {"sec": sec, "req": f"{req_mostrar:.2f}", "dis": dis, "est": est}
            )

    context = {
        "titulo": titulo,
        "datos": datos_items,
        "section_rel": section_rel,
        "blocks": blocks,
        "calc_sections": calc_blocks,
        "tabla": tabla_rows,
        "img_views": img_views,
    }

    template_dir = os.path.join(os.path.dirname(__file__), "vigapp", "html_templates")
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=True)
    template = env.get_template("reporte_flexion.html.j2")
    html_content = template.render(context)

    path = os.path.join("html_report", "reporte_flexion.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html_content)

    abs_path = os.path.abspath(path)
    try:
        subprocess.run(["start", "chrome", abs_path], shell=True)
    except Exception:
        webbrowser.open(f"file://{abs_path}")
