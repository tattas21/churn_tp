---
name: ds-feature
description: >
  Feature Engineering para data science: modo ML (pipeline train/test, sin leakage, handoff al Modeler) y modo BA (variables de negocio con trazabilidad de las 11 técnicas IAAN, validaciones semánticas, temporalidad). NO hace feature selection en modo ML.
  Trigger: "/ds-feature", "preparar features", "variables de negocio", "enriquecer dataset", feature engineering, encodings, modo BA.
license: Apache-2.0
metadata:
  author: agus-chaud
  version: "1.1.0"
---

## Cómo se explica esta skill (auto-descripción)

Esta skill es el **puente entre datos crudos y datos listos para decidir**: o bien para **modelar** (tabla X/y con pipeline reproducible), o bien para **explicar el negocio** (variables derivadas con sentido, nombreable y defendible ante un comité). No mezcla responsabilidades con el Explorer (quien perfila y entrega handoff), ni con el Modeler (quien entrena y hace **feature selection**). Si el usuario pide "solo features para Power BI / cuadro de mando", activá **modo BA**. Si pide "dataset para entrenar", activá **modo ML**. En ambos casos: **split primero en ML**, **orden temporal explícito en series y cohortes**, y **cada variable nueva lleva técnica y justificación**.

## When to Use

**Modo ML (por defecto si el objetivo es entrenar)**

- Existe `reports/handoff_to_modeler.md` generado por el Explorer
- Usuario pide transformar variables, preparar datos para modelar, o aplicar encodings
- Se invoca `/ds-feature` o variantes ("preparar features", "transformar datos", "feature engineering")
- Hay un plan en `plans/` que especifica qué features construir

**Modo BA — Business Analytics / variables de negocio**

- Objetivo es **medir, segmentar, rankear o explicar** con variables derivadas (no necesariamente tabular para sklearn)
- Triggers: "variables de negocio", "crear KPI derivados", "segmentos", "Pareto", "cohorte", "ranking", "modo BA", "/ds-feature ba"
- Pedido explícito de trazabilidad pedagógica (saber **qué técnica** aplicó a cada columna nueva)

## Inputs Permitidos

| Fuente | Qué leer |
|--------|----------|
| `data/raw/` | Datos crudos originales — fuente de verdad |
| `reports/handoff_to_modeler.md` | Columnas a dropear, encodings sugeridos, warnings de leakage |
| `reports/data_quality.md` | Problemas de calidad a resolver (nulls, outliers, constantes) |
| `plans/` | Qué features construir y por qué |
| Engram | Decisiones de transformación previas, features descartadas |

## Modo operativo: ML pipeline vs BA (variables de negocio)

| Aspecto | Modo ML | Modo BA |
|---------|---------|---------|
| Objetivo | `X_train` / `X_test` y `y` listos para el Modeler | Dataset enriquecido para análisis, reporting, decisión operativa |
| Split train/test | **Obligatorio antes de cualquier fit** | No siempre; si hay entidad temporal o cohorte, definí ventanas o holdout **con criterio explícito** |
| Feature selection | No (Modeler) | Puede haber **priorización** de variables para el cuadro (no es subset para CV) |
| Trazabilidad | `feature_report.md` + pipeline | Misma rigor **más** columna "técnica BA" por variable (véase catálogo) |
| Validación | Leakage, shapes, reproducibilidad | + **semántica** (rangos, monotonía esperada, coherencia fechas/cohortes) |

**Regla de oro**: en modo BA no abandonás buenas prácticas de datos: si después alguien quiere modelar con el mismo enriquecimiento, el report debe permitir replicar transformaciones sin magia.

## Catálogo BA — 11 técnicas (IAAN) y cuándo usarlas

Síntesis alineada al material *Creación de variables de negocio* (cheatsheet, notebooks 01–03). Cada variable **nueva** debe poder etiquetarse con al menos una de estas familias (en `reports/business_variables_report.md` o en el `feature_report.md` en tabla ampliada).

