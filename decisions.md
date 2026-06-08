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
