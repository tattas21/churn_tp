# Hipótesis de Negocio — Churn Analysis

## H1: Clientes nuevos (Tenure bajo) tienen mayor riesgo de irse
- **Lógica de negocio:** Sin hábito de compra formado, es más fácil probar alternativas. Los primeros 6 meses son críticos para "enganchar" al cliente.
- **Resultado esperado:** Mayor tasa de churn en clientes con Tenure < 6 meses
- **Test:** Mann-Whitney U (comparación de medias no paramétricas)
- **Acción sugerida si se confirma:** Programa de onboarding en los primeros 6 meses

## H2: Clientes que se quejaron (Complain=1) churnean más
- **Lógica de negocio:** Una queja es señal directa de insatisfacción. Si no se resuelve, el cliente se va.
- **Resultado esperado:** Mayor tasa de churn en Complain=1
- **Test:** Chi-cuadrado (variable categórica vs target)
- **⚠️ RIESGO DE LEAKAGE:** Verificar con el equipo de datos si la queja se registra ANTES o DESPUÉS de que el cliente se fue. Si es después, no puede usarse como feature en el modelo.

## H3: Mayor inactividad (DaySinceLastOrder alto) predice churn
- **Lógica de negocio:** Un cliente que no compra hace 15+ días en una plataforma de e-commerce probablemente encontró una alternativa o perdió el interés.
- **Resultado esperado:** Clientes churneados tienen más días sin comprar
- **Test:** Mann-Whitney U
- **Acción sugerida:** Email de reactivación automático a los 15 días sin compra

## H4: Menor satisfacción (SatisfactionScore bajo) predice churn
- **Lógica de negocio:** Hipótesis obvia — cliente insatisfecho tiene motivos para irse.
- **Resultado esperado:** Score más bajo en churneados
- **Posible resultado contraintuitivo:** Clientes muy satisfechos también pueden irse (por precio, conveniencia, etc.). Los datos pueden sorprender.
- **Test:** Mann-Whitney U

## H5: Menor cashback = mayor tendencia a irse
- **Lógica de negocio:** El cashback actúa como incentivo financiero para quedarse. Clientes con poco cashback tienen menor "costo de salida" percibido.
- **Resultado esperado:** Churneados tienen menor CashbackAmount promedio
- **Test:** Mann-Whitney U
- **Acción sugerida:** Aumentar cashback para clientes identificados como de alto riesgo
