# Decisions.md — TP Churn de Clientes

Registro de cada decisión importante del proyecto.

---

## Decisión — Elección de métrica principal

1. **Qué decidí:** Usar Recall como métrica principal (no Accuracy)
2. **Por qué:** El dataset tiene class imbalance (83% vs 17%). Un modelo que predice "nadie churna" tendría 83% de accuracy pero sería completamente inútil. Queremos detectar la mayor cantidad posible de clientes que van a irse (minimizar falsos negativos), aunque eso implique más falsas alarmas.
3. **Alternativas que descarté:**
   - Accuracy: engañosa con clases desbalanceadas
   - Precision sola: priorizaría no molestar a clientes que no iban a irse, pero a costo de perder detecciones reales
4. **Consecuencias:** Habrá falsos positivos (clientes que no iban a irse pero los contactamos igual). El costo de contactar un cliente activo (un email, un descuento innecesario) es mucho menor que perder un cliente churneado.

---

## Decisión — Tratamiento de la variable Complain

1. **Qué decidí:** Mantenerla en el EDA pero marcarla con alerta de leakage para la etapa de modelado
2. **Por qué:** No tenemos certeza de si la queja se registra antes o después del churn. Si se registra después, es información que no estaríamos disponible al momento de predecir.
3. **Alternativas que descarté:** Eliminarla directamente del análisis (perdemos señal potencialmente valiosa)
4. **Consecuencias:** Necesitamos confirmar el timing con el equipo de datos antes de incluirla en el modelo. Si el dato no está disponible, la excluimos.

---

## Decisión — Unificación de categorías inconsistentes

1. **Qué decidí:** Unificar la misma categoría escrita de varias formas, en 3 columnas:
   - `PreferredPaymentMode`: 'CC' → 'Credit Card', 'COD' → 'Cash on Delivery' (7 → 5 valores)
   - `PreferredLoginDevice`: 'Phone' → 'Mobile Phone' (3 → 2 valores)
   - `PreferedOrderCat`: 'Mobile' → 'Mobile Phone' (6 → 5 valores)
2. **Por qué:** Son la misma categoría escrita distinto. Si no se unifican, el modelo las trata como separadas y aprende patrones incorrectos / genera columnas one-hot redundantes.
3. **Alternativas que descarté:** Mantenerlas separadas (ruido sin información real).
4. **Consecuencias / dónde vive (sin duplicar el paso):** La limpieza se ejecuta **una sola vez, en el EDA** (`01_EDA_Churn.ipynb`), que detecta los duplicados, llama a `src/preprocessing.clean_categories()` y **guarda el resultado en `data/processed/dataset_limpio.csv`**. La preparación (`02_Preparacion_Datos.ipynb`) **carga ese archivo ya limpio** y no vuelve a limpiar. La lógica vive en `src/preprocessing.py` (definida una vez), el paso se corre una vez (EDA), y la prep consume el output.

---

## Decisión — Manejo de outliers (Tenure=60, WarehouseToHome=126)

1. **Qué decidí:** Mantener para el EDA, evaluar en modelado
2. **Por qué:** Los outliers extremos (Tenure=60 cuando la mayoría está en 0-31, distancia=126 cuando la mayoría está en 5-36) probablemente son errores de carga. En el EDA los documentamos. En el modelo evaluaremos si eliminarlos o cap-earlos al percentil 99.
3. **Alternativas que descarté:** Eliminar directamente (podría descartar clientes reales con características válidas)
4. **Consecuencias:** Pueden generar ruido en los modelos lineales. Los árboles de decisión son más robustos a outliers.

---

## Decisión — Split estratificado train/test

1. **Qué decidí:** train_test_split con stratify=y, test_size=0.2, random_state=42
2. **Por qué:** Con solo 17% de churn, un split aleatorio puede desbalancear aún más las proporciones entre train y test. Estratificar garantiza que ambos subsets tengan ~17% de churn. random_state=42 hace el experimento reproducible.
3. **Alternativas que descarté:** Split aleatorio puro (riesgo de distribuciones distintas)
4. **Consecuencias:** Los resultados son reproducibles y los subsets son representativos de la distribución real.

---

## Decisión — Orden del pipeline: split ANTES de imputar (evitar leakage)

