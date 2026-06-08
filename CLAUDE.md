# Churn TP — Contexto del proyecto

> Este archivo es la guía de referencia para cualquier persona (humana o asistente IA) que entre al proyecto. Asume que las PRs en revisión están mergeadas — ver el footer para el estado de las PRs.

## Problema de negocio

Predecir qué clientes de un e-commerce están por irse (churn) antes de que se vayan. Binary classification: `Churn = 1` (se fue) vs `Churn = 0` (sigue activo).

## Dataset

- **Archivo:** `data/raw/E_Commerce_Dataset.csv`
- **Filas:** 5,630 clientes
- **Target:** `Churn` (16.8% positivo → dataset desbalanceado)
- **Variables originales:** 20 columnas (tenure, comportamiento de compra, satisfacción, etc.)
- **Features tras prep:** 36 (19 numéricas/engineered + 17 One-Hot)

## Estructura del proyecto

```
churn_tp/
├── CLAUDE.md              # Este archivo
├── decisions.md           # Registro de decisiones (template /add-decision)
├── recursos_github.md     # Referencias externas (ML/EDA/negocio)
├── requirements.txt       # Dependencias Python
├── .gitignore             # Reglas de exclusión (Python/Jupyter/SO)
├── .claude/commands/      # Skills del proyecto (ver abajo)
├── data/
│   ├── raw/               # CSV original — NO modificar
│   └── processed/         # Outputs del pipeline:
│       ├── dataset_limpio.csv             # output del EDA (categorías unificadas)
│       ├── train_con_complain.csv         # 4504 × 37 con Complain
│       ├── test_con_complain.csv          # 1126 × 37 con Complain
│       ├── train_sin_complain.csv         # 4504 × 36 sin Complain
│       └── test_sin_complain.csv          # 1126 × 36 sin Complain
├── notebooks/
│   ├── 01_EDA_Churn.ipynb                          # EDA + 6 hipótesis + limpieza
│   ├── 01b_Investigacion_Anomalias_H3_H4.ipynb     # Follow-up al EDA: ¿por qué H3/H4 dieron contraintuitivo?
│   ├── 02_Preparacion_Datos.ipynb                  # Split, imputación, caps, FE, One-Hot
│   ├── 02b_Feature_Engineering_Exploracion.ipynb   # Evaluación de 7 candidatas de FE + benchmark RF
│   └── 03_Modeling_Churn.ipynb                     # (pendiente) Baseline + Random Forest + tuning
├── reports/               # Gráficos generados por los notebooks
│   ├── 01_hipotesis.md
│   ├── 01b_h3_investigacion.png
│   ├── 01b_h4_investigacion.png
│   ├── 02b_fe_correlaciones.png
│   └── 02b_fe_rf_benchmark.png
├── models/                # Modelos serializados (.pkl) — gitignored
└── src/
    └── preprocessing.py   # Funciones reutilizables (fit-on-train explícito)
```

## Pipeline de datos

```
raw CSV ──► clean_categories ──► dataset_limpio.csv ──► split (train/test estratificado)
                                                        │
            ┌───────────────────────────────────────────┘
            ▼
    fit_impute_values (train) ──► apply_impute (train, test)
    fit_outlier_caps (train)  ──► apply_caps   (train, test)
    add_features                 (row-wise, fila por fila)
    OneHotEncoder.fit (train) ──► transform   (train, test)
            │
            ▼
    data/processed/{train,test}_{con,sin}_complain.csv
```

**Regla de oro:** ningún estadístico se fitea con todo el dataset — todas las medianas, percentiles y encoders se ajustan **solo con train** y se aplican a test. La separación entre `fit_*` y `apply_*` en `src/preprocessing.py` hace esto explícito.

## Feature engineering (post-imputación, row-wise)

| Feature | Fórmula | Origen |
|---------|---------|--------|
| `CashbackPerOrder` | `CashbackAmount / OrderCount` | H5 (incentivo financiero) |
| `CouponPerOrder` | `CouponUsed / OrderCount` | intensidad de uso |
| `AppHoursPerDevice` | `HourSpendOnApp / NumberOfDeviceRegistered` | engagement |
| `IsNewCustomer` | `Tenure ≤ 3` | H1 (riesgo temprano) |
| `OrdersPerMonth` | `OrderCount / (Tenure + 1)` | benchmark en `02b` |
| `CashbackPerMonth` | `CashbackAmount / (Tenure + 1)` | benchmark en `02b` |

Todas son row-wise sobre datos imputados — no introducen leakage. Cinco candidatas adicionales (`RecentPurchaseWithComplaint`, `NewCustomerComplaint`, `HighSatisfaction`, `MultiAddress`, `Dormant`) se evaluaron en `02b` y se descartaron por baja MI o por degradar Recall.

## Decisiones clave