| # | Técnica | Patrones pandas / numpy | Usala cuando… |
|---|---------|-------------------------|----------------|
| 1 | Cálculos directos y vectorizados | Operaciones entre columnas, `assign` | Derivás un ratio, margen, diferencia entre columnas existentes |
| 2 | `apply` por fila o columna | `df.apply`, `series.map` | La lógica **no** se expresa en una sola expresión vectorizada simple (usar con moderación) |
| 3 | `transform` vs `apply` con `groupby` | `groupby(...).transform` devuelve **misma longitud** que el índice | Necesitás una métrica **por fila** dentro de cada grupo (p. ej. % del total del grupo) |
| 4 | `groupby().agg` vs `transform` | `agg` reduce a una fila por grupo; `transform` alinea | Querés **resumen** por grupo vs **feature a nivel fila** |
| 5 | Discretización | `pd.cut`, `pd.qcut` | Segmentás en bandas; usá `-np.inf`/`np.inf` en `bins` si los extremos son abiertos |
| 6 | Condicionales | `np.where`, `np.select` | Reglas de negocio explícitas por tramos |
| 7 | Serie temporal / cohortes | `cumsum`, `cummax`, `cummin`, `cumprod`, `pct_change`, `shift` | Acumulados, variaciones, lags; **siempre** orden por tiempo y `groupby` por entidad si aplica |
| 8 | Rankings | `rank(method='first', ascending=...)` | Posición relativa dentro de un universo o dentro de un grupo |
| 9 | Dummies | `pd.get_dummies(..., drop_first=..., dtype=int)` | Modelado o tablas pivot; cuidado **multicolinealidad** si `drop_first` depende del contexto |
| 10 | Pareto | ordenar → posición → % acumulado | Priorización de clientes, productos, causas (véase plantilla abajo) |
| 11 | Preproceso de nombres y tipos | estandarizar columnas, `set_index` temporal, `to_numeric` | **Siempre** como paso previo cuando los datos vienen "de la calle" |

**Matriz rápida "¿qué elijo?"**

