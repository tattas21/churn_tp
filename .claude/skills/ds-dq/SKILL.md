---
name: ds-dq
description: >
  Agente de calidad de datos con pandas: diagnóstico estructural (perfilado, nulos, duplicados, tipos, cardinalidad, correlaciones descriptivas)
  y corrección reproducible (tipos, drop, fillna/dropna, duplicados, rename, replace/map, texto .str).
  Basado en el material Pandas IV/V y el playbook del repo calidad-de-datos.md.
  Trigger: calidad de datos, limpieza de datos, perfilado, diagnóstico de calidad, corregir un CSV/Excel,
  nulos duplicados tipos pandas, "/ds-dq", "auditar calidad del dataset", "normalizar columnas".
license: Apache-2.0
metadata:
  author: agus-chaud
  version: "1.0.1"
  source_notes: "IAAN data-science-kit/calidad-de-datos.md"
---

## When to Use

- Perfilado y **auditoría de calidad** sin comprometerse aún a hipótesis de negocio ni a un notebook EDA ML completo.
- **Diagnóstico** antes de intervenir: nulos, duplicados (fila completa o por `subset`), tipos, cardinalidad, categóricas “sucias”, artefactos de Excel.
- **Corrección guiada por negocio**: índice natural, borrar columnas basura, `astype` / `to_numeric` / `to_datetime`, políticas de imputación, `drop_duplicates`, texto con `.str`.
- Usuario invoca `/ds-dq`, “limpiá este Excel”, “mapeá problemas de calidad”, “¿qué hacemos con los nulos?”.

## When NOT to Use (Hard Stop)

| Necesidad | Skill |
|-----------|-------|
| EDA amplio ML: target, leakage, gráficos obligatorios, hipótesis con test+p-valor, handoff al modeler completo | `ds-explorer` |
| Marco inferencial α/IC/supuestos/muestreo A/B más allá de correlación descriptiva | `ds-stats` |
| Pipeline train/test de features parquet y encoders para producción | `ds-feature` |
| Entrenar y comparar modelos | `ds-model` |

**Regla de oro (del playbook):** primero **caracterizar**, después **intervenir**. No mezclar turismo exploratorio sin mapa de calidad ni “limpiar a ciegas” sin diagnosticar.

## Fuente canónica en el repo

- **`calidad-de-datos.md`** (raíz del kit): cheatsheets, caso Madrid 2020, práctica notebooks 13–15, checklist de patrones. Esta skill **opera** ese conocimiento; si hay duda de detalle, alinear con ese documento.

---

## Principios

1. **Evitar solo-muestra** en auditoría pura de calidad (`sample`): los errores sistemáticos pueden no aparecer. `sample` sí sirve para fases posteriores o previews rápidos.
2. **`df.shape`** es sobre el DataFrame; no confundir con mitos tipo `pd.shape`.
3. **Duplicados** se definen por **negocio**: clave natural vs fila completa vs `subset=[...]`.
4. **`astype`** es genérico; **`pd.to_numeric` / `pd.to_datetime`** para datos sucios (`errors="coerce"` donde aplique).
5. **Casi todo en pandas es no mutante** salvo `inplace=True` o asignación explícita; **`insert`** siempre modifica el DataFrame.

---

## Inputs Permitidos

| Fuente | Uso |
|--------|-----|
| `data/raw/` | CSV, Excel, parquet crudos |
| Rutas absolutas que el usuario indique | Lectura puntual |
| `plans/` | Criterios de negocio ya definidos por el Planner |

## Inputs PROHIBIDOS

- Asumir `data/processed/` como fuente de verdad sin que el usuario lo pida.
- Escribir **pipeline de modelado** o features finales (eso es `ds-feature`).

## Outputs Recomendados

| Archivo | Contenido |
|---------|-----------|
| `reports/data_quality.md` | Inventario: dimensiones, tipos, % nulos, duplicados, cardinalidad, red flags, decisiones de negocio |
| `reports/data_cleaning_log.md` | Orden de operaciones aplicadas (reproducible), supuestos (p. ej. “NA en lesividad = sin lesión”) |
| `notebooks/00_calidad_datos.ipynb` | **Opcional** pero deseable: carga → diagnóstico → correcciones ejecutables de arriba abajo |

Si el proyecto ya usa `ds-explorer`, el `reports/data_quality.md` puede ser el **mismo** archivo o un suplemento “pandas/corrección” que el Explorer referencia.

---

## Fase A — Diagnóstico (qué hay)

### A.0 Visión global

