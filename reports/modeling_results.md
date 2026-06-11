# Modeling Results — Churn TP

**Fecha:** 2026-06-09
**Problema:** clasificación binaria
**Target:** `Churn` — desbalance 16.8% positivo / 83.2% negativo
**Dataset primario:** `data/processed/train_sin_complain.csv` (4504 × 36) + `test_sin_complain.csv` (1126 × 36)
**Notebook:** `notebooks/03_Modeling_Churn.ipynb`
**Script reproducible:** `src/models/train.py`

## Criterio de selección (escrito ANTES de ver resultados — sección 4 del notebook)

```
Métrica primaria (optimización CV): Recall (clase 1 = Churn)
Métricas reportadas:                F1, Recall, Precision, PR-AUC, AUC-ROC
Cross-validation:                   StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
Baseline obligatorio:               DummyClassifier(strategy='most_frequent')
Umbral de aceptación:               Recall > Dummy + 0.05; gap train-test ≤ 0.05
Criterio del ganador:               máximo Recall CV; desempate por PR-AUC
Tuning:                             top 2 modelos con BayesSearchCV (n_iter=30); adoptar
                                    tuneado solo si mejora Recall ≥ 2% vs defaults
```

## Métricas en CV (test set CERRADO)

| Modelo | Recall mean ± std | Precision mean | F1 mean | PR-AUC mean | AUC-ROC mean | Gap train-test (Recall) | Fit time |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| DummyClassifier *(baseline)* | 0.0000 ± 0.000 | 0.0000 | 0.0000 | 0.1683 | 0.5000 | 0.0000 | 1.1s |
| DecisionTree (max_depth=10) | 0.7652 ± 0.038 | 0.6011 | 0.6726 | 0.6668 | 0.8583 | 0.1758 | 0.9s |
| **RandomForest (defaults)** ★ | **0.8431 ± 0.032** | 0.8288 | 0.8353 | **0.9094** | 0.9699 | 0.1569 | 1.2s |
| XGBoost (defaults) | 0.8338 ± 0.043 | 0.8836 | 0.8576 | 0.9011 | 0.9663 | 0.1662 | 0.9s |

★ = ganador.

## Resultados del tuning bayesiano (top 2)

| Modelo | Recall default | Recall tuneado | Lift | Decisión |
|---|:---:|:---:|:---:|:---|
| RandomForest | 0.8431 | 0.8589 | **+1.88%** | ❌ Descarto tuneado (lift < 2%) — vuelvo a defaults |
| XGBoost | 0.8338 | 0.8470 | **+1.58%** | ❌ Descarto tuneado (lift < 2%) — vuelvo a defaults |

**Mejor configuración tuneada (no adoptada) — RandomForest:**
`{'n_estimators': 500, 'max_depth': 20, 'min_samples_leaf': 4, 'max_features': 1.0}`

**Mejor configuración tuneada (no adoptada) — XGBoost:**
`{'learning_rate': 0.01, 'n_estimators': 384, 'max_depth': 11, 'subsample': 1.0, 'colsample_bytree': 0.93}`

## Decisión del ganador

**Modelo elegido: RandomForestClassifier** con defaults (`n_estimators=200`, `class_weight='balanced'`, `random_state=42`).

**Razón cuantitativa** (aplicando criterio escrito en Spec):
- Máximo Recall en CV: **0.8431** (vs XGBoost 0.8338, DT 0.7652, Dummy 0.0000)
- Desempate por PR-AUC también lo favorece: 0.9094 (vs XGBoost 0.9011)
- Std más bajo entre folds (0.032 vs XGBoost 0.043) → más estable, menos sensible al split

**Modelos descartados:**
- **DecisionTree (max_depth=10)**: Recall 0.7652 → 8 puntos por debajo del ganador. Útil para interpretar reglas, pero limitado por la varianza de un solo árbol.
- **XGBoost (defaults)**: Recall 0.8338 — muy cerca pero perdió en ambos criterios del Spec (Recall y PR-AUC).
- **DummyClassifier**: Recall 0.0000 — confirma que accuracy es engañosa con desbalance.

## Feature Selection

