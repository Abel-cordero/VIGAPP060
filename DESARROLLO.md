# Guía de Desarrollo

Este documento reúne pautas básicas para contribuir al proyecto y mantener una estructura de trabajo ordenada.

## Entorno de trabajo

1. Utiliza Python 3.8 o superior.
2. Crea un entorno virtual antes de instalar las dependencias:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

## Organización del código

- El archivo principal es `main.py`. Procura mantener cada función centrada en una tarea específica.
- Si añades módulos nuevos colócalos en la carpeta `src/vigapp/` y mantenla limpia.
- Documenta las funciones utilizando docstrings de una sola línea.

## Proceso de contribución

1. Crea una rama a partir de `main` para tus cambios locales.
2. Asegúrate de que el programa se ejecute sin errores antes de crear una solicitud de cambios.
3. Describe brevemente tu aporte en la sección correspondiente del `README`.

## Pruebas

Aún no se cuenta con un conjunto formal de pruebas automatizadas. Si añades pruebas, guárdalas en una carpeta `tests/` y procura que puedan ejecutarse con `pytest`.

## Extensión 3D

Para el módulo de visualización tridimensional consulta el archivo
[DESARROLLO_3D.md](DESARROLLO_3D.md), donde se describen las tecnologías
sugeridas y el flujo de trabajo preliminar.

