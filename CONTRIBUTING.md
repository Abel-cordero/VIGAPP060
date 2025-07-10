# Contribuir al Proyecto

Este repositorio utiliza **pytest** para las pruebas automatizadas. Para poder ejecutarlas debes contar con las siguientes bibliotecas instaladas:

- PyQt5
- numpy
- matplotlib
- scipy
- mplcursors
- pyqtgraph
- sympy
- python-docx
- reportlab
- Jinja2
- ezdxf
- pytest

Puedes instalar todas las dependencias de desarrollo con:

```bash
pip install -r requirements-dev.txt
```

En entornos sin interfaz gráfica (por ejemplo, servidores de integración continua) establece `QT_QPA_PLATFORM=offscreen` para que Qt no requiera pantalla:

```bash
QT_QPA_PLATFORM=offscreen pytest
```

Consulta `DESARROLLO.md` para más detalles de configuración y estilo de código.