1. **Qué decidí:** Hacer el split train/test primero, y recién después calcular medianas y percentiles **solo con train**, aplicándolos a test.
2. **Por qué:** Si imputamos o cap-eamos con estadísticas de todo el dataset, el test "ve" información del train y viceversa (data leakage). El test debe simular datos nunca vistos.
3. **Alternativas que descarté:** Imputar sobre el dataset completo antes de separar (más simple pero infla las métricas — era lo que hacía la versión vieja del notebook de modelado).
4. **Consecuencias:** Las medianas/percentiles se guardan como artefactos del train. La lógica reutilizable vive en `src/preprocessing.py` (fit-on-train explícito).

---

## Decisión — Imputación de nulos con mediana

1. **Qué decidí:** Imputar las 7 columnas numéricas con nulos (4.5–5.5% cada una) usando la mediana calculada en train.
2. **Por qué:** Todas tienen <6% de nulos, así que imputar conserva las filas sin distorsionar. La mediana es robusta a los outliers que detectamos.
3. **Alternativas que descarté:** Eliminar filas (perderíamos ~25% de la base por acumulación); imputar con la media (sensible a outliers).
4. **Consecuencias:** 0 nulos en train y test tras la imputación.

---

## Decisión — Cap de outliers al percentil 99 (resuelve la decisión previa)

1. **Qué decidí:** Cap-ear (winsorizar) `Tenure`, `WarehouseToHome` y `NumberOfAddress` al percentil 99 calculado en train, en lugar de eliminar filas.
2. **Por qué:** Los valores extremos (probables errores de carga) generan ruido en modelos lineales. Cap-ear reduce el ruido sin descartar clientes.
3. **Alternativas que descarté:** Eliminar filas (pierde clientes); dejarlos (ruido en modelos lineales).
4. **Consecuencias:** Resuelve la decisión previa de outliers, que quedaba "a evaluar en modelado". Caps en train: Tenure≤30, WarehouseToHome≤35, NumberOfAddress≤11.

---

## Decisión — One-Hot Encoding para categóricas nominales

1. **Qué decidí:** Usar One-Hot Encoding (fit en train, `handle_unknown='ignore'`) para las 5 nominales: PreferredLoginDevice, PreferredPaymentMode, Gender, PreferedOrderCat, MaritalStatus.
2. **Por qué:** No tienen orden natural. LabelEncoder les impondría un orden falso (ej. Single<Married<Divorced), que los modelos pueden interpretar como una jerarquía inexistente.
3. **Alternativas que descarté:** LabelEncoder (era lo que usaba el notebook de modelado viejo — incorrecto para nominales).
4. **Consecuencias:** Pasamos de 19 a 34 features. CityTier y SatisfactionScore se dejan como numéricas porque sí son ordinales.

---

## Decisión — Feature engineering basado en las hipótesis del EDA

1. **Qué decidí:** Crear 4 features row-wise: `CashbackPerOrder`, `CouponPerOrder`, `AppHoursPerDevice`, `IsNewCustomer` (Tenure≤3).
2. **Por qué:** Derivan de las hipótesis confirmadas (H1 tenure, H5 cashback) y capturan intensidad de uso/engagement que las variables crudas no expresan directamente.
3. **Alternativas que descarté:** `IsSingle` (redundante con el One-Hot de MaritalStatus).
4. **Consecuencias:** Validado en el modelado — `IsNewCustomer` quedó como 2ª variable más importante y `CashbackPerOrder` entre las top 5 del Random Forest.

---

## Decisión — Dos versiones de la base (con y sin Complain)

1. **Qué decidí:** Guardar la base procesada en dos versiones (`*_con_complain.csv` y `*_sin_complain.csv`) y dejar un toggle `USAR_COMPLAIN` en el notebook de modelado.
2. **Por qué:** `Complain` es señal fuerte (quedó 3ª en importancia) pero con riesgo de leakage no confirmado. Tener ambas versiones permite medir cuánto del rendimiento depende de esa variable.
3. **Alternativas que descarté:** Decidir a ciegas incluirla o excluirla.
4. **Consecuencias:** El modelado puede comparar métricas con/sin Complain antes de la decisión final.

---

## Decisión — Estructura: preparación separada del modelado

1. **Qué decidí:** Separar la preparación (`02_Preparacion_Datos.ipynb` + `src/preprocessing.py`) del modelado (`03_Modeling_Churn.ipynb`), que ahora consume `data/processed/`.
2. **Por qué:** La versión anterior mezclaba prep (con leakage) y modelado en un solo notebook. Separar deja la lógica reutilizable, testeable y sin duplicar.
3. **Alternativas que descarté:** Mantener todo en un notebook de modelado.
4. **Consecuencias:** El notebook de modelado viejo se renumeró de `02` a `03`.

---

