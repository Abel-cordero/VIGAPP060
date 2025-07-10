# VIGAPP060

Aplicaci\u00f3n de escritorio para el c\u00e1lculo y dise\u00f1o de vigas de concreto armado seg\u00fan la Norma T\u00e9cnica Peruana E.060. Utiliza PyQt5 para la interfaz y permite generar reportes profesionales en HTML y PDF.

## Caracter\u00edsticas principales

- Correcci\u00f3n autom\u00e1tica de momentos (Dual 1 y Dual 2).
- Diagramas de momentos originales y corregidos con Matplotlib.
- C\u00e1lculo del refuerzo requerido y verificaci\u00f3n de l\u00edmites.
- Vista de secciones en 3D con reordenamiento de varillas y exportaci\u00f3n a DXF.
- Generaci\u00f3n de reportes HTML interactivos y PDF mediante LaTeX (`pdflatex`).
- Captura de gr\u00e1ficos y f\u00f3rmulas al portapapeles o a archivos.
- Sistema de activaci\u00f3n con c\u00f3digo de licencia local.

## Instalaci\u00f3n

Se recomienda usar un entorno virtual. Instala las dependencias b\u00e1sicas:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Para generar PDFs es necesario tener `pdflatex` en el sistema. En Windows se puede utilizar [MiKTeX](https://miktex.org/).

## Ejecuci\u00f3n

Desde la ra\u00edz del repositorio:

```bash
python main.py
```

Al iniciarse por primera vez se solicitar\u00e1 una clave de activaci\u00f3n. Esta se genera con los scripts de la carpeta `scripts/`.

## Flujos de trabajo

1. **Ingreso de momentos**: la ventana principal (`MomentApp`) permite ingresar los seis valores de momento y elegir el sistema estructural. Los diagramas se actualizan autom\u00e1ticamente.
2. **Dise\u00f1o de acero**: la ventana `DesignWindow` calcula las \u00e1reas de refuerzo, muestra los cortes M1, M2 y M3 y permite seleccionar di\u00e1metros y n\u00famero de varillas.
3. **Desarrollo de refuerzo**: `View3DWindow` ofrece una vista simplificada de las secciones. Se pueden mover las varillas y exportar el detalle a DXF.
4. **Reportes**: mediante `reporte_flexion_html.py` y `pdf_engine/` se generan reportes HTML editables y PDF a partir de una plantilla LaTeX.

## Estructura del proyecto

- `vigapp/` – paquete principal con la interfaz y la l\u00f3gica de c\u00e1lculo.
  - `ui/` – ventanas Qt (momentos, dise\u00f1o, vista 3D, f\u00f3rmulas, men\u00fa).
  - `graphics/` – utilidades de dibujo y exportaci\u00f3n.
  - `pdf_engine/` – motor LaTeX para generar el reporte en PDF.
  - `activation/` – gesti\u00f3n de licencias y verificaci\u00f3n.
  - `models/` – constantes y funciones auxiliares.
- `scripts/` – herramientas para generar licencias.
- `tests/` – pruebas unitarias con PyTest.

## Pruebas

Ejecuta las pruebas con:

```bash
pytest
```

## Licencia

Este proyecto se distribuye bajo los t\u00e9rminos de la [Licencia MIT](LICENSE).
