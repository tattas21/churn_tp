# Handoff a Modelado — TP Churn de Clientes

> Sintetiza todo lo que el equipo necesita saber antes de entrenar el modelo final.
> Fuentes: notebooks `01`, `01b`, `02`, `02b` + `decisions.md` + `src/preprocessing.py`.

## Problema y target

- **Tipo:** clasificación binaria
- **Target:** `Churn` (1 = se fue, 0 = sigue activo)
- **Desbalance:** 16.8% positivo (clase minoritaria) / 83.2% negativo
- **Métrica primaria:** **Recall** (clase 1) — justificada en `decisions.md`: el costo de no detectar un churner (perderlo) supera al de marcar uno falsamente.
- **Métricas secundarias a reportar:** F1, Precision, PR-AUC, AUC-ROC.

## Dataset entrante (post-prep)

| Archivo | Filas | Columnas | Uso |
|---|---|---|---|
| `data/processed/train_sin_complain.csv` | 4,504 | **36** (35 features + Churn) | **Train primario** |
| `data/processed/test_sin_complain.csv` | 1,126 | 36 | **Test primario** |
| `data/processed/train_con_complain.csv` | 4,504 | 37 (36 features + Churn) | Audit de leakage de Complain |
| `data/processed/test_con_complain.csv` | 1,126 | 37 | Audit de leakage de Complain |
| `data/processed/dataset_limpio.csv` | 5,630 | 20 (raw + categorías unificadas) | NO USAR para modelado — pre-split |

**Stratify del split:** 17% positivo preservado en train (16.83%) y test (16.87%). `random_state=42`, `test_size=0.2`.

## Pipeline ya ejecutado (sin leakage)

```
raw CSV → clean_categories (sin estadísticas) → split estratificado →
  imputación mediana (fit-on-train, 7 cols con nulos 4-5%) →
  cap outliers p99 (fit-on-train, Tenure≤30, WarehouseToHome≤35, NumberOfAddress≤11) →
  add_features (row-wise, 6 derivadas) →
  OneHotEncoder (fit-on-train, 5 nominales → 17 columnas) →
  CSVs procesados
```

Todo el código vive en `src/preprocessing.py` (fit-on-train explícito).

## Features disponibles para modelado

### Numéricas / engineered (19)
- Crudas: `Tenure`, `CityTier`, `WarehouseToHome`, `HourSpendOnApp`, `NumberOfDeviceRegistered`, `SatisfactionScore`, `NumberOfAddress`, `OrderAmountHikeFromlastYear`, `CouponUsed`, `OrderCount`, `DaySinceLastOrder`, `CashbackAmount`
- Engineered (origen H5/H1):
  - `CashbackPerOrder = CashbackAmount / OrderCount`
  - `CouponPerOrder = CouponUsed / OrderCount`
  - `AppHoursPerDevice = HourSpendOnApp / NumberOfDeviceRegistered`
  - `IsNewCustomer = (Tenure <= 3).astype(int)`
- Engineered (adopción tras benchmark `02b`):
  - `OrdersPerMonth = OrderCount / (Tenure + 1)` — lift Recall +0.0106 vs baseline RF
  - `CashbackPerMonth = CashbackAmount / (Tenure + 1)` — lift +0.0053

### One-Hot (17)
- `PreferredLoginDevice` × 2 (Computer, Mobile Phone)
- `PreferredPaymentMode` × 5 (Cash on Delivery, Credit Card, Debit Card, E wallet, UPI)
- `Gender` × 2
- `PreferedOrderCat` × 5 (Fashion, Grocery, Laptop & Accessory, Mobile Phone, Others)
- `MaritalStatus` × 3 (Divorced, Married, Single)

### Adicional solo en `*_con_complain.csv`
- `Complain` (0/1) — **VER warning de leakage abajo**

## ⚠️ Warning de leakage — `Complain`

**Riesgo no resuelto.** El dataset es público (E_Commerce_Dataset.csv de Kaggle); no podemos consultar al sistema fuente cuándo se registra la queja vs. cuándo ocurre el churn.