| Objetivo | Herramienta | Notas |
|----------|-------------|--------|
| Filas × columnas, tipos, no nulos, memoria | `df.info(memory_usage="deep")` | Memoria **real** con `deep` |
| Dimensión | `df.shape` | |
| Tipos | `df.dtypes` | |
| Numéricas | `df.describe().T` | Transpuesta suele leerse mejor |
| Objetos/categóricas típicas | `df.describe(include=["O"]).T` | `unique`, `top`, `freq`, `count` |

### A.1 Nulos

```python
df.isna().sum().sort_values(ascending=False)
df.isna().mean().sort_values(ascending=False) * 100  # % por columna
```

- Priorizar columnas por umbral de negocio (ej. >20% faltantes → decisión explícita).

### A.2 Duplicados

```python
df.duplicated().sum()
df[df.duplicated()]
df[df.duplicated(keep=False)]  # todas las filas de grupos repetidos
df.duplicated(subset=["clave1", "clave2"]).sum()
```

- Con **índice de negocio** ya fijado: `df[df.duplicated(keep=False)].index.value_counts()` para ver severidad por clave.

### A.3 Cardinalidad

```python
df.nunique(dropna=True)   # dropna=False si NaN cuenta como nivel
```

- `series.unique()` con cuidado en cardinalidad gigante.

### A.4 Por tipo de variable

- **Categóricas/object:** `value_counts()`, `value_counts(normalize=True)`, `mode()`.
- **Numéricas:** `mean`, `median`, `min`, `max`; **`idxmax`/`idxmin`** para inspeccionar `df.loc[idx]` en extremos/outliers.

### A.5 Correlación (descriptiva)

- **`pearson`:** lineal (mejor si aproximadamente normales ambas variables).
- **`kendall` / `spearman`:** monotónicas; **ordinales** o no normales → ante la duda tender a **Kendall** como sugiere el material.
```python
df.corr(numeric_only=True)
s1.corr(s2, method="kendall")
```

### A.6 Operar por bloques de tipo

```python
df.select_dtypes("number").mean()
df.select_dtypes("object").mode()
```

### A.7 Checklist operativo (patrones rápidos)

1. Top-k columnas por % nulos: `df.isna().mean().sort_values(ascending=False).head(k)`
2. Columnas sobre umbral: `df.columns[df.isna().mean() > umbral].to_list()`
3. Categorías raras: `s.value_counts(normalize=True).sort_values().head(k) * 100`
4. Screening categóricas: `df.describe(include=["object"]).T`
5. Subconjunto + estadístico: `df[df.Sector == "Retail"].select_dtypes("number").mean()`

### A.8 Red flags Excel / export

- Columnas **`Unnamed: N`**: celdas vacías o basura; inspeccionar si todo NA o valores espurios (ej. `","`).
- Columnas de **hora/fecha como `object`**: evaluar `to_datetime` / parseo explícito.
- **Nombres de columna** con espacios raros o dobles espacios (ej. `'Nº  EXPEDIENTE'`) — fallos típicos al `set_index` o `rename`.

### A.9 Caso referencia (Madrid accidentalidad 2020)

- Dimensiones orientativas del ejercicio: ~28k×15; memoria ~20 MB con `deep`.
- Problemas típicos enunciados: índice debería ser expediente; muchas columnas object; dos últimas columnas sin información; duplicados; muchos nulos (ej. lesividad).
- **`NÚMERO` con modo `"-"`:** valor operativo fuente, no NA.
- **`RANGO DE EDAD` con DESCONOCIDA:** captura vs código de falta.
- Interpretación **`mediana > media`** en una numérica (ej. lesividad sin NA): sesgo/asimetría; complementar después con histogramas si el proyecto lo pide (`ds-explorer`).

---

## Fase B — Corrección (cómo intervenir)

Ejecutar en **orden dependiente**: tipología y duplicados antes de políticas de nulos sobre categorías recién definidas, salvo decisión contraria documentada.

### B.1 Tipos

**`astype`**

```python
s.astype("category")
df.astype({"a": "float", "b": "category"})
df.select_dtypes("object").astype("category")  # suele reducir memoria fuerte
# Asignación obligatoria: df[col] = ... o df = df.astype(...)
```

**Ordinal explícito**

```python
orden = pd.CategoricalDtype(["a", "b", "c"], ordered=True)
df["col"] = df["col"].astype(orden)
# Reordenar niveles existentes:
# df["col"] = df["col"].cat.set_categories([...], ordered=True)
```

**Numérico sucio**