## Decisión — Resolución H3: DaySinceLastOrder se mantiene

1. **Qué decidí:** Conservar `DaySinceLastOrder` como feature del modelo y descartar la regla de negocio original de enviar email de reactivación a los 15 días sin compra.
2. **Por qué:** La inactividad por sí sola no identifica clientes en riesgo — quienes más churnean son los clientes nuevos, que por construcción tienen pocos días sin comprar. El verdadero patrón de riesgo para retención es "compra reciente con queja sin resolver" (38.9% churn vs 7.1% en el escenario opuesto), no la inactividad sostenida. La variable sí aporta al modelo cuando se combina con Tenure y Complain (ver `01b_Investigacion_Anomalias_H3_H4.ipynb`: tasa de nulos sin sesgo p=0.78, información mutua 0.0262 — tercera más alta del set).
3. **Alternativas que descarté:**
   - Dropear `DaySinceLastOrder` por su relación contraintuitiva en el EDA.
   - Mantener la regla de "reactivación a los 15 días" como acción de negocio.
4. **Consecuencias:** El modelo debe poder capturar interacciones DSL × Complain × Tenure — eso prioriza modelos basados en árboles (Random Forest, GBM); en caso de usar un modelo lineal hay que crear features de interacción explícitas. La acción de negocio recomendada cambia: alertas sobre quejas sin resolver en clientes recientes, no campañas por inactividad.

---

## Decisión — Resolución H4: SatisfactionScore queda en evaluación

1. **Qué decidí:** Incluir `SatisfactionScore` en el set inicial de features con expectativa baja, y descartar la variable si no aparece en el top-10 de feature importance del modelo final.
2. **Por qué:** El score auto-reportado se mueve con el churn de forma estadísticamente significativa pero su poder de discriminación es ínfimo (información mutua 25× menor que Tenure). Eso indica que el indicador no captura las verdaderas razones de salida (precio, conveniencia, competencia) y por lo tanto no debería guiar acciones de retención por sí solo. Mantenerlo como candidato deja que el modelo valide empíricamente si encuentra alguna utilidad marginal sin comprometer la estrategia (ver `01b_Investigacion_Anomalias_H3_H4.ipynb`: la escala no está invertida, dif. con/sin queja = -0.095, casi nulo).
3. **Alternativas que descarté:**
   - Dropear inmediatamente sin validar contra el modelo.
   - Transformar a binaria `HighSatisfaction = (score >= 4)` — queda como opción si el score crudo no aporta en el modelo final.
4. **Consecuencias:** Ninguna acción de negocio de retención se construye sobre este indicador hasta validar con el equipo de datos cómo y cuándo se recolecta el score. Si el modelo final lo descarta, la variable sale del pipeline de producción.

---

## Decisión — Adopción de features per-tenure (OrdersPerMonth, CashbackPerMonth)

1. **Qué decidí:** Agregar `OrdersPerMonth = OrderCount / (Tenure + 1)` y `CashbackPerMonth = CashbackAmount / (Tenure + 1)` al pipeline de feature engineering.
2. **Por qué:** Ambas capturan la **tasa por mes** de engagement (órdenes) y de incentivo recibido (cashback), una señal de negocio que las variables crudas mezclan con la antigüedad del cliente. En el benchmark del notebook `02b` cada una mejora el Recall del Random Forest sobre el baseline (5-fold CV: +0.0106 y +0.0053 respectivamente, con MI 0.118 y 0.148 — la segunda mayor del set). Convertir el volumen total en una tasa hace explícita la pregunta "este cliente compra/recibe poco por antigüedad o realmente está desenganchado", que es la pregunta accionable para retención.
3. **Alternativas que descarté:**
   - Adoptar las 7 candidatas evaluadas: el lift adicional (+0.0053 de Recall sobre adoptar solo estas dos) no justifica duplicar la complejidad del feature set.
   - Mantener solo las features crudas (`OrderCount`, `CashbackAmount`, `Tenure`) y dejar que el RF infiera la tasa: el modelo lo intenta pero pierde ~1 punto de Recall por hacerlo implícito.
4. **Consecuencias:** Se extiende `add_features()` en `src/preprocessing.py` para crear ambas columnas tras imputar. Se regeneran los 4 CSVs en `data/processed/` (con/sin Complain × train/test). El feature count pasa de 34 a 36. El notebook 03 de modelado consume las versiones nuevas. Ambas features son row-wise sobre datos ya imputados — sin leakage (ver auditoría en el PR de adopción).

---

