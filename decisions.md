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

## Decisión — Resolución de H3 (DaySinceLastOrder con relación invertida)

1. **Qué decidí:** Mantener `DaySinceLastOrder` como feature en el modelo. Descartar la recomendación de negocio original ("email a los 15 días sin compra").
2. **Por qué:** En el EDA la relación apareció invertida (churneados con DSL mediana 2.0d vs activos 4.0d). La investigación en `01b_Investigacion_Anomalias_H3_H4.ipynb` mostró:
   - **No es sesgo por nulos** (5.4% vs 5.7% nulos, chi² p=0.78).
   - **Es confundidor con Tenure**: en el quartil más nuevo el churn es 38–59% para todos los DSL, y como los nuevos dominan la población churneada, arrastran la mediana hacia DSL bajo.
   - **Hay interacción fuerte con Complain**: "compra reciente + queja" = 38.9% churn vs 7.1% en "lejano + sin queja" (efecto 5.5×).
   - `DSL` queda 3º en información mutua con el target (0.0262), después de Tenure y Cashback.
3. **Alternativas que descarté:** Dropear `DaySinceLastOrder` por relación contraintuitiva.
4. **Consecuencias:** Preferir modelos basados en árboles (Random Forest, GBM) que capturan interacciones automáticamente. Si se usa regresión logística, crear features `DSL × Complain` y `DSL × IsNewCustomer`.

---

## Decisión — Resolución de H4 (SatisfactionScore con relación contraintuitiva)

1. **Qué decidí:** Mantener `SatisfactionScore` en el set inicial de features pero con **expectativa baja**. Si en el modelo final no aparece en el top-10 de feature importance, descartar.
2. **Por qué:** En el EDA los churneados tenían score promedio MÁS ALTO (3.39 vs 3.00). La investigación en `01b_Investigacion_Anomalias_H3_H4.ipynb` mostró:
   - **No es escala invertida**: la diferencia entre con/sin queja es solo -0.095 (score y queja son casi independientes).
   - **El churn rate crece monótonamente con el score** (11.5%, 12.6%, 17.2%, 17.1%, 23.8%) — la relación es real.
   - **Tenure es confundidor parcial**: el patrón es fuerte en clientes nuevos (Q1: 36%→57%) pero se aplana en clientes viejos.
   - **Poder predictivo muy bajo**: información mutua = 0.0054, **25× menor que Tenure (0.1359)**. El score auto-reportado parece no reflejar sentimiento real (posiblemente inflado o medido en otro momento del journey).
3. **Alternativas que descarté:** (a) Dropear inmediatamente (sin validar contra otros modelos); (b) Crear feature binaria `HighSatisfaction = (score >= 4)` — queda como opción de transformación si el score crudo no aporta.
4. **Consecuencias:** No usar `SatisfactionScore` para decisiones de negocio sin validar antes cómo y cuándo se mide en el sistema fuente.