1. **Métrica principal: Recall** — minimizar falsos negativos (churners no detectados).
2. **Split estratificado** — `stratify=y`, `random_state=42`, `test_size=0.2`.
3. **Split ANTES de imputar** — medianas y percentiles fit solo en train.
4. **Imputación con mediana** (train) para las 7 columnas con nulos.
5. **Cap de outliers al percentil 99** (`Tenure`, `WarehouseToHome`, `NumberOfAddress`).
6. **One-Hot Encoding** para categóricas nominales (no LabelEncoder).
7. **`class_weight='balanced'`** en Random Forest — compensa el desbalance.
8. **Variable `Complain` en vigilancia** — base guardada con y sin ella para comparar.
9. **Resolución H3** (DSL) — la inversión del EDA viene de Tenure confound + interacción con Complain. `DSL` se mantiene como feature; modelos con interacciones (RF/GBM) preferidos.
10. **Resolución H4** (Score) — relación monótona pero MI 25× menor que Tenure. Score se mantiene con baja expectativa; descartar si no aparece en feature importance.
11. **Adopción de features per-tenure** — `OrdersPerMonth` y `CashbackPerMonth` mejoran el Recall del RF en +0.0106 y +0.0053 respectivamente.
12. **Descarte de 5 candidatas de FE** — bajo MI o degradación del Recall; la regla histórica de "email a 15 días sin compra" queda formalmente retirada.

Ver el detalle de cada decisión en `decisions.md`.

## Setup local

Pensado para macOS / Linux. Para Windows usar conda / pip equivalentes.

### Requisitos previos

- `git` + `gh` (GitHub CLI, para clonar y operar el repo)
- Miniconda o Anaconda

### Instalación

```bash
# 1. Clonar
gh repo clone tattas21/churn_tp ~/code/churn_tp
cd ~/code/churn_tp

# 2. Crear el env con conda-forge (evita el ToS de los canales default de Anaconda)
conda create -n churn_tp -c conda-forge --override-channels python=3.11 pip -y

# 3. Instalar dependencias
ENV_BIN=$(conda info --base)/envs/churn_tp/bin
$ENV_BIN/pip install -r requirements.txt
```

### Ejecutar los notebooks

```bash
# Desde la raíz del repo
conda activate churn_tp
jupyter notebook   # o jupyter lab
```

O sin activar el env explícitamente:

```bash
$ENV_BIN/jupyter notebook
```

### Re-ejecutar el pipeline desde cero

```bash
# Orden: 01 (EDA → dataset_limpio.csv) → 02 (prep → train/test CSVs)
$ENV_BIN/jupyter nbconvert --to notebook --execute --inplace notebooks/01_EDA_Churn.ipynb
$ENV_BIN/jupyter nbconvert --to notebook --execute --inplace notebooks/02_Preparacion_Datos.ipynb
```

> **Conocido:** `notebooks/01_EDA_Churn.ipynb` cell 4 hardcodea `DATA_PATH = '/Users/tomasattas/...'`. Hasta que se ajuste a path relativo (`../data/raw/E_Commerce_Dataset.csv`), cualquier colaborador necesita editar esa línea para correr el EDA localmente.

### Workflow de PRs

El proyecto es colaborativo (Tomás, Agustín, Bautista). Las pautas:

- Nunca pushear directo a `main`.
- Branch por tarea (`feat/...`, `eda/...`, `chore/...`, `docs/...`).
- Conventional Commits en español (`feat:`, `docs:`, `chore:`, `eda:`).
- PR con descripción de cambios + plan de test + links a decisiones / hallazgos relevantes.
- Una decisión que modifica el pipeline debe documentarse en `decisions.md` usando el template del skill `/add-decision`.
- Notebooks ya entregados (01, 02) **no se editan in-place**: si hay un follow-up, se crea un sufijo (ej. `01b_...`) para no romper diffs ni reescribir historia revisada.

## Skills disponibles

Los skills viven en `.claude/commands/` y son convenciones del proyecto — léelos antes de hacer trabajo del tipo correspondiente, no esperes que el usuario los invoque con `/`.

| Skill | Cuándo usar |
|-------|-------------|
| `/add-decision` | Agregar una entrada a `decisions.md` (título corto, Qué decidí en una oración, Por qué justificado por negocio, Alternativas como lista con guión, Consecuencias) |
| `/check-checkpoint` | Verificar el estado de los checkpoints del TP |
| `/eda-churn` | Guía para análisis exploratorio (distribuciones, hipótesis, correlaciones, outliers) |
| `/ml-churn` | Guía para modelado (comparación de modelos, FE, tuning, métricas, manejo de desbalance) |
| `/negocio-ecommerce` | Contexto de negocio (RFM, cohortes, impacto económico, retención) |

Ver `recursos_github.md` para los links de referencia externos.

## Estado actual del proyecto

| Fase | Estado |
|------|--------|
| EDA (01) | ✅ Completo — 6 hipótesis testeadas |
| Investigación de anomalías (01b) | ✅ Completo — H3 y H4 explicadas |
| Preparación de datos (02) | ✅ Completo — 36 features, 4 CSVs |
| Exploración de FE (02b) | ✅ Completo — 7 candidatas evaluadas, 2 adoptadas |
| Modelado (03) | ⏳ Pendiente — siguiente paso |

Las PRs originales que dejaron este estado: #1 (`.gitignore`), #2 (investigación H3/H4 + `01b`), #3 (exploración FE + `02b`), #4 (adopción `OrdersPerMonth` + `CashbackPerMonth`).