## Decisión — Descarte de 5 candidatas de feature engineering

1. **Qué decidí:** No adoptar `RecentPurchaseWithComplaint`, `NewCustomerComplaint`, `HighSatisfaction`, `MultiAddress` ni `Dormant` tras evaluarlas en `notebooks/02b_Feature_Engineering_Exploracion.ipynb`.
2. **Por qué:** Para tres de ellas (`HighSatisfaction`, `MultiAddress`, `Dormant`) la información mutua con el target queda debajo del piso de 0.005 — no aportan señal incremental al modelo. Para las otras dos (interacciones `DSL × Complain` y `Tenure × Complain`) los gates pasan pero el Recall del Random Forest **empeora** al agregarlas (−0.0039 y −0.0066 en 5-fold CV): el modelo ya las descubre vía splits anidados y la versión pre-computada solo introduce varianza. Operativamente, esto significa que la regla de negocio histórica "campaña de reactivación a los 15 días sin compra" (que `Dormant` formalizaba) no se sostiene con la evidencia disponible.
3. **Alternativas que descarté:**
   - Adoptar las 7 candidatas en bloque por el lift agregado (+0.0159) — la diferencia respecto al shortlist de 2 features cae dentro del std del benchmark (~0.025) y no compensa la complejidad.
   - Forzar la inclusión de las interacciones pre-computadas "por interpretabilidad" — pierde validez si el modelo final tiene peor performance.
4. **Consecuencias:** El feature set adoptado en el pipeline es 34 + 2 = 36 columnas, sin las interacciones explícitas. La regla de negocio "email a 15 días sin compra" queda formalmente retirada. `SatisfactionScore` permanece como ordinal sin binarizar.

---

## Decisión — Random Forest como familia ganadora

> **Nota:** esta decisión define la **familia** del modelo (RF vs DT vs XGB). La **configuración exacta** dentro de RF (defaults vs tuneado) se resuelve en la decisión siguiente tras una iteración del tuning.

1. **Qué decidí:** Adoptar la familia **`RandomForestClassifier`** como modelo de producción para predecir churn, en lugar de Decision Tree o XGBoost.
2. **Por qué:** Random Forest tuvo el mejor Recall en cross-validation (0.8431 ± 0.032 en defaults) — la métrica que la consigna establece como primaria por el costo asimétrico de perder un churner. XGBoost quedó muy cerca (0.8338) pero con mayor varianza entre folds (std 0.043 vs 0.032), y perdió también el desempate por PR-AUC (0.9094 vs 0.9011). El Decision Tree, aunque obligatorio per rúbrica y útil para interpretar reglas, quedó 8 puntos por debajo (0.7652). RF combina lo mejor de ambos: captura interacciones nativamente (como confirma el análisis de feature engineering en `02b`) y promedia varianza con su naturaleza de ensemble — exactamente lo que un dataset desbalanceado y con interacciones (DSL × Complain × Tenure documentadas en `01b`) necesita.
3. **Alternativas que descarté:**
   - **XGBoost (familia)**: el contendiente más cercano (Recall 0.8338), descartado por mayor varianza entre folds y peor PR-AUC. Quedó como segunda opción en caso de que RF mostrara problemas.
   - **Decision Tree**: descartado por performance — sirve para visualización pero su Recall es 8 puntos inferior. Hubiera ganado si la rúbrica priorizara interpretabilidad sobre detección.
   - **Logistic Regression**: no entró en la comparación porque tras el feature engineering del notebook `02b` el modelo se beneficia de capturar interacciones (DSL × Complain × Tenure), algo que un modelo lineal no captura sin pre-computar todas las interacciones manualmente.
4. **Consecuencias:** La familia queda fijada en RF. La configuración exacta dentro de RF (defaults vs tuneado) se decide en la siguiente entrada tras un análisis iterativo del tuning. Las dos features adoptadas en la decisión previa (`CashbackPerMonth`, `OrdersPerMonth`) quedaron #1 y #3 en feature importance, validando retrospectivamente el trabajo de FE.

---

## Decisión — Adopción final de Random Forest V1 tuneado tras iteración del tuning

> **Nota:** esta decisión REVISA la conclusión inicial del tuning (sección 8 del notebook). La decisión vigente es la siguiente.

