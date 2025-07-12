
# DISEÑO POR CORTE — MÓDULO `shear_design`

Este módulo realiza el diseño por corte para vigas de concreto armado según normativa vigente. Está basado en el esquema de distribución mínima de estribos para vigas **tipo Dual 1 y Dual 2**, y considera casos de **vigas apoyadas o voladas**.

La ventana de diseño por corte muestra ahora lateralmente la sección de la viga con sus dimensiones básicas y los diámetros seleccionados de varilla y estribo.

---

## 1. DATOS DE ENTRADA

- `Vu`: Cortante último (en **Tn-f**, tnf)
- `Ln`: Luz libre de viga (en **m**)
- `d`: Peralte efectivo (en **cm**)
- `b`: Base de la sección (en **cm**)
- `f'c`: Resistencia del concreto (en **kg/cm²**)
- `Fy`: Fluencia del acero (por defecto: 4200 kg/cm²)
- `φ_cortante`: Coeficiente de reducción por corte → `0.85`

Estos valores pueden obtenerse del diseño por flexión (si está presente), o ser editados manualmente.

---

## 2. CÁLCULOS PRINCIPALES

### 2.1 Cortante resistente del concreto:

```
Vc = 0.53 * sqrt(f'c) * b * d
```

> En unidades de **kg**, luego convertido a **Tn-f**

### 2.2 Área transversal de acero (estribos):

```
Av = n_ramales * área_varilla
```

> Por defecto: 2 ramales con varilla de 3/8" → Av = 2 * 0.71 = **1.42 cm²**

### 2.3 Cortante que resiste el acero:

```
Vs = (Av * Fy * d) / S
```

> S: separación en cm. Inversamente, se despeja:

```
S = (Av * Fy * d) / Vs
```

---

## 3. ZONAS DE LA VIGA

- **ZONA DE CONFINAMIENTO (Lo)**  
  - Dual 1 → `Lo = 2h`  
  - Dual 2 → `Lo = 2d`

- **ZONA CENTRAL (Lc)**  
  ```
  Lc = Ln - 2Lo
  ```

---

## 4. SEPARACIONES MÍNIMAS

### Zona de confinamiento (SC):
Menor de los siguientes:
1. `d / 4`, no menor a 150 mm  
2. `10ϕ` (ϕ = diámetro de barra longitudinal menor)  
3. `24ϕ_estribo`  
4. `300 mm`

### Zona restante (SR):
- Entre `0.5d` y `300 mm`

---

## 5. VERIFICACIONES

### Condición mínima normativa:

> Se distribuyen estribos con SC y SR **aunque Vu < φVc**

### Condición de seguridad:

> Debe cumplirse **en todo momento**:
```
Vu ≤ φ (Vc + Vs)
```

- Se evalúa Vs calculado y también Vs mínimo, y si **no se cumple**, se genera alerta.

---

## 6. DIÁMETROS DISPONIBLES

| Diámetro nominal | Área (cm²) | Descripción |
|------------------|-------------|-------------|
| 3/8”             | 0.71        | Varilla No. 3 |
| 1/2”             | 1.27        | Varilla No. 4 |
| 5/8”             | 1.98        | Varilla No. 5 |

> No se permiten diámetros personalizados.

---

## 7. RESULTADO Y REPORTE

- Se genera:
  - **Gráfico de distribución de estribos** (zonas SC y SR)
  - **Tabla detallada de cálculos** (`Vc`, `Vs`, `S`, `φVc`, `φ(Vc+Vs)`)
  - **Verificación automática de Vu**

---

## 8. RECOMENDACIONES IMPLEMENTADAS

✔️ Valores editables si no hay flexión  
✔️ Redondeo inteligente:  
- Separaciones hacia abajo  
- Cantidades hacia arriba

✔️ Validaciones dobles  
✔️ Campo `Fy` editable  
✔️ Verificación en tiempo real

---

## 9. PENDIENTES A FUTURO

- Visualización de varillas en el gráfico  
- Detalle HTML final con cotas  
- Exportación a PDF/HTML integrada

---

> **Autor:** Humberto Cordero  
> **Proyecto:** VIGA_FINAL  
