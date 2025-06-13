# Diseño de Vigas NTP E.060

Esta aplicación implementa una interfaz gráfica para el cálculo y diseño de refuerzos en vigas de concreto armado siguiendo la Norma Técnica Peruana E.060.

Para más detalles de configuración revisa [DESARROLLO.md](DESARROLLO.md).

# Alcance:

INSTRUCCIÓN PARA GENERAR UNA APLICACIÓN EN PYTHON – DISEÑO DE VIGAS SEGÚN NTP E.060 (PERÚ)
## Objetivo del proyecto

Crear una aplicación completa en Python con interfaz gráfica que permita:

Ingresar momentos flectores en 3 secciones de una viga (6 valores: + y − en cada punto)

Generar y mostrar diagramas de momentos originales y corregidos


Aplicar corrección de momentos automáticamente según el tipo de sistema estructural (dual 1 o 2), según Norma Técnica Peruana E.060

## Corrección de momentos

Las reglas de la NTP E.060 se aplican de forma automática a los seis valores ingresados:

- Para **Dual 2 y pórticos** el momento positivo en cada cara del nudo no puede ser menor que la mitad del momento negativo proporcionado en esa misma cara.
- En **Dual 1** dicha relación mínima es un tercio.
- Además, en cualquier sección de la viga los momentos positivos y negativos no pueden ser menores que la cuarta parte del mayor momento existente en las caras.


Pasar a una segunda ventana donde se haga el diseño de refuerzo:

Mostrar refuerzo requerido (superior)

Mostrar refuerzo diseñado (inferior)

Permitir manipular número y diámetro de varillas (hasta 2 tipos diferentes)

Verificar cumplimiento estructural según la norma

Exportar resultados en formato visual, incluyendo opción de captura automática para Word

ETAPA 1 – INTERFAZ PRINCIPAL: INGRESO Y DIAGRAMA DE MOMENTOS
Elementos requeridos:

Entrada de los 6 momentos:

M1+ y M1− (primer extremo)

M2+ y M2− (centro del vano)

M3+ y M3− (segundo extremo)

Selector de tipo de sistema:

Dual tipo 1

Dual tipo 2

Visualización:

Diagrama de momentos originales (sin corregir), representado gráficamente en la parte superior

Diagrama de momentos corregidos (según el sistema elegido), en la parte inferior

Cada diagrama debe tener etiquetas, unidades y leyenda

Botones:

“Calcular Momentos Corregidos” → genera el segundo diagrama con los valores corregidos

“Ir al Diseño de Acero” → cambia de interfaz a la segunda etapa del proceso

ETAPA 2 – INTERFAZ DE DISEÑO DE ACERO
Visualización principal:

Diagrama esquemático de la viga con refuerzos:

Parte superior: mostrar visualmente los aceros requeridos (según los momentos corregidos)

Parte inferior: mostrar visualmente los aceros de diseño seleccionados por el usuario

Elementos interactivos:

Selector para elegir hasta 2 tipos distintos de acero:

Casilla 1: cantidad y diámetro (ej. 2 Ø16)

Casilla 2: cantidad y diámetro (ej. 1 Ø25)

Cálculo automático del área de acero total de diseño

Comparación en pantalla:

Área requerida vs. área diseñada

Verificación de cumplimiento (diseño ≥ requerido)

Botones adicionales:

“Verificar diseño” → muestra si el diseño cumple o no

“Captura para Word” → toma automáticamente una captura de esta ventana y la guarda como imagen o la envía a Word (usar pyautogui y opcionalmente python-docx)


ETAPA 3 – VISUALIZACIÓN DE FÓRMULAS
Permite convertir expresiones lineales como `As = Mu / (0.9 * fy * (d - a/2))` en un formato fraccionario similar al de un libro de cálculo.
Elementos principales:
* Campo de texto para la fórmula
* Botón **Mostrar** que renderiza la ecuación
* Botones **Capturar** y **Exportar** para copiar la imagen o guardarla en PNG, PDF o Word

“Volver a Momentos” → para regresar a la etapa anterior y modificar datos si es necesario

CONSIDERACIONES TÉCNICAS:
Lenguaje: Python 3.x

Normativa: Toda lógica y cálculo se basa en la NTP E.060 (Perú). No es necesario explicar ni insertar fórmulas, ya que el modelo tiene acceso a ellas.

Librerías sugeridas:

tkinter (interfaz gráfica)

matplotlib (graficar los diagramas de momento)

pyautogui o Pillow (captura de pantalla)

python-docx (inserción opcional en Word)

math o numpy (cálculos)

El código debe estar modularizado:

Una función para corrección de momentos

Una función para cálculo de área de acero requerida

Una función para graficar momentos

Una función para comparar aceros

Una función para captura de interfaz

RESUMEN DE INTERFAZ (UX):
Ventana 1: Ingreso de momentos → Diagramas superior/inferior → Corrección → Botón "Ir al Diseño"

Ventana 2: Visualización de viga con aceros → Selección de varillas → Resultados y verificación → Botón captura/exportar