1. **Qué decidí:** Adoptar **Random Forest V1 tuneado** (`n_estimators=1469, max_depth=50, min_samples_leaf=3, max_features=0.978, class_weight='balanced'`) como modelo final, tras una auditoría iterativa que reveló que la primera ronda de tuning estaba artificialmente limitada por search spaces demasiado estrechos.
2. **Por qué:** La decisión inicial era "no tunear" porque ambos modelos quedaron debajo del 2% threshold (RF +1.88%, XGB +1.58%). Pero una auditoría post-mortem mostró que **3/4 de los best_params de RF estaban pegados a los límites del search space original** — el optimizer quería ir más allá pero no podía. Re-corriendo con ranges expandidos (n_iter=100) RF cruzó el 2% (+2.34%), y una tercera ronda con ranges narrow targeteados (n_iter=50) confirmó el resultado (plateau en iter 27). Análisis de overfitting: **el RF V1 tuneado overfittea MENOS que el default** (gap train-CV 0.1371 vs 0.1569). En test set el ganador detecta **181 de 190 churners reales (Recall 95.3%, +0.0105 vs default)**, con costo de 42 falsos positivos vs 16 — trade-off alineado con el costo asimétrico documentado en la decisión #1 (perder un churner cuesta mucho más que un email innecesario).
3. **Alternativas que descarté:**
   - **Mantener defaults** (decisión original): rechazada porque el análisis de boundaries reveló que la conclusión "tuning no sirve" estaba sesgada por search spaces inadecuados. Adoptar el tuneado correcto es la conclusión defendible con los datos en mano.
   - **Adoptar RF V2** (n_iter=50 narrow, Recall CV 0.8615): muy cercano a V1 (0.8629) pero `max_depth=99` es más agresivo sin ganancia. V1 con `max_depth=50` da el mismo resultado con configuración más conservadora.
   - **Adoptar XGBoost V2 tuneado** (Recall CV 0.8562): config más "típica" de XGB, pero Recall menor que RF V1. Perdió en la métrica primaria.
   - **No re-evaluar en test set** para mantener la regla "una sola evaluación": rechazado porque adoptar un modelo sin validar en test es peor higiene que documentar transparentemente la segunda evaluación.
4. **Consecuencias:** El modelo serializado vive en `models/RandomForest_V1_winner.pkl` (gitignored). El script `src/models/train.py` está actualizado a la config V1. El test set quedó **evaluado dos veces** (defaults + V1) — declarado como limitación en `notebook 03` sección 20. Recomendación a futuro: si el modelo se mueve a producción a largo plazo, definir un nuevo holdout 100% intocado para validación. Trade-off explícito: el modelo V1 sube Recall +1.05 pp pero baja Precision −10.62 pp respecto a defaults — alineado con el costo asimétrico declarado en la decisión #1, pero requiere comunicación clara al equipo comercial sobre el aumento de falsas alarmas (42 vs 16 sobre 936 clientes activos).

---

## Decisión — Drop definitivo de `Complain` por riesgo de leakage no validable

1. **Qué decidí:** **Eliminar `Complain` del modelo en producción**, cerrando la decisión previa "Dos versiones de la base" que la dejaba pendiente de validación.
2. **Por qué:** El dataset es público (E_Commerce_Dataset.csv de Kaggle) y no podemos consultar al sistema fuente para confirmar si la queja se registra antes o después de que el cliente decide irse. El audit cuantitativo realizado en `notebooks/03_Modeling_Churn.ipynb` (sección 14) re-entrenó el ganador sobre `con_complain.csv` y midió el lift: **Recall sube solo 0.79%** (de 0.8431 a 0.8509). Una mejora tan modesta no justifica el riesgo de que el modelo se entrene con información que en producción no estaría disponible al momento de la predicción. La postura conservadora documentada en la consigna (pag. 8 "ojo con el leakage") prevalece sobre el beneficio marginal.
3. **Alternativas que descarté:**
   - **Mantener Complain en el modelo** apostando a que el lift de 0.79% vale el riesgo: rechazado porque sin validación del timing puede invalidar todo el modelo en producción.
   - **Validar con el equipo de datos** y decidir después: imposible — no hay equipo de datos accesible para un dataset público.
   - **Usar Complain solo para análisis exploratorio**, no para predicción: ya cubierto — el EDA (`01`) y el análisis de interacciones (`01b`) la usan; solo se la excluye del modelo de inferencia.
4. **Consecuencias:** El pipeline de modelado consume exclusivamente `*_sin_complain.csv` (36 features). Los CSVs `*_con_complain.csv` se mantienen en `data/processed/` para reproducibilidad del audit y por si en el futuro se confirma el timing de la variable. Si eso sucede, agregar Complain al pipeline es trivial — los notebooks ya tienen el código de re-entrenamiento.
