# Resumen del TP para el equipo

> **Para:** Tomás, Agustín V., Francisco, Agustin P.
> **De:** Bautista
> **Estado al:** 14/06/2026

---

## TL;DR (30 segundos)

Durante la última semana trabajé con un asistente de IA (Claude Code) para terminar todo lo que faltaba del TP. **Los 4 entregables del 19/06 están listos**, distribuidos en **9 pull requests** (6 ya mergeadas a `main`, 3 abiertas esperando review). El modelo final es un **Random Forest tuneado que detecta 95% de los churners en test set**. Quedan dos cosas: revisar/mergear las PRs abiertas y **practicar la defensa oral**.

---

## Estado de los entregables (rúbrica)

| Entregable | Deadline | Estado | Dónde está |
|---|:---:|:---:|---|
| EDA con hipótesis | 12/06 | ✅ Entregado | `notebooks/01_EDA_Churn.ipynb` + `notebooks/01b_*.ipynb` |
| Código + GitHub + skills | 12/06 | ✅ Entregado | Repo entero + `.claude/skills/` |
| `decisions.md` v1 y v2 | 12/06 y 19/06 | ✅ 19 entradas | `decisions.md` |
| Notebook Modelado | 19/06 | ✅ En PR #7 | `notebooks/03_Modeling_Churn.ipynb` |
| Reporte ejecutivo PDF | 19/06 | ✅ En PR #8 | `reports/executive_summary.pdf` |
| Defensa oral 15 min | 19/06 | ✅ Material en PR #9 | `reports/defense_*.pdf` + `talking_points.md` + `glossary_defense.md` |

---

## Lo que se hizo, por fase

### Fase 1 — Investigación de anomalías del EDA (PR #2, mergeada)

**Problema:** dos de las 6 hipótesis del EDA original dieron contraintuitivo:
- **H3**: la inactividad supuestamente predecía churn, pero los datos mostraron lo **opuesto** (los churners ordenaron MÁS recientemente que los activos).
- **H4**: los churners reportaron satisfacción MÁS ALTA, no más baja.

**Qué hicimos:** un notebook de seguimiento (`01b_Investigacion_Anomalias_H3_H4.ipynb`) que **investigó por qué** y resolvió:

- **H3 era confundido por Tenure**: los clientes nuevos churnean masivo (50%) y por construcción tienen pocos días sin comprar. El verdadero patrón es **"compra reciente + queja"** = 39% churn vs 7% baseline.
- **H4 contraintuitivo es real pero débil**: el score auto-reportado tiene poder predictivo 25× menor que Tenure. Es ruidoso.

**Conclusión accionable**: la regla histórica "email a 15 días sin compra" no se sostiene empíricamente.

### Fase 2 — Exploración + adopción de feature engineering (PRs #3 y #4, mergeadas)

**Problema:** mejorar el feature set antes de modelar.

**Qué hicimos:**
- Evaluamos **7 candidatas** con criterio escrito ANTES de ver resultados (información mutua ≥ 0.005, redundancia ≤ 0.85, lift de Recall en RF).
- Solo 2 pasaron: **`OrdersPerMonth`** y **`CashbackPerMonth`** (tasas mensuales normalizadas por antigüedad).
- 5 fueron descartadas con razón cuantitativa (3 por baja MI, 2 porque empeoraban el RF).
- Las 2 adoptadas se sumaron al pipeline (`src/preprocessing.py`) y los 4 CSVs en `data/processed/` se regeneraron.

**Validación retrospectiva**: estas 2 features terminaron #1 y #3 en feature importance del modelo final. El protocolo funcionó.

### Fase 3 — Documentación y skills del equipo (PRs #5 y #6, mergeadas)

- `CLAUDE.md` actualizado con la estructura completa, instrucciones de setup, y workflow del equipo.
- Las **11 skills del data-science-kit** (de la cátedra de Agustín Chaud) bundleadas en `.claude/skills/` del repo. Antes había que instalarlas globalmente cada uno; ahora viajan con el repo.

### Fase 4 — Notebook de modelado (PR #7, **pendiente review**)

**Problema:** construir el modelo final que la rúbrica pide.

**Qué hicimos** (`notebooks/03_Modeling_Churn.ipynb`):
1. **Baseline obligatorio** (DummyClassifier) + 3 modelos: Decision Tree (obligatorio per rúbrica), Random Forest, XGBoost.
2. **StratifiedKFold k=5** con criterio del ganador **escrito antes** de ver resultados.
3. **Tuning bayesiano iterativo** (3 rondas): primero descartado (debajo del 2%), después detectamos boundaries pegados, expandimos rangos y cruzamos el umbral. Validamos overfitting (gap train-CV).
4. **Análisis SHAP** global + local (2 ejemplos).
5. **Audit de Complain** (riesgo de leakage): re-entrenamos el ganador con/sin Complain y medimos gap. Resultado: drop confirmado.