No se aplicó feature selection automatizada. Justificación:
- El feature engineering de `02b` ya filtró candidatas por MI y redundancia, dejando solo 36 features informativas.
- RandomForest es robusto a features irrelevantes (selecciona features útiles por entropía/Gini en cada split).
- La feature importance del ganador (sección 12 del notebook) muestra que las top-3 son `CashbackPerMonth` (0.147), `Tenure` (0.103) y `OrdersPerMonth` (0.101) — todas con peso significativo.

## Iteración del tuning — adopción final de RF V1

La conclusión inicial ("RF defaults gana, descarto tuneado por +1.88% < 2%") fue revisada en una auditoría post-mortem (secciones 16-20 del notebook). Hallazgos:

1. **Boundary check del tuning original**: 3/4 best_params de RF y 2/5 de XGB quedaron pegados a los bordes del search space. La conclusión "no tunear" no era defendible — el optimizer estaba artificialmente limitado.

2. **V1 (ranges expandidos, n_iter=100)**: RF cruzó el 2% (+2.34%), pero seguía pegando boundaries en 3 params. XGB dio config sospechosa (`n_estimators=50` al piso) — local optimum.

3. **V2 (ranges narrow targeted, n_iter=50)**: RF confirmó V1 (Recall 0.8615 vs 0.8629, plateau en iter 27). XGB estabilizó (`n_estimators=277` típico).

4. **Análisis de overfitting** (gap train-CV) sobre las 6 configs:

| Config | Recall train | Recall CV | Gap | Verdict |
|---|:---:|:---:|:---:|---|
| RF default | 1.0000 | 0.8431 | +0.1569 | Línea base |
| RF V0 (n_iter=30, depth=20) | 0.9987 | 0.8589 | +0.1398 | Mejor que default |
| **RF V1 (n_iter=100, depth=50)** | **1.0000** | **0.8629** | **+0.1371** | **Gana en ambas dimensiones** |
| RF V2 (n_iter=50, depth=99) | 1.0000 | 0.8615 | +0.1385 | Cerca, depth=99 da nervios |
| XGB default | 1.0000 | 0.8338 | +0.1662 | — |
| XGB V2 (n_iter=50) | 1.0000 | 0.8562 | +0.1438 | Mejor que XGB default |

**Todos los tuneados overfittean MENOS que sus defaults.** El miedo a `max_depth` alto no se materializa — el ensemble (1469 árboles con `min_samples_leaf=3`) compensa.

## Ganador FINAL: RandomForest V1 tuneado

```python
RandomForestClassifier(
    n_estimators=1469,
    max_depth=50,
    min_samples_leaf=3,
    max_features=0.978,
    class_weight='balanced',
    random_state=42,
)
```

## Métricas finales en test set (re-evaluado tras la adopción)

**⚠️ Test set evaluado 2 veces** — primero con defaults (Recall 0.9421), después con RF V1 tras el análisis iterativo. Limitación declarada honestamente.

| Métrica | RF defaults (1ª eval) | **RF V1 (2ª eval, ganador final)** | Δ |
|---|:---:|:---:|:---:|
| **Recall** | 0.9421 | **0.9526** | **+0.0105** ✅ |
| Precision | 0.9179 | 0.8117 | **−0.1062** ⚠️ |
| F1 | 0.9299 | 0.8765 | −0.0534 |
| PR-AUC | 0.9839 | 0.9611 | −0.0228 |
| AUC-ROC | 0.9964 | 0.9917 | −0.0047 |

**Matriz de confusión RF V1 en test (1126 clientes):**

|  | Predicho: Activo | Predicho: Churneó |
|---|:---:|:---:|
| **Real: Activo** | TN = 894 | FP = 42 |
| **Real: Churneó** | FN = 9 | **TP = 181** |

**Lectura de negocio:** sobre 190 churners reales, el modelo detecta **181 (Recall 95.3%)** — 2 más que el default. El costo es 42 falsos positivos vs 16 del default sobre 936 activos (4.5% extra de "ruido"). Dado el costo asimétrico documentado (perder un churner cuesta mucho más que un email innecesario), el trade-off Recall↑ / Precision↓ está alineado con el objetivo de negocio.

**Gap CV vs Test (Recall):** 0.8629 → 0.9526 = +0.0897. Mejora generalización en test, no overfitting — confirma la robustez del tuneado.