- ¿La pregunta es "¿cuánto aporta cada categoría al total?" → agregación + posible Pareto (#10).
- ¿La pregunta es "¿cómo evoluciona cada unidad en el tiempo?" → temporal (#7) con orden y entidad.
- ¿La pregunta es "¿a qué segmento pertenece esta fila?" → discretización (#5) o condicionales (#6).

## Outputs por modo (separación ML vs BA)

**Modo ML** (`reports/feature_report.md` + artefactos ya definidos abajo).

**Modo BA** — además o en lugar del pipeline ML:

| Archivo | Contenido |
|---------|-----------|
| `data/processed/dataset_ba_enriched.parquet` (o CSV acordado) | Mismo universo de filas que el análisis + **columnas nuevas** con nombres de negocio |
| `reports/business_variables_report.md` | Por cada variable nueva: nombre, **técnica BA (#1–11)**, fórmula o código de referencia, supuestos, validaciones pasadas |
| Gráfico opcional | Si hubo Pareto: referencia al archivo exportado (`reports/figures/pareto_*.png`) |

Si un proyecto pide **ambos** modos, mantené **dos ramas de salida**: no mezcles `features_train.parquet` con columnas solo-BA sin documentarlo en ambos reportes.

## Validaciones semánticas (modo BA y sanity checks en ML)

Además de tipos y nulls:

- **Rangos**: ¿la variable derivada respeta dominio de negocio? (p. ej. proporciones en [0,1], días ≥ 0).
- **Monotonicidad esperada**: si el negocio asume "a más X, más Y", documentá si el dato la cumple o por qué no.
- **Coherencia temporal**: fechas no decrecientes por entidad; sin mezclar periodos (ver siguiente sección).
- **Cohortes**: mismas reglas de ventana (quién entra en la cohorte y en qué timestamp).

## Reglas de temporalidad y cohortes

1. **Orden**: ordená explícitamente por variable de tiempo antes de `shift`, `pct_change`, acumulados.
2. **Entidad**: si hay cliente/usuario/producto, usá `groupby(entidad).transform(...)` o `shift` **por grupo**, no global salvo que el negocio lo pida.
3. **No mezclar periodos**: si fusionás meses distintos, documentá la regla (¿suma? ¿promedio? ¿último valor?).
4. **Leakage en ML**: si una feature temporal se usa en modelado, el split respeta el tiempo (**time-based split**), no mezclar futuro en train.

## Plantilla Pareto (reutilizable)

1. Ordenar descendente por la métrica de impacto (ventas, coste, frecuencia).
2. Calcular suma total y **% sobre total** por fila.
3. **% acumulado** sobre el universo ordenado.
4. Marcar "top que explica el ~80%" (regla orientativa, no dogma).
5. Export opcional: tabla + gráfico de barras + línea acumulada (matplotlib/seaborn); guardar ruta en el report BA.

## Checklist previo: patrones de datos sucios (material IAAN)

Antes de transformar, en **modo ML y BA**:

- [ ] Nombres de columnas: acentos, espacios, mayúsculas inconsistentes → **normalizar**.
- [ ] Números con formato local (guiones, separadores miles) → **`to_numeric` con `errors`** y trazabilidad de filas inválidas.
- [ ] Fechas en string heterogéneas → **parse explícito** o `infer_datetime_format` con revisión de NaT.
- [ ] Índice temporal opcional pero recomendado si hay serie: **`set_index`** o columna `fecha` tipada `datetime64`.
- [ ] Duplicados lógicos (misma entidad + mismo timestamp) → política explícita (agregar, último, error).

## Inputs PROHIBIDOS (Hard Stop)

- `src/models/` — no le concierne entrenar modelos
- `reports/eda.md` directamente — ya procesado en el handoff del Explorer; si necesitás algo de ahí, usá el handoff
- **Regla**: si estás entrenando o evaluando un modelo, saliste del scope. STOP.
- **Regla**: si estás haciendo feature selection (elegir qué features usar), eso es del Modeler. STOP.

## Outputs Requeridos (modo ML)

| Archivo | Contenido |
|---------|-----------|
| `data/processed/features_train.parquet` | Features transformadas — solo filas de train |
| `data/processed/features_test.parquet` | Features transformadas — solo filas de test |
| `src/features/pipeline.py` | Pipeline reproducible sklearn/pandas |
| `reports/feature_report.md` | Justificación de cada transformación (si hay variables BA, añadí columna **Técnica BA**) |
| `reports/handoff_to_modeler.md` | Actualizado con feature list final + notas para el Modeler |

## Outputs PROHIBIDOS

- Modelos entrenados
- Feature selection (rankings, importances, subsets seleccionados) — eso es del Modeler
- Datos de test usados para fitear transformaciones

## SDD Flow Adaptado

### Fase 0 — Explore: "¿Qué me deja el Explorer?"

1. **Elegir modo**: ML (modelar), BA (variables de negocio), o **híbrido** (documentar las dos salidas).
2. **Checklist datos sucios** (patrones IAAN): nombres, numéricos con basura, fechas, duplicados (sección checklist arriba).
3. Leer `reports/handoff_to_modeler.md` — columnas a dropear, encodings sugeridos, warnings
4. Leer `reports/data_quality.md` — problemas pendientes de resolver
5. Buscar en engram (`mem_context` + `mem_search`) — ¿hubo decisiones de features previas?
6. Cargar `data/raw/` y, **si modo ML**, aplicar el split train/test ANTES de cualquier transformación que aprenda de datos

**Regla crítica del split (modo ML)**: el split se hace PRIMERO. Toda transformación se fitea sobre train y se aplica a test. Sin excepciones.

En **modo BA** sin modelado inmediato: el split puede no aplicarse, pero **orden temporal** y **ventanas** deben quedar definidos en el report para que un modelo futuro no herede ambigüedad.

### Fase 1 — Propose: Plan de Transformaciones

Proponer qué transformaciones aplicar, en qué orden, con justificación del Explorer:

> "Basado en el handoff: (1) dropear columnas de leakage → (2) imputar nulls → (3) encodings → (4) escalado → (5) features derivadas"

Alternativas explícitas cuando hay decisiones no triviales:
- ¿TargetEncoder vs OneHotEncoder para alta cardinalidad? Trade-offs explícitos.
- ¿Imputar con mediana vs KNNImputer? Trade-offs explícitos.

**STOP** — presentar al usuario y esperar confirmación antes de continuar.

### Fase 2 — Spec: Contrato de Features

Definir ANTES de transformar:

```
Variables de entrada: {lista del handoff}
Variables descartadas: {lista + razón del Explorer}
Variables de salida: {features que se van a producir}
Target: {nombre, sin transformar}
Split strategy: {train/test ratio, stratify, random_state}
```

**No-objetivos explícitos**:
- Feature selection → Modeler
- Hiperparámetros de transformación sin respaldo del EDA → no inventar

### Fase 3 — Design: Decisión por Variable

Documentar explícitamente qué transformación aplica a cada variable y POR QUÉ:

| Variable | Tipo | Problema detectado | Transformación | Justificación |
|----------|------|-------------------|----------------|---------------|
| `age` | numérica continua | outliers (IQR) | RobustScaler | resistente a outliers |
| `department` | categórica nominal, cardinalidad=8 | — | OneHotEncoder | baja cardinalidad, sin orden |
| `salary_band` | categórica ordinal | — | OrdinalEncoder | hay orden natural |
| `employee_id` | identificador | — | DROP | no es feature predictiva |

**Reglas de selección de transformación**:

| Situación | Transformación | Por qué |
|-----------|---------------|---------|
| Numérica con outliers severos | RobustScaler | Usa IQR, no se rompe con extremos |
| Numérica sin outliers, distribución normal | StandardScaler | Centrado y escalado clásico |
| Numérica con distribución muy asimétrica | log1p + StandardScaler | Reduce asimetría antes de escalar |
| Categórica nominal, baja cardinalidad (≤15) | OneHotEncoder | Sin supuesto de orden |
| Categórica nominal, alta cardinalidad (>15) | TargetEncoder | Evita explosión dimensional — fitear solo en train |
| Categórica ordinal | OrdinalEncoder con categorías explícitas | Preserva el orden |
| Variable con nulls < 5% | SimpleImputer (mediana/moda) | Rápido, suficiente |
| Variable con nulls 5-20% | KNNImputer o IterativeImputer | Más preciso cuando hay patrón |
| Variable con nulls > 20% | Crear flag `{col}_was_null` + imputar | El null puede ser señal |
| Identificador / constante / leakage | DROP | Sin valor predictivo o contamina |

### Fase 4 — Tasks: Bloques de Ejecución

**Bloque 1 — Split y setup**
1. Cargar `data/raw/` completo
2. Separar X e y
3. Aplicar train/test split (stratify=y si hay desbalance)
4. Verificar que test set NO se toca para fitear — solo para transform

**Bloque 2 — Limpieza según data_quality.md**
1. Dropear columnas de leakage (lista del handoff)
2. Dropear constantes y duplicados identificados
3. Verificar que el drop se aplica igual a train y test

**Bloque 3 — Imputación**
1. Fitear imputers sobre train
2. Aplicar a train y test
3. Verificar: ¿quedan nulls? Si sí, documentar por qué

**Bloque 4 — Encodings**
1. Fitear encoders sobre train (TargetEncoder usa y_train también)
2. Aplicar a train y test
3. Verificar: ¿nuevas columnas tienen nombres descriptivos?

**Bloque 5 — Escalado**
1. Fitear scalers sobre train
2. Aplicar a train y test
3. Verificar: ¿distribuciones post-escala son razonables?

**Bloque 6 — Features derivadas** (si el plan las incluye)
1. Crear features de interacción o ratio con justificación del EDA
2. Nombrarlas descriptivamente: `salary_per_year_experience`, no `feat_47`
3. Cada feature derivada tiene hipótesis de por qué agrega información

**Bloque 7 — Validación post-transformación**
1. Re-verificar ausencia de leakage en el dataset transformado
2. Verificar que test no filtró información a train
3. Chequear shapes: train + test = total original

### Fase 5 — Apply

Construir el pipeline sklearn:

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# Separar columnas por tipo
numeric_features = [...]
categorical_low = [...]
categorical_high = [...]
ordinal_features = [...]

numeric_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', RobustScaler())
])

categorical_transformer = Pipeline([
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
])

preprocessor = ColumnTransformer([
    ('num', numeric_transformer, numeric_features),
    ('cat_low', categorical_transformer, categorical_low),
    # ...
])

X_train_processed = preprocessor.fit_transform(X_train)
X_test_processed = preprocessor.transform(X_test)  # solo transform, nunca fit
```

Guardar:
- `preprocessor` serializado en `src/features/pipeline.py` como función `build_pipeline()`
- Arrays procesados como parquet en `data/processed/`

### Fase 6 — Verify: Autochecklist

Antes de emitir handoff, verificar:

**Modo ML**

- [ ] ¿El split se hizo ANTES de cualquier transformación?
- [ ] ¿Todos los fiteos (imputers, encoders, scalers) usan solo train?
- [ ] ¿Se aplicó transform (no fit_transform) al test set?
- [ ] ¿Shapes de output son consistentes? (train + test = total)
- [ ] ¿No hay leakage post-transformación? (correlación target en test no debería ser perfecta)
- [ ] ¿Toda transformación tiene justificación en el feature_report?
- [ ] ¿Nombres de columnas son descriptivos? (no `col_0`, `x3`)
- [ ] ¿Las features derivadas tienen hipótesis respaldada por el EDA?
- [ ] ¿Se hizo feature selection? → STOP, eso es del Modeler
- [ ] ¿El pipeline es reproducible? (random_state fijo, sin side effects)

**Modo BA (añadidos)**

- [ ] ¿Cada variable nueva tiene **técnica BA (#1–11)** en el report?
- [ ] ¿Pasaron validaciones semánticas (rangos, coherencia fechas/cohortes)?
- [ ] ¿Orden temporal y `groupby` por entidad correctos para `shift` / acumulados?
- [ ] Si hubo Pareto: ¿pasos reproducibles y figura/archivo referenciado?

### Fase 7 — Archive

Guardar en engram (`mem_save`):
- Transformaciones aplicadas y su justificación
- Decisiones no triviales (por qué TargetEncoder y no OHE para X)
- Features derivadas creadas + hipótesis
- Columnas dropeadas + razón
- Warnings para el Modeler

**NO guardar**: arrays numpy, DataFrames, outputs de shape/describe.

## Formato del Feature Report

Archivo: `reports/feature_report.md`

```markdown
# Feature Engineering Report
**Fecha**: {fecha}
**Input**: data/raw/{archivo}
**Modo**: ML | BA | híbrido
**Output**: data/processed/features_train.parquet, features_test.parquet (+ dataset_ba_enriched si aplica)
**Split**: {train_size} train / {test_size} test — stratify={True/False} — random_state={N}

---

## Columnas Dropeadas

| Columna | Razón |
|---------|-------|
| {col} | leakage detectado por Explorer |
| {col} | constante — sin varianza |

---

## Transformaciones Aplicadas

| Variable original | Transformación | Técnica BA (#) | Parámetros | Justificación |
|-------------------|----------------|----------------|------------|---------------|
| {col} | RobustScaler | — | — | outliers detectados (IQR) en EDA |
| {col} | OneHotEncoder | — (9 dummies) | handle_unknown='ignore' | categórica nominal, cardinalidad=8 |
| `monto_acum_ventas` | — | (7) cumsum por cliente | — | KPI de carrera por entidad |
| {col} | log1p + StandardScaler | — | — | asimetría positiva severa (skew=4.2) |

---

## Features Derivadas

| Feature nueva | Fórmula | Hipótesis |
|---------------|---------|-----------|
| `salary_per_tenure` | salary / years_at_company | Empleados con bajo salario relativo a antigüedad tienen mayor attrition |

---

## Imputación

| Variable | % Null | Estrategia | Flag creado |
|----------|--------|------------|-------------|
| {col} | 3% | mediana | No |
| {col} | 18% | KNNImputer | Sí — `{col}_was_null` |

---

## Warnings para el Modeler

- {col_X} y {col_Y} tienen alta correlación post-encoding ({r}). Considerar VIF antes de incluir ambas.
- El desbalance es {ratio}. Evaluar class_weight o umbral de clasificación.
- TargetEncoder en {col} puede introducir overfitting leve — validar con CV.
```

## Formato `business_variables_report.md` (solo modo BA)

Archivo: `reports/business_variables_report.md`

```markdown
# Variables de negocio — reporte
**Fecha**: {fecha}
**Dataset**: data/processed/dataset_ba_enriched.{ext}

## Variables nuevas

| Columna nueva | Técnica BA (#) | Fórmula / pasos | Supuestos | Validación |
|---------------|----------------|-----------------|-----------|------------|
| `share_ventas_grupo` | 3 `transform` | ventas / sum(ventas) por mes | ... | suma por grupo = 1 |

## Temporalidad

- Entidad: {columna}
- Tiempo: {columna}
- Orden aplicado: sí/no

## Pareto (si aplica)

- Métrica: ...
- Figura: reports/figures/pareto_*.png
```

## Formato del Handoff Actualizado

Actualizar `reports/handoff_to_modeler.md` agregando sección:

```markdown
## Feature Engineering — Resultado Final

**Features disponibles**: {N} columnas
**Train shape**: {filas} × {cols}
**Test shape**: {filas} × {cols}
**Pipeline**: `src/features/pipeline.py` — función `build_pipeline()`

### Features a evaluar para selection (decisión del Modeler)
{lista completa de features disponibles con tipo}

### Recomendaciones para el Modeler
- Empezar con todas las features y usar el Modeler para selection
- Atención a correlación entre {col_X} y {col_Y}
- Desbalance: aplicar {estrategia sugerida}
```

## Naming Conventions (Obligatorio)

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Feature original transformada | `{nombre_original}` | `age` |
| Feature escalada | `{nombre_original}` | `age` (el scaler está en pipeline, no en nombre) |
| Feature OHE | `{col}_{categoria}` | `department_sales` |
| Feature derivada | `{componente1}_per_{componente2}` / `{col}_ratio` | `salary_per_tenure` |
| Flag de null | `{col}_was_null` | `last_evaluation_was_null` |

**Prohibido**: `col_0`, `x3`, `feature_47`, `transformed`, `new_col`.

## Anti-Patrones (NUNCA hacer esto)

| Anti-patrón | Por qué es malo | Alternativa |
|-------------|-----------------|-------------|
| fit_transform en test set | Leakage de distribución | Solo transform en test |
| Split DESPUÉS de transformar | Leakage por imputer/scaler | Split siempre primero |
| Feature selection aquí | Viola separación de responsabilidades | Pasar todo al Modeler |
| Features sin nombre descriptivo | Imposible debuggear | Naming conventions obligatorias |
| Transformación sin justificación del EDA | Invención sin respaldo | Toda transformación referencia un hallazgo |
| TargetEncoder fiteado en todo el dataset | Leakage del target | Fitear solo con y_train |
| Ignorar columnas con nulls > 20% sin flag | Perder señal implícita en el null | Crear `{col}_was_null` antes de imputar |

## Decision Logging (personalizado)

Objetivo: registrar decisiones de transformación que afectan validez y mantenibilidad.

### Candidate Gate (Feature)

Registrar como candidata solo si hubo:
- Elección no trivial de imputación/encoding/escalado (con trade-off explícito)
- Decisión de dropear columnas por leakage, redundancia o baja utilidad
- Creación de features derivadas con hipótesis de valor predictivo
- Resolución de conflicto entre simplicidad del pipeline y performance esperada

### Comportamiento durante la tarea

- No interrumpir durante la construcción del pipeline.
- Guardar internamente candidatas con: variable, decisión, alternativa y riesgo evitado.

### Cierre de tarea (una sola pregunta)

Si hay candidatas:
"Detecté {N} decisiones de feature engineering candidatas para `decisions.md` (imputación/encoding/drop/derivadas). ¿Querés que las documente ahora?"

Si no hay candidatas: no preguntar.

### Plantilla sugerida para `decisions.md` (Feature)

1. **Contexto**: variable(s), problema detectado y restricción del pipeline.
2. **Decisión tomada**: transformación elegida y criterio técnico.
3. **Alternativas consideradas**: opciones descartadas y por qué.
4. **Consecuencias**: impacto en leakage, reproducibilidad y handoff al Modeler.

## Integración con Gentleman Mode

Referencia de tono y pedagogía: `skills/gentleman/SKILL.md`. Esta skill debe poder **explicarse sola** en conversación: si te preguntan "¿qué sos y qué no sos?", usá el guión corto de abajo y **no** diluyas fronteras por amabilidad.

### Guión de auto-presentación (para el agente)

1. **Quién soy**: "Soy la skill de **feature engineering**: preparo datos **listos para modelar** (modo ML) o **listos para decidir** (modo BA). No entreno modelos ni elijo el subset final de columnas para el algoritmo — eso es el Modeler."
2. **Qué entrego**: "En ML: `features_train`/`features_test`, `pipeline.py` y reportes. En BA: dataset enriquecido + `business_variables_report` con la **técnica IAAN** que usamos por cada variable."
3. **Qué no hago**: "No hago EDA de exploración inicial (Explorer); no hago feature selection para ML (Modeler); no invento transformaciones sin amarre al handoff o al negocio."
4. **Por qué importa**: "Si confundís transformación con selección de variables, o mezclás train y test, el número que ves en el notebook **miente**. Por eso el split primero y el report."

### Razonamiento en voz alta (correcciones típicas)

- **Feature selection en ds-feature**: "Pará: acá **transformamos** y dejamos el menú completo para el Modeler. Si seleccionás columnas vos para el algoritmo en esta etapa, contaminás la historia de qué aportó cada cosa. Eso es trabajo del Modeler con su criterio de validación."
- **fit_transform en test**: "Esto es **leakage** de distribución. El test tiene que entrar al pipeline como invitado que no enseña: solo `transform`."
- **Modo BA sin tiempo ordenado**: "Acá hay `shift` o acumulados. ¿Ordenamos por fecha y, si hay cliente, agrupamos antes? Si no, el KPI está **bonito y falso**."
- **Variable nueva sin técnica etiquetada**: "¿Qué número del catálogo BA es? Si no lo sabemos, no está lista para explicarla en una reunión."
- **Trade-offs al proponer**: No "puse OHE". Sí: "OHE porque cardinalidad baja y no hay orden; si sube, pasamos a TargetEncoding **solo en train** en modo ML."

### Ritmo Gentleman

- **STOP en Fase 1** (ML): confirmación antes de transformar. En **BA**, al menos **validación explícita** del mapa de variables nuevas antes del código masivo.
- Celebrá la pregunta incómoda: el usuario que pide leakage o mezcla de roles **está aprendiendo a defender el análisis**.

### Frases puente hacia otras skills

- Hipótesis o tests formales antes de decidir transformación → **`ds-stats`**.
- Exploración inicial y handoff → **`ds-explorer`**.
- Entrenar, seleccionar features, métricas → **`ds-model`**.

## Regla transversal de hipótesis (obligatoria)

- Si para justificar una transformación se necesita plantear o contrastar hipótesis, usar la skill `ds-stats` antes de decidir.

## Complemento: skill `ds-stats`

**Supuestos** y **diagnóstico formal** de normalidad, linealidad y multicolinealidad (y lectura inferencial asociada) → skill **`ds-stats`**. En **ds-feature** solo se implementan las **transformaciones acordadas** (pipeline, imputación, encoding, escalado) con justificación en `feature_report.md`.
