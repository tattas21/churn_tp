# Hipótesis de Negocio — Churn Analysis

## H1: Clientes nuevos (Tenure bajo) tienen mayor riesgo de irse
- **Lógica de negocio:** Sin hábito de compra formado, es más fácil probar alternativas. Los primeros 6 meses son críticos para "enganchar" al cliente.
- **Resultado esperado:** Mayor tasa de churn en clientes con Tenure < 6 meses
- **Test:** Mann-Whitney U (comparación de medias no paramétricas)
- **✅ Resultado obtenido:** CONFIRMADA. Tenure promedio: 3.4 meses (churneados) vs 11.5 meses (activos), p < 0.000001.
- **Acción sugerida si se confirma:** Programa de onboarding en los primeros 6 meses

## H2: Clientes que se quejaron (Complain=1) churnean más
- **Lógica de negocio:** Una queja es señal directa de insatisfacción. Si no se resuelve, el cliente se va.
- **Resultado esperado:** Mayor tasa de churn en Complain=1
- **Test:** Chi-cuadrado (variable categórica vs target)
- **✅ Resultado obtenido:** CONFIRMADA. Chi² = 350.9, p < 0.000001 (asociación fuerte).
- **⚠️ RIESGO DE LEAKAGE:** Verificar con el equipo de datos si la queja se registra ANTES o DESPUÉS de que el cliente se fue. Si es después, no puede usarse como feature en el modelo.

## H3: Mayor inactividad (DaySinceLastOrder alto) predice churn
- **Lógica de negocio:** Un cliente que no compra hace 15+ días en una plataforma de e-commerce probablemente encontró una alternativa o perdió el interés.
- **Resultado esperado:** Clientes churneados tienen más días sin comprar
- **Test:** Mann-Whitney U
- **❌ Resultado obtenido:** REFUTADA — y con relación INVERTIDA. Los churneados compraron MÁS recientemente (mediana 2.0 días) que los activos (mediana 4.0 días), p = 1.000. Hallazgo a revisar: posibles nulos en `DaySinceLastOrder` o que el cliente se va tras una mala experiencia de compra reciente. NO confiar en la acción de reactivación basada en este supuesto.
- **Acción sugerida (descartada):** Email de reactivación a los 15 días sin compra — no respaldada por los datos.

## H4: Menor satisfacción (SatisfactionScore bajo) predice churn
- **Lógica de negocio:** Hipótesis obvia — cliente insatisfecho tiene motivos para irse.
- **Resultado esperado:** Score más bajo en churneados
- **Posible resultado contraintuitivo:** Clientes muy satisfechos también pueden irse (por precio, conveniencia, etc.). Los datos pueden sorprender.
- **Test:** Mann-Whitney U
- **⚠️ Resultado obtenido:** CONTRAINTUITIVO. Los churneados tienen score MÁS ALTO (3.39 vs 3.00 activos), p < 0.000001. La satisfacción auto-reportada no explica el churn aquí: posible ruido en el dato o que la causa real de salida (precio, competencia) no se refleja en el score. Usar con cautela como feature.

## H5: Menor cashback = mayor tendencia a irse
- **Lógica de negocio:** El cashback actúa como incentivo financiero para quedarse. Clientes con poco cashback tienen menor "costo de salida" percibido.
- **Resultado esperado:** Churneados tienen menor CashbackAmount promedio
- **Test:** Mann-Whitney U
- **✅ Resultado obtenido:** CONFIRMADA. Cashback promedio: $160 (churneados) vs $181 (activos), p < 0.000001.
- **Acción sugerida:** Aumentar cashback para clientes identificados como de alto riesgo

## H6: Los clientes Single churnean más que casados y divorciados
- **Lógica de negocio:** Los solteros suelen tener menor "anclaje" al servicio: compras más impulsivas, menos compras recurrentes para un hogar y menor costo de cambio percibido.
- **Resultado esperado:** Mayor tasa de churn en MaritalStatus = Single
- **Test:** Chi-cuadrado (variable categórica vs target)
- **✅ Resultado obtenido:** CONFIRMADA (fuerte). Single 26.7% (n=1,796) vs Divorced 14.6% (n=848) vs Married 11.5% (n=2,986). Chi² = 188.7, p ≈ 1e-41. Los Single casi duplican el promedio general (16.8%).
- **Acción sugerida:** Tratar el estado civil como variable de segmentación. Campañas de fidelización y beneficios por recurrencia enfocados en el segmento Single.

---

## Resumen de resultados

| #  | Variable          | Test         | Resultado                                       |
|----|-------------------|--------------|-------------------------------------------------|
| H1 | Tenure            | Mann-Whitney | ✅ Confirmada — menor tenure → más churn        |
| H2 | Complain          | Chi-cuadrado | ✅ Confirmada ⚠️ posible leakage                |
| H3 | DaySinceLastOrder | Mann-Whitney | ❌ Refutada — relación invertida                |
| H4 | SatisfactionScore | Mann-Whitney | ⚠️ Contraintuitivo — churneados más satisfechos |
| H5 | CashbackAmount    | Mann-Whitney | ✅ Confirmada — menor cashback → más churn      |
| H6 | MaritalStatus     | Chi-cuadrado | ✅ Confirmada — Single churnea ~2× más          |

**Predictores más fuertes para el modelo:** Tenure (H1) y MaritalStatus/Single (H6).
**A revisar antes de modelar:** H3 (posibles nulos en DaySinceLastOrder), H4 (ruido en satisfacción), H2 (confirmar leakage de Complain).