ETAPA 4 – MEMORIA DE CÁLCULO
Muestra un resumen detallado de cada operación realizada en el diseño. Las fórmulas se presentan con notación LaTeX para una lectura clara e incluye botones para **Capturar**, **Exportar a PDF** o **Exportar a Word**.

## Requisitos de plataforma

- Python 3.8 o superior instalado en el sistema.
- Sistema operativo con soporte para PyQt5 (Windows, macOS o distribuciones de
  Linux con entorno de escritorio).

## Instalación de dependencias

1. Se recomienda crear un entorno virtual con `venv` o herramienta similar.
2. Instalar las bibliotecas necesarias a partir del archivo `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

   Para funciones opcionales de captura o exportación a Word se pueden agregar
   `pyautogui` y `python-docx`.
3. Para la visualización de fórmulas se recomienda contar con una distribución **LaTeX** instalada (TeX Live o similar).

## Ejecución

Desde la raíz del repositorio ejecutar:

```bash
python main.py
```

Se abrirá la interfaz gráfica donde se ingresan los momentos y se generan los
diagramas correspondientes.

## Activación

Al ejecutarse por primera vez, la aplicación solicita una clave de licencia.
Si la clave coincide con la esperada, se almacena una huella del equipo en un
archivo cifrado `key.dat` dentro de la carpeta de datos de la aplicación (por
ejemplo `%LOCALAPPDATA%\vigapp060` en Windows). Esta huella se genera a partir
de la MAC, el nombre de host y el número de serie del primer disco disponible.
En ejecuciones posteriores se descifra dicho archivo y se compara la huella con
la de la máquina actual para verificar la validez de la licencia.


## Formulario de datos y flujos

La aplicación cuenta con dos ventanas principales:

**Ventana de Momentos**

- Seis campos numéricos (`QLineEdit`) para ingresar `M1-`, `M2-`, `M3-`, `M1+`, `M2+` y `M3+`.
- Selector del sistema estructural con dos opciones: `Dual 1` y `Dual 2`.
- Botones principales: **Calcular Diagramas**, **Ir a Diseño de Acero** y **Capturar Diagramas**.

**Ventana de Diseño**

- Parámetros de sección: `b`, `h`, `r`, `f'c`, `fy` y `φ`.
- Selección de diámetros de estribo y varilla mediante `QComboBox`.
- Combos de cantidad y diámetro para dos tipos de barra en cada posición de momento.
- Indicadores de `As` mínimo/máximo y base requerida.
- Botón **Capturar Diseño**.

Los diagramas y resultados se actualizan cada vez que se modifican los datos o se presionan los botones de cálculo.

## Estructura del código y objetos principales

El código se encuentra organizado en la carpeta `src/` y se inicia desde `main.py`. El antiguo archivo `viga2.0.py` se eliminó en favor de `main.py` como punto de entrada. Los módulos principales son:

- **`beam_model.py`** — clase `BeamModel` con geometría, barras y lógicas de cálculo.
- **`rebar_editor_widget.py`** — panel lateral para editar rápidamente las barras.
- **`length_input_toolbar.py`** — barra de entrada de longitud con atajos `L/3`, `L/2` y `L`.
- **`section2d_view.py`** — vista 2D interactiva que permite arrastrar varillas.
- **`section3d_view.py`** — ventana 3D para inspeccionar la viga y su refuerzo.
- **`bar_properties_panel.py`** — diálogo con propiedades detalladas de cada barra.
- **`project_manager.py`** — gestor opcional para guardar o cargar configuraciones.
- **`summary_view.py`** — previsualización dinámica de la memoria de cálculo.
- **`utils.py`** — constantes y funciones auxiliares.

- **`moment_app.py`** — ventana de ingreso de momentos y corrección.
- **`design_window.py`** — etapa de diseño principal.
- **`view3d_window.py`** — vista tridimensional simplificada.
- **`memoria_window.py`** — ventana con memoria de cálculo detallada.
Las clases principales son:

- **`MomentApp`** (en `src/moment_app.py`)
  - `get_moments()` — lee los valores ingresados.
  - `get_length()` — obtiene la longitud de la viga.
  - `correct_moments(mn, mp, sys_t)` — aplica la corrección de la NTP E.060.
  - `plot_original()` y `plot_corrected()` — generan los diagramas.
  - `on_calculate()` — coordina lectura y graficado.
  - `on_next()` — abre la ventana de diseño con los momentos corregidos.

- **`DesignWindow`** (en `src/design_window.py`)
  - `_calc_as_req()` y `_calc_as_limits()` — cálculos de acero requerido y límites.
  - `_required_areas()` — devuelve las áreas necesarias por posición.
  - `draw_section()`, `draw_required_distribution()` y `draw_design_distribution()` — funciones de representación gráfica.
  - `update_design_as()` — calcula el refuerzo propuesto y verifica la base.
  - `_capture_design()` — copia la vista al portapapeles.
  - `show_view3d()` — abre una vista 3D simplificada.

- **`View3DWindow`** (en `src/view3d_window.py`)
  - `draw_views()` — genera la visualización 2D y 3D de la viga.

- **`MemoriaWindow`** (en `src/memoria_window.py`)
  - `_capture()` — guarda una captura de la memoria de cálculo.
