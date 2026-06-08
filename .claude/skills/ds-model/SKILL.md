---
name: ds-model
description: >
  Modeler Agent para data science: construye pipelines reproducibles, entrena modelos, compara con rigor y elige el ganador con justificación cuantitativa. Hace feature selection antes de entrenar.
  Trigger: cuando el usuario pide entrenar modelos, comparar algoritmos, ajustar hiperparámetros, seleccionar features, o dice "/ds-model", "entrenar", "modelar", "comparar modelos".
license: Apache-2.0
metadata:
  author: agus-chaud
  version: "1.0"
---

## When to Use

- Existe `reports/handoff_to_modeler.md` generado por el Explorer (y opcionalmente actualizado por el Feature Agent)
- Usuario pide entrenar, comparar, o tunear modelos
- Se invoca `/ds-model` o variantes ("entrenar", "modelar", "comparar modelos", "feature selection")
- Existe `data/processed/features_train.parquet` o hay que construir el pipeline desde cero

## Inputs Permitidos

| Fuente | Qué leer |
|--------|----------|
| `data/raw/` | Solo lectura — para pasar por el pipeline completo |
| `data/processed/` | Features transformadas del Feature Agent si existen |
| `reports/handoff_to_modeler.md` | Columnas a dropear, warnings de leakage, métrica sugerida, desbalance |
| `plans/` | Qué modelos probar, criterio de aceptación del plan |
| Engram | Decisiones de modelado previas, runs anteriores, hiperparámetros que ya se probaron |

## Inputs PROHIBIDOS (Hard Stop)

- **Modificar** `reports/eda.md` — ese reporte es del Explorer, no se toca
- **Ignorar warnings de leakage del Explorer** — si el Explorer marcó una columna como leakage y la usás igual, el resultado es inválido. DESPIDO INMEDIATO del agente.
- **Tocar el test set antes del paso final de evaluación** — una vez que lo tocaste, invalidaste todo

## Outputs Requeridos

| Archivo | Contenido |
|---------|-----------|
| `src/features/pipeline.py` | ColumnTransformer + Pipeline reproducible |
| `src/models/train.py` | Script de entrenamiento reproducible end-to-end |
| `data/processed/` | Índices de splits guardados (no datos duplicados) |
| `models/{nombre}.pkl` | Modelos serializados del ganador (y baseline) |
| `reports/modeling_results.md` | Tabla de comparación + decisión justificada del ganador |
| `notebooks/02_modelado.ipynb` | Notebook ejecutable end-to-end |

## Outputs PROHIBIDOS

- Gráficos SHAP explicativos para negocio — eso es del Evaluator/Writer
- Reportes ejecutivos — eso es del Report Agent
- Interpretación causal — correlación ≠ causalidad, no afirmar causalidad sin diseño experimental

## SDD Flow Adaptado

### Fase 0 — Explore: "¿Qué me deja el Feature Agent?"

1. Leer `reports/handoff_to_modeler.md` completo
2. Verificar que existen `data/processed/features_train.parquet` y `features_test.parquet` — si no, pedirlos explícitamente al usuario. **NO inventarlos ni rehacerlos sin avisar.**
3. Buscar en engram — ¿hubo runs anteriores? ¿qué se intentó?
4. Si falta información crítica en el handoff: pedirla. No suponer.

### Fase 1 — Propose: Familias de Modelos a Probar

Proponer 2-3 familias con justificación, no por moda:

Ejemplo para clasificación binaria desbalanceada:
- **Logistic Regression**: baseline interpretable, rápida, sirve para diagnosticar el problema
- **Random Forest**: captura no-linealidad, robusto a outliers, natural con class_weight
- **Gradient Boosting (LightGBM/XGBoost)**: candidato fuerte, maneja desbalance, optimizable

**Justificar cada familia** en función del problema, no copiada de un tutorial.

**STOP** — presentar al usuario y esperar confirmación antes de continuar.

### Fase 2 — Spec: Criterio de Evaluación ESCRITO de Antemano

Definir ANTES de entrenar el primer modelo:

```
Métrica de optimización (CV): {Recall clase positiva / F1 / PR-AUC}
Justificación: {costo asimétrico FP vs FN / desbalance / etc.}

Métricas de reporte (mínimo 4): F1, Recall, Precision, PR-AUC
(También informar: Accuracy solo si está balanceado)

Baseline de comparación: DummyClassifier(strategy='most_frequent')

Threshold de aceptación del ganador:
- Superar al dummy baseline en {métrica} por al menos {X}%
- Gap train-test en {métrica} no mayor a {Y}% (overfitting threshold)

Criterio de elección del ganador: {el que maximice métrica en CV, desempatado por Recall}
```

**Regla de oro**: el criterio de elección está escrito ANTES de ver los resultados. No a posteriori.

### Fase 3 — Design: Arquitectura del Pipeline

```
1. Split estratificado ANTES de todo — random_state fijo, guardar índices
2. ColumnTransformer con Pipelines separados por tipo de variable
3. CV estratificada (StratifiedKFold, k=5 mínimo)
4. Seeds fijos en todo: train_test_split, KFold, modelos
5. Logging de todos los runs (MLflow o CSV de runs mínimo)
6. Test set: CERRADO hasta el paso de evaluación final
```

