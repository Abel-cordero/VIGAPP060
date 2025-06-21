# Diseño de Vigas NTP E.060

Esta aplicación implementa una interfaz gráfica para el cálculo y diseño de refuerzos en vigas de concreto armado siguiendo la Norma Técnica Peruana E.060.

Para más detalles de configuración revisa [DESARROLLO.md](DESARROLLO.md).

## Requisitos adicionales

Para generar los reportes en PDF se necesita tener instalada una distribución de
LaTeX que provea el ejecutable `pdflatex`. En Windows se recomienda instalar
[MiKTeX](https://miktex.org/) y asegurarse de que `pdflatex` esté disponible en
la variable de entorno `PATH`.

Si la compilación falla y MiKTeX informa que la base de datos está dañada o que
no se han verificado las actualizaciones, abre **MiKTeX Console** y ejecuta una
actualización completa. Luego puedes reparar la base de datos con:

```bash
initexmf --update-fndb
```

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

El código se encuentra organizado en la carpeta `src/vigapp/` y se inicia desde `main.py`. El antiguo archivo `viga2.0.py` se eliminó en favor de `main.py` como punto de entrada. Los módulos principales son:

- **`ui/length_input_toolbar.py`** — barra de entrada de longitud con atajos `L/3`, `L/2` y `L`.
- **`graphics/section2d_view.py`** — vista 2D interactiva que permite arrastrar varillas.
- **`graphics/section3d_view.py`** — ventana 3D para inspeccionar la viga y su refuerzo.
- **`sistema/project_manager.py`** — gestor opcional para guardar o cargar configuraciones.
- **`models/utils.py`** — constantes y funciones auxiliares.

- **`ui/moment_app.py`** — ventana de ingreso de momentos y corrección.
- **`ui/design_window.py`** — etapa de diseño principal.
- **`ui/view3d_window.py`** — vista tridimensional simplificada.
Las clases principales son:

- **`MomentApp`** (en `src/vigapp/ui/moment_app.py`)
  - `get_moments()` — lee los valores ingresados.
  - `get_length()` — obtiene la longitud de la viga.
  - `correct_moments(mn, mp, sys_t)` — aplica la corrección de la NTP E.060.
  - `plot_original()` y `plot_corrected()` — generan los diagramas.
  - `on_calculate()` — coordina lectura y graficado.
  - `on_next()` — abre la ventana de diseño con los momentos corregidos.

- **`DesignWindow`** (en `src/vigapp/ui/design_window.py`)
  - `_calc_as_req()` y `_calc_as_limits()` — cálculos de acero requerido y límites.
  - `_required_areas()` — devuelve las áreas necesarias por posición.
  - `draw_section()`, `draw_required_distribution()` y `draw_design_distribution()` — funciones de representación gráfica.
  - `update_design_as()` — calcula el refuerzo propuesto y verifica la base.
  - `_capture_design()` — copia la vista al portapapeles.
  - `show_view3d()` — abre una vista 3D simplificada.

- **`View3DWindow`** (en `src/vigapp/ui/view3d_window.py`)
  - `draw_views()` — genera la visualización 2D y 3D de la viga.

- **`FormulaWindow`** (en `src/vigapp/ui/formula_window.py`)
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


---

## 🧩 Funcionamiento del sistema

1. Al ejecutar `main.py`, se invoca `activacion/ventana_activacion.py`, que abre una ventana para gestionar la activación.
2. Se obtiene automáticamente el número de serie del disco duro mediante el comando `wmic`, y se muestra como un **ID de solicitud**.
3. El usuario copia ese ID y lo envía al desarrollador.
4. El desarrollador usa `generador_licencia.py` para generar una **clave de activación de 6 caracteres alfanuméricos en mayúscula** (ej. `A9F7D2`), basada en el ID.
5. El usuario ingresa la clave en la ventana.
6. Si la clave es válida, se guarda de forma local en el **Registro de Windows** (`HKEY_CURRENT_USER\SOFTWARE\MiApp\Licencia`), para que:
   - La activación solo se requiera **una vez por equipo**.
   - No se cree ningún archivo externo.
   - La clave **no funcione en otra computadora**, ya que depende del ID del disco.
7. En futuras ejecuciones, el sistema revisa automáticamente el Registro. Si la clave guardada es válida para el equipo actual, **la aplicación se inicia sin pedir activación**.

---

## 🛠️ Características técnicas

- El ID se genera con `wmic diskdrive get SerialNumber`.
- La clave se obtiene aplicando `SHA256` al ID + secreto, luego transformada a **base 36**, y truncada a 6 caracteres.
- El Registro de Windows se utiliza como almacenamiento persistente.
- No se generan archivos `.dat`, `.key`, ni bases de datos.
- El almacenamiento local es invisible al usuario casual y difícil de copiar entre equipos.

---

## 🖥️ Sobre el generador de licencias

- Ubicado en `activacion/generador_licencia.py`.
- Permite ingresar el ID del usuario, generar la clave, copiarla y cerrarlo.
- Puede tener una GUI estilo keygen (500x200 px) con campos "Request", "Activation", y botones "Generate", "Copy", "Quit".

---

## ✅ Ventajas

- **Activación única por equipo.**
- **Persistencia sin archivos.**
- **Protección simple y efectiva.**
- **Sin conexión a internet.**
- **No reutilizable entre PCs.**
- **Ideal para pruebas beta de software técnico.**

---

### Cambios recientes

- Los diagramas de momentos se ajustaron para mostrar los valores negativos
  hacia arriba y los positivos hacia abajo, respetando su posición habitual.
- La función `correct_moments` aplica ahora los mínimos por cara y global
  siguiendo los criterios de Dual 1 y Dual 2.

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

⚠️ NOTA IMPORTANTE:

Todo el cálculo estructural en esta aplicación se realiza utilizando **unidades tradicionales** según lo estipulado en el **Anexo 2 de la NTP E.060**. Las unidades utilizadas en todos los módulos son:

- Longitud: **cm**
- Fuerza: **kgf**
- Tensión: **kgf/cm²**
- Momento: **tonf·m**
- Área: **cm²**

Este enfoque asegura coherencia con la práctica profesional en Perú y con los formatos establecidos por el reglamento nacional.

No se usa el sistema internacional (SI) para los cálculos ni para el almacenamiento de variables internas.


# 📘 REESTRUCTURACIÓN MODULAR DE REPORTES – DISEÑO A FLEXIÓN

Este documento describe cómo debe actualizarse de forma modular la generación del reporte en PDF del diseño a flexión, dentro del proyecto `VIGA_FINAL`. El objetivo es lograr una presentación editorial clara, técnica y profesional, siguiendo normas de estilo específicas. No se deben generar estructuras nuevas, solo mejorar la presentación del reporte generado actualmente con ReportLab.

⚠️ Cada módulo de actualización debe ejecutarse de forma **secuencial y aislada** para evitar errores de interpretación por parte de Codex u otra IA.

---

## 📍 ETAPA 1 – TÍTULO PRINCIPAL

### 🎯 Objetivo:
Mostrar al inicio del reporte el título técnico con formato adecuado.

### 🛠️ Especificaciones:
- Texto: `"DISEÑO A FLEXIÓN DE VIGA bxh"`  
  (reemplazar `b` y `h` con los valores reales de base y altura ingresados).
- Fuente: `Arial`, tamaño `12`, estilo `negrita`.
- Alineación: `centrado superior del documento`.
- No debe repetirse en otra parte del reporte.

---

## 📍 ETAPA 2 – SECCIÓN DE DATOS

### 🎯 Objetivo:
Presentar los datos de entrada en una tabla clara, con encabezado correcto.

### 🛠️ Especificaciones:
- Encabezado: `"DATOS"` (en mayúsculas, reemplaza “Datos del Proyecto”).
- Fuente: `Arial`, tamaño `11`.
- Tabla de datos debe estar alineada y clara.
- A la derecha de esta tabla, insertar un gráfico técnico de la sección de la viga.

---

## 📍 ETAPA 3 – GRÁFICO DE SECCIÓN DE VIGA

### 🎯 Objetivo:
Mostrar un dibujo técnico que represente visualmente la sección de la viga.

### 🛠️ Especificaciones:
- Ubicación: a la derecha de la tabla de datos.
- Mostrar: base, altura, peralte (d), recubrimiento, estribo con offset.
- Estilo:
  - Líneas continuas finas (no punteadas).
  - Cotas con estilo técnico (sin flechas dobles grandes).
- Tamaño proporcional al bloque de datos.

---

## 📍 ETAPA 4 – SECCIÓN CÁLCULOS

### 🎯 Objetivo:
Mostrar el desarrollo técnico de cada fórmula del diseño a flexión.

### 🛠️ Subtítulos fijos con artículo normativo:
- Peralte: d (ART.1.1 E060)
- Coeficiente B1 (ART.1.1 E060)
- Pbal (ART.1.1 E060)
- Pmax (ART.1.1 E060)
- As mín (ART.1.1 E060)
- As máx (ART.1.1 E060)
- Fórmula general del As (ART.1.1 E060)
- As para M1, M2, M3, etc.

### 🧮 Formato del desarrollo:
- Estilo escalonado, por ejemplo:

- Cada fórmula debe mostrarse como imagen PNG renderizada desde LaTeX.
- Fracciones deben verse con `\frac{a}{b}` (nunca `1/2`, ni `\tfrac`).
- Usar `fontsize=6 o 7` para fracciones pequeñas.
- No mostrar fórmulas como texto plano.

---

## 📍 ETAPA 5 – SECCIÓN DE RESULTADOS

### 🎯 Objetivo:
Mostrar de manera clara los resultados de diseño final.

### 🛠️ Especificaciones:
- Mostrar todos los valores de As para los momentos corregidos.
- Ubicar esta sección al final del reporte como bloque bien separado.
- Puede incluir resumen de selección de acero si aplica.

---

## 📍 ETAPA 6 – IMÁGENES COMPLEMENTARIAS

### 🎯 Objetivo:
Agregar al reporte las vistas gráficas del diseño estructural.

### 🛠️ Incluir:
- Gráfica de momentos positivos y negativos.
- Secciones de acero (M1, M2, M3).
- Cada imagen debe estar centrada, con márgenes consistentes.
- No repetir imágenes innecesarias (por ejemplo, no duplicar sección).

## 🔒 RESTRICCIONES GENERALES

- No crear nuevas estructuras ni modificar lógicas existentes.
- No usar texto plano para fórmulas matemáticas.
- No usar librerías externas nuevas (todo debe integrarse a ReportLab).
- No modificar la lógica de cálculo, solo la presentación.

---

## 🧩 RECOMENDACIÓN DE USO

Se recomienda aplicar una etapa a la vez, validando que Codex la interprete y aplique correctamente antes de pasar a la siguiente.