**Ganador final**: **RandomForest V1 tuneado**
- Recall CV: 0.8629 (vs 0.8431 default)
- **Recall test: 0.9526** (181 de 190 churners detectados)
- Precision test: 0.8117 (trade-off Recall↑/Precision↓ alineado con costo asimétrico)

### Fase 5 — Reporte ejecutivo PDF (PR #8, **pendiente review**)

**Problema:** producir el reporte de 4-6 páginas para el gerente comercial.

**Qué hicimos** (`reports/executive_summary.pdf`, 5 páginas):
- Estructura: TL;DR → Problema → 4 Hallazgos → Cómo funciona el modelo → 4 Recomendaciones → Limitaciones → Próximos pasos
- Sin tecnicismos: cada métrica traducida ("Recall 95% = detecta 95 de cada 100 churners")
- Recomendaciones con **verbo + objeto + impacto + responsable + plazo**
- Limitaciones honestas (no minimizadas)

### Fase 6 — Material para defensa oral (PR #9, **pendiente review, recién actualizada**)

**Problema:** preparar la presentación oral de 15 min + soporte visual.

**Qué hicimos** (al 14/06):
1. **Dos PDFs separados** (generados con IA de diseño + design brief):
   - `reports/defense_executive.pdf` (12 págs) → para gerente comercial
   - `reports/defense_technical.pdf` (19 págs) → para evaluador técnico
2. **`reports/talking_points.md`** → qué decir en cada slide, tiempos estimados, preguntas probables
3. **`reports/glossary_defense.md`** → los 13 términos de la rúbrica con definición técnica + analogía simple + ejemplo del proyecto

---

## El modelo final en una hoja

**Modelo:** `RandomForestClassifier(n_estimators=1469, max_depth=50, min_samples_leaf=3, max_features=0.978, class_weight='balanced', random_state=42)`

**Dataset usado para entrenar:** `data/processed/train_sin_complain.csv` (sin la variable Complain por riesgo de leakage no validable).

**Métricas en test set** (1126 clientes, evaluado dos veces — defaults + V1, declarado como limitación):

| Métrica | Valor | Lectura de negocio |
|---|:---:|---|
| **Recall** | **0.9526** | Detecta 95 de cada 100 churners reales |
| Precision | 0.8117 | De cada 10 alertas, 8 son reales |
| F1 | 0.8765 | — |
| PR-AUC | 0.9611 | — |
| AUC-ROC | 0.9917 | — |

**Top 3 features** (built-in importance):
1. `CashbackPerMonth` — adoptada en PR #4
2. `Tenure` — raw
3. `OrdersPerMonth` — adoptada en PR #4

---

## Decisiones clave (para defender en la oral)

Las 19 decisiones están en `decisions.md`. Las **6 más importantes** para defender:

| # | Decisión | Por qué |
|:---:|---|---|
| 1 | **Recall como métrica primaria** | Costo asimétrico: perder un churner cuesta varias veces más que un email innecesario. Accuracy engaña con desbalance. |
| 6 | **Split antes de imputar** | Para que las medianas de imputación no usen información del test (prevención de leakage). |
| 13 | **Resolución H3** (DSL se mantiene como feature) | La inversión del EDA era confundida por Tenure. El verdadero patrón es DSL × Complain. |
| 15 | **Adopción de FE per-tenure** | 2 features pasaron los gates (MI, redundancia, lift CV) y terminaron en top 3 de importance. |
| 18 | **RF V1 tuneado** (tras 3 rondas) | Cruzó el 2% del threshold solo después de auditar boundaries del search space. Validado con gap train-CV. |
| 19 | **Drop definitivo de Complain** | Audit cuantitativo: gap +0.79% en Recall no compensa el riesgo de leakage no validable. |

---

## Estructura final del repo