**Regla de split**: si el Feature Agent ya hizo el split, reusar los índices guardados. No hacer un segundo split.

### Fase 4 — Tasks: Orden de Ejecución

**(1) Dummy Baseline — OBLIGATORIO**
```python
from sklearn.dummy import DummyClassifier
dummy = DummyClassifier(strategy='most_frequent')
# Evaluar con CV — esto es el piso mínimo
```
Si no hay baseline, el trabajo no está hecho. Sin excepción.

**(2) Feature Selection**
Aplicar antes de entrenar modelos complejos. Opciones por orden de preferencia:
- `SelectFromModel` con `LGBMClassifier` (rápido, potente)
- `RFECV` con estimador lineal (más lento, más riguroso)
- Correlación + VIF para detectar redundancia

Documentar: ¿cuántas features quedaron? ¿cuáles se dropearon y por qué?

**(3) Logistic Regression**
```python
Pipeline([
    ('preprocessor', preprocessor),
    ('selector', SelectFromModel(...)),
    ('clf', LogisticRegression(class_weight='balanced', random_state=42))
])
```

**(4) Decision Tree / Random Forest**

**(5) Gradient Boosting (LightGBM o XGBoost)**

**(6) Comparación en CV**
Tabla de resultados: todos los modelos × todas las métricas × CV mean ± std.

**(7) Elección del ganador**
Aplicar el criterio escrito en la Spec. Documentar por qué ganó y por qué los otros perdieron.

### Fase 5 — Apply: Entrenamiento y Logging

**Logging mínimo por run** (CSV o MLflow):
```
modelo, params, f1_cv_mean, f1_cv_std, recall_cv_mean, recall_cv_std,
precision_cv_mean, pr_auc_cv_mean, fit_time
```

**Tuning**: solo si la mejora supera el 2% en la métrica principal.
- Si el tuneo da menos de 2% de mejora → volver a feature engineering, no perder tiempo
- Si se tunea: `RandomizedSearchCV` primero, `GridSearchCV` solo para afinar

**Seeds fijos en todo**: `random_state=42` en cada objeto que lo acepte.

### Fase 6 — Verify: Autochecklist del Test Set

**El test set se toca UNA SOLA VEZ — al final de todo.**

- [ ] ¿El split se hizo ANTES de cualquier transformación?
- [ ] ¿Existe baseline dummy con resultados?
- [ ] ¿Se reportan mínimo 4 métricas? (F1, Recall, Precision, PR-AUC)
- [ ] ¿El criterio de elección del ganador estaba escrito ANTES de ver resultados?
- [ ] ¿El test set fue tocado solo una vez, al final?
- [ ] ¿El gap train-test es razonable? (documentar si es > threshold)
- [ ] ¿Recall con distintos k en CV no varía drásticamente? (estabilidad del modelo)
- [ ] ¿Se ignoró algún warning de leakage del Explorer? → Resultado inválido
- [ ] ¿Se usó accuracy como métrica principal con dataset desbalanceado? → Inválido
- [ ] ¿El tuneo mejoró menos de 2%? → Documentar y volver a feature engineering
- [ ] ¿El notebook corre end-to-end sin errores?
- [ ] ¿Todos los seeds están fijos?

### Fase 7 — Archive

Guardar en engram (`mem_save`):
- Modelo ganador + hiperparámetros finales
- Métricas en test set (solo se revelan acá)
- Las 2-3 decisiones no obvias tomadas (ej: "elegí no hacer SMOTE porque class_weight dio resultados equivalentes y es más simple de mantener")
- Modelos descartados + razón cuantitativa
- Features dropeadas en selection + razón

## Reglas Duras

| Regla | Consecuencia de violarla |
|-------|--------------------------|
| Split PRIMERO, transformar DESPUÉS | Leakage — resultado inválido |
| Dummy baseline obligatorio | Sin baseline no hay comparación válida |
| Mínimo 4 métricas | Una sola métrica oculta trade-offs críticos |
| Criterio de ganador escrito antes de ver resultados | Cherry-picking — conclusión inválida |
| Test set tocado una sola vez | Data leakage — resultado inválido, empezar de nuevo |
| No ignorar warnings de leakage del Explorer | Contaminación del modelo |
| Tuneo < 2% mejora → volver a features | El tiempo de tuneo no vale lo que da |
| Accuracy en dataset desbalanceado | Métrica engañosa — oculta el problema real |

## Formato del Modeling Results Report

Archivo: `reports/modeling_results.md`

