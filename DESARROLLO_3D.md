# Desarrollo de Interfaz 3D

Este documento bosqueja los pasos preliminares para integrar una vista en tres dimensiones al proyecto.

## Objetivo

Ofrecer una representación interactiva de la viga y su refuerzo. Permitirá inspeccionar distribuciones de acero y realizar ajustes visuales antes de regresar al flujo normal de cálculo.

## Tecnologías sugeridas

- **PyOpenGL** o **PyQtGraph** para renderizar geometría sencilla.
- Alternativamente se puede enlazar con **Blender** mediante su API de Python para escenas más complejas.
- Se evaluará mantener la compatibilidad con PyQt5.

## Flujo propuesto

1. Desde la ventana principal se accede a la vista 3D mediante un botón opcional.
2. Se genera un modelo sencillo de la viga utilizando los datos de sección.
3. El usuario puede arrastrar barras, cambiar diámetros y observar interferencias.
4. Al confirmar los cambios, se actualizan los valores en la interfaz de diseño convencional.

Este archivo servirá como referencia inicial para futuras iteraciones.