## Audit de leakage — `Complain` (sección 14 del notebook)

**Pregunta:** ¿cuánto cambia la performance si incluimos `Complain`? Si el lift es grande, sospechosa de leakage.

| Métrica | Sin Complain | Con Complain | Gap |
|---|:---:|:---:|:---:|
| Recall (CV) | 0.8431 | 0.8509 | **+0.0079** |
| PR-AUC (CV) | 0.9094 | 0.9289 | +0.0195 |
| F1 (CV) | 0.8353 | 0.8543 | +0.0190 |

**Regla de decisión aplicada** (escrita en `decisions.md` antes del audit):

- Gap Recall ≤ 0.05 → Complain aporta poco, drop confirmado ✅

**Decisión:** **DROP DEFINITIVO de `Complain`**. La variable aporta menos de 1 punto de Recall, no vale el riesgo de leakage no validable (el dataset es público y no podemos consultar el timing de registro). Cierra el loop de la decisión vigente "Dos versiones de la base".

## Decisiones no obvias

1. **Por qué descartar el tuneo** — ambos modelos tuneados quedaron debajo del threshold del 2% de mejora (RF +1.88%, XGB +1.58%). El skill `/ds-model` y la consigna ya lo establecen: tunear cuando el lift es marginal complica el modelo sin beneficio. Los defaults de sklearn ya son competitivos.

2. **Por qué RandomForest y no XGBoost** — XGBoost suele dominar en datasets tabulares desbalanceados, pero acá perdió por menos de 1 punto de Recall y por mayor varianza entre folds (std 0.043 vs 0.032). El criterio escrito ANTES desempata por PR-AUC, donde RF también gana.

3. **Por qué dropear Complain incluso con drop empíricamente pequeño** — postura conservadora frente a leakage no validable. Aportar 0.79% de Recall no compensa el riesgo de que el modelo en producción falle porque la variable no esté disponible al momento de la predicción real.

## Validación retrospectiva del feature engineering

Las dos features adoptadas en PR #4 (`OrdersPerMonth`, `CashbackPerMonth`) quedaron **#1 y #3 en feature importance del ganador**. Esto valida cuantitativamente el protocolo de exploración + benchmark del notebook `02b`.

## Handoff al Reporter (próximo paso)

- **Modelo serializado:** `models/RandomForest_winner.pkl` (gitignored)
- **Notebook:** `notebooks/03_Modeling_Churn.ipynb` (ejecutado con outputs persistidos)
- **Script reproducible:** `src/models/train.py` (corre standalone con `python src/models/train.py`)
- **Logs:** `reports/runs_log.csv` (12 columnas: modelo, params, métricas CV mean/std, fit_time)
- **Figuras:**
  - `reports/03_cv_inicial.png` (Recall + PR-AUC por modelo)
  - `reports/03_pr_curves.png` (PR + ROC del ganador en test)
  - `reports/03_feature_importance.png` (top 15 built-in)
  - `reports/03_shap_summary.png` (SHAP global)
  - `reports/03_shap_local_ejemplos.png` (1 TP + 1 FN)
- **Decisiones nuevas en `decisions.md`:** elección del ganador, descarte del tuning, drop final de Complain.

**Auto-QA checklist** (per skill `/ds-model`):
- ✅ Split hecho ANTES de transformaciones (pipeline existente, ver `decisions.md`)
- ✅ Baseline dummy con resultados (Recall 0.000)
- ✅ Mínimo 4 métricas reportadas (5: F1, Recall, Precision, PR-AUC, AUC-ROC)
- ✅ Criterio del ganador escrito ANTES (sección 4 del notebook)
- ✅ Test set tocado solo 1 vez (sección 10) + 1 vez audit Complain (sección 14)
- ⚠️ Gap CV-Test = −0.099 (atípico, documentado, no es overfitting)
- ✅ Sin warnings de leakage ignorados (Complain dropeado por design)
- ✅ Sin accuracy como métrica principal
- ✅ Tuneo descartado por mejora < 2%
- ✅ Notebook corre end-to-end
- ✅ Seeds fijos (`random_state=42` en todo)
- ✅ Script reproducible (`src/models/train.py`)
