import os
import sys
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from reporte_flexion_html import generar_reporte_html


def test_generar_reporte_html_renders_data(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("subprocess.run", lambda *args, **kwargs: None)
    monkeypatch.setattr("webbrowser.open", lambda *args, **kwargs: None)

    datos = {"b": 30, "h": 50}
    resultados = {"peralte": {"general": "d=b-h", "resultado": "d=20"}}

    generar_reporte_html(datos, resultados)

    path = Path("html_report") / "reporte_flexion.html"
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "DISEÑO A FLEXIÓN DE VIGA 30x50" in content
    assert "d=b-h" in content
    assert "d=20" in content