```
churn_tp/
├── CLAUDE.md                  # Documentación principal del proyecto
├── decisions.md               # 19 decisiones (template /add-decision)
├── recursos_github.md         # Referencias externas
├── requirements.txt           # Deps Python
├── RESUMEN_EQUIPO.md          # ← Este archivo
├── TP_Negocios_Consigna(1).pdf
│
├── .claude/
│   ├── commands/              # 5 skills específicas del TP (/add-decision, /ml-churn, etc.)
│   └── skills/                # 11 skills del data-science-kit
│
├── data/
│   ├── raw/                   # CSV original — NO modificar
│   └── processed/             # Outputs del pipeline (5 CSVs)
│
├── notebooks/
│   ├── 01_EDA_Churn.ipynb            # EDA + 6 hipótesis
│   ├── 01b_Investigacion_Anomalias_H3_H4.ipynb  # Follow-up al EDA
│   ├── 02_Preparacion_Datos.ipynb    # Pipeline anti-leakage
│   ├── 02b_Feature_Engineering_Exploracion.ipynb # Benchmark 7 candidatas
│   └── 03_Modeling_Churn.ipynb       # Modelo final + tuning + SHAP
│
├── src/
│   ├── preprocessing.py       # Funciones reutilizables fit-on-train
│   └── models/
│       ├── __init__.py
│       └── train.py           # Script CLI reproducible (RF V1)
│
├── reports/
│   ├── 01_hipotesis.md
│   ├── handoff_to_modeler.md         # Contexto técnico para reproducir
│   ├── modeling_results.md           # Tabla comparativa del modelado
│   ├── runs_log.csv                  # Log de runs en CV
│   ├── executive_summary.md/pdf      # Reporte ejecutivo (PR #8)
│   ├── defense_executive.pdf         # Deck ejecutivo (PR #9, 12 págs)
│   ├── defense_technical.pdf         # Deck técnico (PR #9, 19 págs)
│   ├── talking_points.md             # Qué decir en cada slide
│   ├── glossary_defense.md           # 13 términos rúbrica + analogías
│   ├── design_brief.md               # Spec usado para generar los PDFs de defensa
│   └── *.png                         # 9 gráficos del proyecto
│
└── models/                    # Modelos .pkl (gitignored)
```

---

## Cómo usar cada artefacto

### Para entender el proyecto desde cero
1. Leer **`CLAUDE.md`** (5 min) — overview completo
2. Leer **`reports/executive_summary.md`** (5 min) — hallazgos clave en lenguaje de negocio
3. Mirar **`reports/defense_executive.pdf`** (10 min) — todo en formato visual

### Para defender técnicamente
1. **`decisions.md`** es tu memoria — referenciá decisiones por número en la oral
2. **`reports/modeling_results.md`** — tabla comparativa exacta + auto-QA checklist
3. **`notebooks/03_Modeling_Churn.ipynb`** — pasos del modelado con outputs
4. **`reports/defense_technical.pdf`** — deck para evaluador técnico

### Para reproducir el modelo
```bash
conda activate churn_tp
python src/models/train.py
# Re-entrena RF V1 y serializa en models/RandomForest_V1_winner.pkl
```

### Para re-correr los notebooks
```bash
# Asumiendo conda env churn_tp activo
ENV_BIN=/opt/homebrew/Caskroom/miniconda/base/envs/churn_tp/bin

# Orden recomendado:
# 01 → 01b (opcional, ya está ejecutado) → 02 → 02b → 03
$ENV_BIN/jupyter nbconvert --to notebook --execute --inplace notebooks/02_Preparacion_Datos.ipynb
$ENV_BIN/jupyter nbconvert --to notebook --execute --inplace notebooks/03_Modeling_Churn.ipynb
```

### Para practicar la defensa oral
1. Leer **`reports/glossary_defense.md`** — practicar los 13 términos sin leer
2. Leer **`reports/talking_points.md`** — qué decir slide por slide
3. **Skill `/grill-me`** (en `.claude/skills/grill-me/`) — te interroga sin advertencia. Recomendado: 2-3 sesiones de 15 min antes del 19/06.

---

## Lo que falta al 14/06

| Pendiente | Cuándo | Quién |
|---|---|---|
| Mergear PR #7 (modelado) | Ya | Tomás (owner del repo) |
| Mergear PR #8 (reporte ejecutivo) | Ya | Tomás |
| Mergear PR #9 (material defensa, incluye los 2 PDFs nuevos) | Ya | Tomás |
| Practicar defensa oral con `/grill-me` | Antes del 19/06 | Equipo (cada uno) |
| Decidir quién presenta qué parte | Antes del 19/06 | Equipo (reunión) |
| Ensayo final | 17 o 18/06 | Equipo entero |

---

## Para preguntas

- Bautista: brios@itba.edu.ar
- Repo: github.com/tattas21/churn_tp
- Slack del equipo: [pendiente confirmar]