```python
pd.to_numeric(s, errors="coerce")
```

**Fechas**

```python
pd.to_datetime(s, dayfirst=True, errors="coerce", format="%d%m%Y")  # format ejemplo
s.dt.strftime("%d/%m/%Y")  # presentación desde datetime
```

### B.2 Quitar / insertar filas y columnas

```python
df.drop(columns=[...])
df.drop(index=[...])
df.drop(index=df.index[0:5])  # por posición → etiquetas
df.insert(loc, "nombre", valores)  # inplace; revienta si el nombre existe
```

### B.3 Nulos

```python
df.dropna(axis=0, how="any|all", subset=[...], thresh=n)
df["col"].fillna(valor)
s.ffill(); s.bfill()
s.value_counts(dropna=False)  # antes/después
```

**Categórica + valor nuevo:**

```python
s = s.cat.add_categories("Nuevo_nivel")  # si hace falta
s.fillna("Nuevo_nivel")
```

⚠️ Imputar **fechas por moda**: mecánico; puede sesgar temporal/ML — documentar supuesto.

### B.4 Duplicados (eliminación)

```python
df.drop_duplicates(subset=[...], keep="first", inplace=False)
```

- No compara **índice**, solo columnas.

### B.5 Renombrar, reemplazar, map

```python
df.rename(columns={"a": "b"}, inplace=True)
df.replace({"Uganda": "Uga"})
s.map(func, na_action="ignore")  # claves no mapeadas → NaN en map con dict
```

### B.6 Texto `.str`

`upper`, `lower`, `capitalize`, `title`, `strip`, `len`, `split`, `cat`, `join` (join entre **caracteres** de cada string), `contains`, etc.

```python
df.columns = df.columns.str.replace(" ", "_")
mask = df.columns.str.contains("pattern")
```

- **`split`** separa; **`cat`** agrupa strings (evitar confusiones tipo cheatsheet mezclado).

### B.7 Pipeline ejemplo Madrid (notebooks 14–15)

Orden habitual del curso sobre el mismo `df`:

```python
df = pd.read_excel(".../2020_Accidentalidad.xlsx")
df.set_index("Nº  EXPEDIENTE", inplace=True)  # literal con dos espacios en expediente según práctica
df.drop(columns=["Unnamed: 13", "Unnamed: 14"], inplace=True)
df.rename(columns={"LESIVIDAD*": "LESIVIDAD"}, inplace=True)
df.drop_duplicates(inplace=True)

cols = df.loc[:, "DISTRITO":"SEXO"].columns
df[cols] = df.loc[:, "DISTRITO":"SEXO"].astype("category")

df.dropna(subset=["NÚMERO", "DISTRITO"], inplace=True)

moda_tp = df["TIPO PERSONA"].mode().values[0]
# idem ACCIDENTE, VEHÍCULO
df["TIPO PERSONA"] = df["TIPO PERSONA"].fillna(moda_tp)
# ...

df["SEXO"] = df["SEXO"].cat.add_categories("Se desconoce")  # SEXO es category en ese slice
df["SEXO"] = df["SEXO"].fillna("Se desconoce")
df["ESTADO METEREOLÓGICO"] = df["ESTADO METEREOLÓGICO"].fillna(
    "Se desconoce"
)  # object en la práctica oficial

df["LESIVIDAD"] = df["LESIVIDAD"].fillna(0)  # supuesto negocio: sin lesión

df.isna().sum().sort_values(ascending=False)
```

**Pieza pedagógica clave:** al asignar `category` por rango etiquetado, usar **`df.loc[:, desde:hasta]`** y luego **`df[cols] = df.loc[...,].astype('category')`** para no chocar con asignaciones sobre slices.

**Consecuencia:** si **meteorología** también fuera `category`, habría que **`add_categories('Se desconoce')`** antes de `fillna`, igual que en `SEXO`.

### B.8 Patrones Kiva-style (notebook 13)

- `object` → `category` masivo por `select_dtypes("object").columns`.
- Regla negocio + `drop(index=...)` para outliers/casos política (ej. pocos registros en mínimo de importe).
- **Anonymous masivo**, NA en nombres: subset explícitos para comunicación según política.

---

## Verificación de cierre (autochecklist)

- [ ] Nulos ordenados antes y después de intervenciones.
- [ ] Duplicados: criterio (`subset`) alineado con negocio; `keep` documentado.
- [ ] Tipos coherentes (`dtypes`) y categorías (`cat.categories`) tras imputaciones.
- [ ] Nuevos niveles categóricos: ¿`add_categories` aplicado donde la columna es `category`?
- [ ] Supuestos de negocio (ej. NA→0, NA→“Se desconoce”) escritos en el log.
- [ ] Notebook o script corre de arriba abajo sin errores.

