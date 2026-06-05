# negocio-ecommerce

Skill para entender el contexto de negocio de ecommerce en el proyecto de churn. Traduce hallazgos técnicos en impacto de negocio y guía análisis orientados a retención de clientes.

## Contexto del proyecto
- Problema: predecir qué clientes se van antes de que se vayan
- Dataset: clientes de un ecommerce con variables de comportamiento, satisfacción y perfil
- Stakeholder implícito: equipo de retención / CRM

## Framework de negocio que aplicás

### Métricas clave de ecommerce (siempre tenerlas presentes)
- **Churn Rate:** % clientes perdidos por período
- **LTV (Lifetime Value):** ingreso esperado de un cliente durante su vida útil
- **CAC (Customer Acquisition Cost):** costo de adquirir un cliente nuevo (generalmente 5-7x más caro que retener)
- **Retention Rate:** 1 - Churn Rate
- **ARPU (Average Revenue Per User):** ingreso promedio por usuario

### Segmentación RFM (Recency, Frequency, Monetary)
Si el dataset tiene variables de fecha o monto:
- **Recency:** cuánto hace que compró (proxy: `DaySinceLastOrder`)
- **Frequency:** cuántas veces compró (proxy: `OrderCount`, `CouponUsed`)
- **Monetary:** cuánto gastó (proxy: `CashbackAmount`, `OrderAmountHikeFromlastYear`)

Segmentos típicos a identificar:
| Segmento | RFM | Acción |
|----------|-----|--------|
| Champions | Alto-Alto-Alto | Fidelizar, pedir reviews |
| Loyal | Alto-Alto-Medio | Upsell |
| At Risk | Bajo-Alto-Alto | Campaña de retención urgente |
| Lost | Bajo-Bajo-Bajo | Win-back o ignorar |
| New | Alto-Bajo-Bajo | Onboarding, primer hábito |

### Análisis de cohortes
Una cohorte = grupo de clientes que empezaron en el mismo período.
- Proxy en este dataset: agrupar por rangos de `Tenure`
- Calcular churn rate por cohorte para ver si los clientes más nuevos churnan más

## Lo que hacés cuando te invocan

### Sin argumento / "contexto de negocio"
Explicá el problema de churn en términos de negocio:
- Por qué churn importa más allá del modelo (costo de adquisición vs retención)
- Qué significa un falso negativo (churner no detectado = cliente perdido sin intervención)
- Qué significa un falso positivo (campaña de retención innecesaria = costo)
- Por qué Recall > Precision en este contexto

### "impacto" o "cuánto vale"
Calculá o estimá el impacto económico:
```python
# Estimación simple del valor de mejorar Recall
churners_reales = df['Churn'].sum()          # 946 clientes
falsos_negativos_actuales = ...               # del confusion matrix
falsos_negativos_nuevos = ...
clientes_recuperables = falsos_negativos_actuales - falsos_negativos_nuevos
ltv_promedio = df['CashbackAmount'].mean() * 12  # proxy de valor anual
valor_recuperado = clientes_recuperables * ltv_promedio * 0.3  # tasa de conversión de campaña
```

### "RFM" o "segmentar clientes"
Construí la segmentación RFM usando las variables disponibles:
1. Asignar score 1-5 a Recency, Frequency, Monetary
2. Combinar scores
3. Etiquetar segmentos
4. Analizar churn rate por segmento

```python
df['R_score'] = pd.qcut(df['DaySinceLastOrder'], 5, labels=[5,4,3,2,1])
df['F_score'] = pd.qcut(df['OrderCount'].rank(method='first'), 5, labels=[1,2,3,4,5])
df['M_score'] = pd.qcut(df['CashbackAmount'], 5, labels=[1,2,3,4,5])
df['RFM_score'] = df['R_score'].astype(str) + df['F_score'].astype(str) + df['M_score'].astype(str)
```

### "cohortes" o "cohort analysis"
Agrupar por rangos de `Tenure` y calcular churn rate:
```python
bins = [0, 6, 12, 24, 48, float('inf')]
labels = ['0-6m', '6-12m', '1-2y', '2-4y', '4y+']
df['cohort'] = pd.cut(df['Tenure'], bins=bins, labels=labels)
churn_by_cohort = df.groupby('cohort')['Churn'].agg(['mean', 'count'])
```

### "recomendaciones" o "qué hacer con el modelo"
Dado el resultado del modelo, estructurá las recomendaciones así:

**Por segmento de riesgo predicho:**
- Riesgo alto (prob > 0.7): intervención inmediata — descuento personalizado, llamada de retención
- Riesgo medio (0.4-0.7): campaña proactiva — email con oferta, survey de satisfacción
- Riesgo bajo (< 0.4): mantener engagement — newsletter, loyalty points

**Variables accionables vs no accionables:**
- Accionables: `SatisfactionScore` (mejorar soporte), `CouponUsed` (más cupones), `HourSpendOnApp` (push notifications)
- No accionables: `Tenure` (no podés hacer que un cliente lleve más tiempo), `Gender`, `CityTier`

### "variables" o "qué significa cada columna"
Explicá las variables en contexto de negocio:
- `Tenure`: antigüedad en meses — clientes nuevos son más volátiles
- `CityTier`: 1 = ciudad principal, 2 = secundaria, 3 = terciaria — indica calidad logística disponible
- `WarehouseToHome`: distancia del depósito al cliente — afecta experiencia de entrega
- `NumberOfDeviceRegistered`: clientes multidevice son más comprometidos
- `PreferedOrderCat`: categoría favorita de compra — sirve para personalización
- `SatisfactionScore`: 1-5, autoexplicativo
- `Complain`: si hizo reclamo en el último mes ⚠️ posible leakage
- `OrderAmountHikeFromlastYear`: % de aumento de gasto vs año anterior

## Reglas
- Siempre conectá los hallazgos del EDA o del modelo a una acción de negocio concreta
- Cuando des recomendaciones, separar claramente lo que el modelo puede predecir de lo que el negocio debe ejecutar
- Advertí cuando una variable de alto impacto predictivo no es accionable (ej: `Tenure`)
- Documentá las recomendaciones de negocio en `decisions.md` con `/add-decision`

## Referencias
- [Churn-Analysis-Ecommerce-Customer (archie-cm)](https://github.com/archie-cm/Churn-Analysis-Ecommerce-Customer) — análisis con persona de cliente y estrategia de retención por segmento
- [Customer-Lifetime-Value-Retention-Analytics-with-Python (ManikaNagpal)](https://github.com/ManikaNagpal/Customer-Lifetime-Value-Retention-Analytics-with-Python) — LTV, cohort analysis, RFM, ROI de marketing en datos retail
- [RFM-Segmentation-Cohort-Analysis-Market-Basket-Analysis (psgpyc)](https://github.com/psgpyc/RFM-Segmentation-Cohort-Analysis-Market-Basket-Analysis-on-eCommerce-Data) — pipeline completo de análisis de ecommerce con SQL + Python
- [marketingwithpython (sonyalomsadze)](https://github.com/sonyalomsadze/marketingwithpython) — churn, CLV, RFM, cohortes y segmentación en un solo repo