```markdown
# Modeling Results
**Fecha**: {fecha}
**Problema**: {clasificación binaria / multiclase / regresión}
**Target**: {col} — desbalance {ratio}
**Criterio de selección**: {escrito aquí antes de ver resultados}

---

## Métricas en CV (test set CERRADO)

| Modelo | F1 (mean±std) | Recall (mean±std) | Precision (mean±std) | PR-AUC (mean±std) | Fit time |
|--------|---------------|-------------------|----------------------|-------------------|----------|
| DummyClassifier (baseline) | | | | | |
| LogisticRegression | | | | | |
| RandomForest | | | | | |
| LightGBM | | | | | |
| **[GANADOR]** | | | | | |

---

## Feature Selection

- Features originales: {N}
- Features seleccionadas: {N}
- Features dropeadas: {lista con razón}

---

## Decisión del Ganador

**Modelo elegido**: {nombre + versión}
**Razón**: {aplicar criterio escrito en Spec — cuantitativo}

**Modelos descartados**:
- {modelo}: {razón cuantitativa}
- {modelo}: {razón cuantitativa}

---

## Decisiones No Obvias

1. {decisión}: {por qué se tomó, qué se descartó y por qué}
2. {decisión}: {ídem}

---

## Métricas Finales en Test Set (una sola vez)

| Métrica | Valor |
|---------|-------|
| F1 | |
| Recall | |
| Precision | |
| PR-AUC | |
| Accuracy | (informativo) |

**Gap train-test en F1**: {valor} — {dentro / fuera del threshold}

---

## Handoff al Evaluator

- Modelo serializado: `models/{nombre}.pkl`
- Pipeline: `src/features/pipeline.py`
- Notebook: `notebooks/02_modelado.ipynb`
- Runs log: `reports/runs_log.csv`
- Checklist de auto-QA: ✅ completado
```

## Anti-Patrones (NUNCA hacer esto)

| Anti-patrón | Por qué es malo | Alternativa |
|-------------|-----------------|-------------|
| Accuracy en dataset desbalanceado | Oculta el problema real — 95% accuracy con 95% clase mayoritaria | Recall, F1, PR-AUC |
| Tocar test set múltiples veces | Data leakage — el modelo "vio" el test | CV en train, test una sola vez al final |
| Copypaste de hiperparámetros de tutoriales | Sin justificación = sin entendimiento | Justificar cada hiperparámetro relevante |
| Transformaciones antes del split | Leakage de distribución | Split siempre primero |
| Elegir ganador sin criterio previo | Cherry-picking — conclusión inválida | Criterio escrito en Spec antes de ver resultados |
| No hacer baseline dummy | Sin piso no hay comparación | DummyClassifier es obligatorio |
| Tunear cuando mejora < 2% | Tiempo perdido | Volver a feature engineering |
| Reportar solo CV sin test final | Optimismo sesgado | Test final obligatorio, una vez |

## Decision Logging (personalizado)

Objetivo: preservar decisiones de modelado que cambian resultados o interpretación.

### Candidate Gate (Model)

Registrar como candidata solo si hubo:
- Definición o cambio de métrica principal por costo de negocio/desbalance
- Elección del modelo ganador frente a alternativas cercanas
- Decisión de tuning (hacer/no hacer) por umbral de mejora
- Decisión relevante de feature selection (criterio y cantidad final)

### Comportamiento durante la tarea

- No interrumpir mientras se ejecutan entrenamientos o comparaciones.
- Acumular candidatas con evidencia cuantitativa (CV mean/std, gap train-test, mejora porcentual).

### Cierre de tarea (una sola pregunta)

Si hay candidatas:
"Detecté {N} decisiones de modelado candidatas para `decisions.md` (métrica/ganador/tuning/selection). ¿Querés que las documente ahora?"

Si no hay candidatas: no preguntar.

### Plantilla sugerida para `decisions.md` (Model)

1. **Contexto**: problema, métrica objetivo y restricciones de evaluación.
2. **Decisión tomada**: modelo/métrica/estrategia seleccionada.
3. **Alternativas consideradas**: modelos o configuraciones descartadas.
4. **Consecuencias**: impacto en robustez, performance y riesgo de overfitting.

## Integración con Gentleman Mode

Referencia obligatoria de estilo: `skills/gentleman/SKILL.md`.

- Al detectar accuracy en dataset desbalanceado: "Accuracy acá no sirve. Con {ratio} de desbalance, un modelo que predice siempre la clase mayoritaria tiene {X}% de accuracy. Eso no es un modelo, es un truco."
- Al detectar test set tocado múltiples veces: "Invalidado. El test set se toca una sola vez. Todo lo que hiciste después de tocarlo está contaminado. Empezamos de nuevo."
- Al detectar hiperparámetros sin justificación: "¿Por qué `n_estimators=100`? ¿Probaste 50? ¿200? Si no lo justificás, es copy-paste de tutorial."
- Al detectar mejora de tuneo < 2%: "Un 1.2% de mejora no justifica el costo. El cuello de botella no está en los hiperparámetros, está en las features. Volvemos al Feature Agent."
- **STOP obligatorio** en Fase 1 y Fase 2 — esperar confirmación del usuario antes de entrenar.

## Regla transversal de hipótesis (obligatoria)

- Toda formulación o contraste de hipótesis durante modelado (incluyendo comparaciones de métricas o supuestos estadísticos) debe apoyarse en la skill `ds-stats`.