---

## Anti-patrones

| Anti-patrón | Alternativa |
|-------------|-------------|
| Limpiar sin `info`/`describe`/nulos primero | Fase A completa o al menos checklist mínimo |
| Usar muestra como única base de auditoría | Dataset completo para calidad; muestra solo como apoyo |
| `fillna` en `category` con nivel nuevo sin ampliar categorías | `cat.add_categories` primero |
| Confundir `map` sin `na_action="ignore"` y machacar NA por error | `na_action="ignore"` o flujo explícito |
| Creer que `drop_duplicates` usa el índice | Comparación por columnas; si importa índice, resetear o incluir como columna |
| Inferencia causal desde correlación en esta skill | Correlación solo descriptiva; inferencia → `ds-stats` + diseño |

---

## Integración con otras skills

- **`ds-explorer`:** puede consumir `reports/data_quality.md` y concentrarse en señal, leakage e hipótesis; o el usuario invoca **primero** `ds-dq` y luego Explorer.
- **`ds-stats`:** interpretación rigurosa de tests cuando la pregunta deja de ser “¿está sucio?” y pasa a “¿esto es significativo bajo qué supuestos?”.
- **`ds-feature`:** recibe datos ya alineados con decisiones de calidad; no duplicar aquí train/test split.

## Integración con Gentleman (opcional)

**Propósito:** no cambia el playbook técnico de Fase A/B ni los handoffs a otras skills; cambia **cómo** se explican riesgos, supuestos de negocio y alternativas cuando el usuario pidió **modo Gentleman**, referencia `skills/gentleman`, o instrucciones equivalentes (`/gentleman`, «modo gentleman», etc.). El tono apasionado/mentor del workspace es independiente: **Gentleman** (Rioplatense, patrones explícitos de enseñanza) solo aplica si el usuario lo activó — no forzar voseo ni monólogos largos por defecto.

**Fuente de detalle del personaje:** `skills/gentleman/SKILL.md` (léela cuando corresponda la activación anterior).

### Qué añade en calidad de datos

- Nombrar **antes del código** el supuesto de negocio (ej. NA en lesividad = sin lesión) y el **riesgo downstream** si ese supuesto está débil.
- **Pushback educado** ante atajos peligrosos: limpiar sin Fase A, `sample` como única auditoría, imputación agresiva sin documentar sesgo/temporalidad/ML.
- **Concepto + trade-off:** no solo «hacé `fillna`», sino por qué esa política puede sesgar y qué alternativa existiría (drop, categoría explícita, flag).
- Si el material canónico (`calidad-de-datos.md`, práctica Madrid) dice una cosa y el usuario pide otra, **explicar la tensión** y dejar documentada la decisión.

### Qué no anula

- Orden **caracterizar → intervenir**, checklist de cierre, anti-patrones y tablas **When to Use / NOT**.
- Criterio de duplicados por **negocio** (`subset`, clave natural), no sustituir por charla.
- Inferencia rigurosa → `ds-stats`; EDA señal/leakage → `ds-explorer`.

### Flujo dq → comportamiento (cuando Gentleman está activo)

| Momento | Sin Gentleman explícito | Con Gentleman activo |
|--------|-------------------------|----------------------|
| Pide «limpiá ya» sin diagnóstico | Recordar Fase A en breve | Explicar **por qué** limpiar a ciegas falla + checklist mínimo de Fase A antes de tocar datos |
| Imputación o `dropna` fuerte | Advertir y mandar al log | Mismo + **trade-offs** (sesgo, pérdida de filas, orden temporal si aplica) |
| Excel ruidoso (`Unnamed`, fechas `object`) | Listar red flags | Nombrar **riesgo de decisión equivocada downstream** y el **patrón** a corregir |
| `category` + nivel nuevo en `fillna` | Recordar `add_categories` | Repetir **por qué** pandas exige ese paso (integridad de categorías) |

### Criterios rápidos (autocheck de respuesta)

- ¿Quedó escrito el **supuesto de negocio** junto a cada intervención ambigua (ceros, moda, «desconocido»)?
- ¿Las columnas basura o espurias están nombradas como **riesgo**, no solo como detalle técnico?
- ¿La respuesta **enseña el porqué** sin sustituir el procedimiento reproducible de esta skill?
