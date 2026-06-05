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

## Decisión — Unificación de categorías en PreferredPaymentMode

1. **Qué decidí:** Reemplazar 'CC' → 'Credit Card' y 'COD' → 'Cash on Delivery'
2. **Por qué:** Son claramente la misma categoría escrita de forma distinta. Si no se unifican, el modelo las trata como categorías separadas y aprende patrones incorrectos.
3. **Alternativas que descarté:** Mantenerlas separadas (causaría ruido en el modelo sin agregar información real)
4. **Consecuencias:** El campo PreferredPaymentMode queda con 6 valores únicos en lugar de 8.

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