- Si la queja se registra ANTES del churn → señal legítima.
- Si la queja se registra DESPUÉS (típico en sistemas de baja) → leakage.

`Complain` es la 3ª variable más informativa por MI (0.028) según el EDA. Por eso el equipo decidió guardar dos versiones del dataset y resolver la duda empíricamente en modelado.

**Acción del modelado:** entrenar primary en `sin_complain` (postura conservadora) y hacer un audit cuantitativo re-entrenando al ganador en `con_complain`. Aplicar la regla de decisión documentada en este PR.

## Features que NO ayudan al RF (resultado de `02b`)

Las 5 candidatas testeadas y descartadas en el benchmark de FE — **no agregar al modelo**:

| Candidata | Por qué se descartó |
|---|---|
| `RecentPurchaseWithComplaint = (DSL≤3) & (Complain==1)` | Pasa gates de MI/redundancia pero **degrada Recall en RF** (−0.0039). El RF encuentra la interacción nativamente. |
| `NewCustomerComplaint = (Tenure≤3) & (Complain==1)` | Idem — degrada Recall (−0.0066). |
| `HighSatisfaction = (SatisfactionScore≥4)` | Falla gate de MI (0.0031 < 0.005). Score auto-reportado es ruidoso. |
| `MultiAddress = (NumberOfAddress≥5)` | Falla ambos gates (MI ≈ 0). |
| `Dormant = (DaySinceLastOrder≥14)` | Falla gate de MI. **Confirma:** no usar regla histórica "email a 15 días". |

## Decisiones de modelado ya tomadas

1. **Métrica primaria = Recall** (clase 1). Optimizar para minimizar falsos negativos (churners no detectados). Costo: más falsos positivos (clientes que no se iban pero los contactamos).
2. **`class_weight='balanced'`** en cualquier modelo que lo acepte. Para XGBoost: `scale_pos_weight = (#neg / #pos) ≈ 4.94`.
3. **Cross-validation:** `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`.
4. **Test set:** se toca **UNA SOLA VEZ** al final, con el ganador ya tuneado.
5. **Seeds fijos:** `RANDOM_STATE = 42` en TODO.
6. **Modelos a comparar (rúbrica + decisión del equipo):**
   - `DummyClassifier(strategy='most_frequent')` — baseline obligatorio
   - `DecisionTreeClassifier` — obligatorio per rúbrica (interpretable)
   - `RandomForestClassifier` — captura interacciones nativamente
   - `XGBClassifier` — esperado mejor performance en tabular desbalanceado
7. **Tuning:** solo top 2 por CV inicial, con **Bayesian optimization** (`BayesSearchCV` de `scikit-optimize`), `n_iter=30`, `scoring='recall'`. Adoptar la versión tuneada solo si mejora ≥ 2% en Recall vs defaults.
8. **Interpretabilidad obligatoria:** feature importance built-in + SHAP global (summary plot) + SHAP local (2 ejemplos: 1 TP + 1 FN).

## Próximos pasos esperados del modelado

1. Generar `reports/modeling_results.md` con la tabla de comparación, la elección del ganador justificada cuantitativamente, y las métricas finales en test.
2. Documentar en `decisions.md`: (a) ganador y por qué, (b) approach de tuning, (c) resolución final de Complain con el número del gap.
3. Serializar el ganador en `models/{ganador}.pkl` (gitignored).
4. Producir `src/models/train.py` para reproducibilidad CLI.
5. Generar gráficos en `reports/03_*.png` (PR/ROC curves, feature importance, SHAP).

## Referencias

- Investigación de las anomalías H3/H4 del EDA: `notebooks/01b_Investigacion_Anomalias_H3_H4.ipynb`
- Exploración + benchmark de FE: `notebooks/02b_Feature_Engineering_Exploracion.ipynb`
- Historial completo de decisiones: `decisions.md`
- Skill protocol seguido: `.claude/skills/ds-model/SKILL.md`