- **`FormulaWindow`** (en `src/formula_window.py`)
  - Permite escribir una fórmula en texto y visualizarla en formato LaTeX.
  - Botones para capturar la vista o exportarla a PNG/PDF/DOCX.

Esta organización modular facilita la comunicación y coordinación dentro del equipo, ya que cada función se asocia a una tarea específica del flujo de trabajo.

## Guía de desarrollo

Consulta el archivo [DESARROLLO.md](DESARROLLO.md) para pautas sobre configuración del entorno y aportes al código.

### Icono de la aplicación

Los archivos de icono se almacenan en la carpeta `icon/`. Coloca tu imagen PNG en
ese directorio con el nombre `vigapp060.png` para que la interfaz lo utilice
automáticamente. La imagen original debe tener un tamaño de `1024x1024` y la
aplicación la escalará internamente a `256x256` cuando se inicie.

### Generar ejecutable en Windows

Para que el mismo icono aparezca en la barra de tareas y en el archivo `.exe`,
primero convierte `vigapp060.png` a formato `.ico`. Luego usa
`auto-py-to-exe` o `pyinstaller` indicando esa ruta en la opción `--icon`.



### Sistema de Activación y Validación de Licencias – VIGA_FINAL (Versión Beta)

Este sistema protege la aplicación contra uso no autorizado, ligando la licencia a una única computadora mediante el número de serie del disco duro (S/N). La activación es completamente local, sin requerir conexión a internet, y es ideal para distribución controlada de versiones beta.

La validación está contenida en un módulo independiente ubicado en la carpeta activacion/. El archivo principal del proyecto (main.py) no realiza la validación directamente, sino que llama a este módulo para verificar el estado de activación antes de continuar.

🧠 ¿Cómo funciona?
La primera vez que se ejecuta la aplicación, se abre una ventana de activación (activacion/ventana_activacion.py). Esta obtiene automáticamente el serial del disco mediante el comando wmic, y lo muestra como un ID de solicitud. El usuario debe copiar ese ID y enviarlo al desarrollador.

El desarrollador, usando activacion/generador_licencia.py, genera una clave de activación alfanumérica de 6 caracteres. Esta clave se construye combinando el ID con una clave secreta interna, aplicando un hash SHA256, convirtiéndolo a base 36 y tomando los primeros 6 caracteres.

El usuario ingresa esta clave en la ventana de activación. Si la clave es válida para ese equipo, el sistema:

Crea un archivo local de activación llamado licencia.key.

Este archivo almacena la clave validada y el ID del sistema.

En futuras ejecuciones, la app lee licencia.key y lo compara con el serial actual del disco.

Si coinciden, el programa se activa automáticamente y no vuelve a pedir código.

Si el archivo se copia a otra máquina, el ID no coincide y la activación es rechazada.

🖥️ Sobre el generador de licencias
El generador (generador_licencia.py) puede tener interfaz gráfica o ser por consola. Permite pegar el ID, generar la clave, copiarla, y cerrar. Su uso es exclusivo del desarrollador y está protegido por una clave secreta interna no compartida.

✅ En resumen:
La activación solo se realiza una vez por máquina.

Se guarda localmente en licencia.key.

El sistema se asegura de que esa clave solo sea válida en la misma PC.

No se requiere conexión a internet ni base de datos.

Si se copia la app a otro equipo, no podrá validarse con ese archivo.

main.py depende del módulo activacion/ para realizar la validación.

Las claves son cortas, legibles y únicas: 6 caracteres alfanuméricos (ej. 8ZK7X1).

El sistema es liviano, local y adecuado para versiones beta.

### Cambios recientes

- Los diagramas de momentos se ajustaron para mostrar los valores negativos
  hacia arriba y los positivos hacia abajo, respetando su posición habitual.
- La función `correct_moments` aplica ahora los mínimos por cara y global
  siguiendo los criterios de Dual 1 y Dual 2.
- Se añadió una pantalla de carga inicial y un menú principal unificado.

## Desarrollo de Refuerzo

Se añadió un botón **Desarrollo de Refuerzo** en la ventana de diseño que abre
una representación simple de la viga. Actualmente se muestran los cortes de
sección en M1, M2 y M3. La longitud de la viga se ingresa en esta ventana
mediante el campo **L (m)** (sin efecto por ahora). Esta vista incluye una
textura grisácea semitransparente para el concreto y las barras se sombrean con
transparencia. Además es posible reordenar las barras de cada sección haciendo
clic en una barra y utilizando las flechas izquierda/derecha del teclado o
arrastrándola a la posición deseada. Internamente la función `swap_bars` en
`View3DWindow` permite intercambiar dos varillas de una sección.
Las varillas ahora se dibujan por capas (hasta 4) usando colores primarios
para distinguirlas, siguiendo el mismo criterio de la primera capa.
Es una funcionalidad experimental que sirve como paso previo a la integración
más completa descrita en [DESARROLLO_3D.md](DESARROLLO_3D.md).

## Licencia

Este proyecto se distribuye bajo los términos de la [Licencia MIT](LICENSE).

