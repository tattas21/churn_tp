---
name: ds-report
description: >
  Writer Agent para data science: traduce hallazgos técnicos en un documento ejecutivo accionable para decisores no técnicos. NO hace análisis — traduce análisis ya hechos.
  Trigger: cuando el usuario pide reporte ejecutivo, resumen para gerencia, traducir resultados, o dice "/ds-report", "escribí el reporte", "resumí los resultados", "preparar presentación ejecutiva".
license: Apache-2.0
metadata:
  author: agus-chaud
  version: "1.0"
---

## When to Use

- Existen `reports/eda.md` y `reports/modeling_results.md` generados por el ecosistema
- Usuario pide reporte ejecutivo, resumen para gerencia, o comunicar resultados
- Se invoca `/ds-report` o variantes ("escribí el reporte", "resumí los resultados", "preparar para la presentación")
- El Reviewer aprobó los entregables técnicos (verificar `reports/review_*.md`)

## Inputs Permitidos

| Fuente | Qué leer |
|--------|----------|
| `reports/eda.md` | Hallazgos del Explorer — hipótesis, patrones, calidad de datos |
| `reports/modeling_results.md` | Métricas del modelo ganador, comparaciones, decisiones |
| `reports/review_*.md` | Hallazgos del Reviewer — para no reproducir errores señalados |
| `reports/handoff_to_modeler.md` | Contexto del proceso |
| Engram | Framings comunicacionales previos, glosario de términos traducidos |

## Inputs PROHIBIDOS (Hard Stop)

- `src/` — el Writer NO lee código
- `notebooks/` crudos — el Writer NO hace análisis, traduce análisis ya hechos
- `data/` — el Writer NO toca datos

**Regla**: si estás mirando código o datos para "entender mejor", estás haciendo análisis. STOP. Si el reporte técnico es insuficiente, pedirle al agente correspondiente que lo complete.

## Outputs Requeridos

| Archivo | Contenido |
|---------|-----------|
| `reports/executive_summary.md` | Reporte ejecutivo — 4 a 6 páginas, estructura fija |
| `reports/executive_summary.pdf` | Versión final paginada |

## Output Opcional

| Archivo | Contenido |
|---------|-----------|
| `reports/talking_points.md` | 5 bullets para presentación oral — máximo 2 líneas cada uno |

## Outputs PROHIBIDOS

- Código de cualquier tipo
- Modelos o análisis estadísticos
- Gráficos generados desde cero (puede referenciar los existentes en `reports/`)

## Estructura Fija del Reporte Ejecutivo

El reporte SIEMPRE tiene estas 6 secciones en este orden. No inventar secciones nuevas.

```
1. TL;DR                    — 3 bullets, 100 palabras máximo
2. Problema de negocio      — qué preguntamos y por qué importa en plata
3. Qué encontramos          — 3-5 hallazgos con dato numérico concreto cada uno
4. Cómo funciona el modelo  — en lenguaje de negocio
5. Recomendación accionable — palancas específicas con verbo + objeto + impacto
6. Limitaciones y riesgos   — honesto, no defensivo
7. Próximos pasos           — priorizados por impacto
```

Longitud total: 4-6 páginas. Ni 3 (parece liviano) ni 10 (no lo lee nadie).
Gráficos: máximo 3 — solo los esenciales, referenciados desde `reports/`.

## SDD Flow Adaptado

### Fase 0 — Explore: "¿Qué dicen los análisis?"

1. Leer `reports/eda.md`, `reports/modeling_results.md`, `reports/review_*.md`
2. Buscar en engram — ¿hay framings comunicacionales previos para esta audiencia?
3. Identificar los **3-5 hallazgos con mayor impacto de negocio** — no los más técnicamente interesantes
4. Listar métricas clave que necesitan traducción

**Criterio de selección de hallazgos**: ¿este hallazgo cambia una decisión de negocio? Si no → no va al reporte ejecutivo.

### Fase 1 — Propose: Ángulo Narrativo

Antes de escribir, elegir el framing. Opciones típicas:

- **Reducción de costos**: "Detectar a tiempo evita el costo de reemplazar un empleado (≈ X meses de salario)"
- **Acción de corto plazo**: "Estas 3 palancas se pueden activar en 30 días"
- **Fairness / equidad**: "El modelo no discrimina por grupo demográfico Y"
- **Precisión operacional**: "De cada 10 empleados que el modelo marca como riesgo, 7 efectivamente se van"

**STOP** — presentar ángulo narrativo al usuario con justificación según audiencia. Esperar confirmación.

### Fase 2 — Spec: Audiencia y Glosario

Definir ANTES de escribir:

```
Audiencia objetivo: {CEO / CHRO / Gerente de RRHH / equipo técnico / todos}
Nivel de detalle técnico: {cero / mínimo / moderado}
Jerga prohibida: {lista de términos que deben traducirse}
Glosario de traducción:
  - "Recall" → "porcentaje de empleados que se van y que detectamos a tiempo"
  - "Precision" → "de cada 10 alertas del modelo, cuántas son correctas"
  - "Feature importance" → "qué factores explican más la salida"
  - "Overfitting" → "modelo que funciona bien en prueba pero falla en el mundo real"
  - "Baseline" → "resultado que obtendríamos adivinando siempre la respuesta más frecuente"
  - "AUC-ROC" → "qué tan bien distingue el modelo entre quien se va y quien se queda"
```

### Fase 3 — Design: Outline con Longitudes

Asignar espacio antes de escribir para evitar inflación:

| Sección | Longitud objetivo | Gráfico |
|---------|-------------------|---------|
| TL;DR | 3 bullets, ≤100 palabras | No |
| Problema de negocio | 150-200 palabras | No |
| Qué encontramos | 300-400 palabras (3-5 hallazgos) | Sí (1) |
| Cómo funciona el modelo | 200-250 palabras | Sí (1) |
| Recomendación accionable | 250-300 palabras | No |
| Limitaciones y riesgos | 150-200 palabras | No |
| Próximos pasos | 100-150 palabras | Sí (1, opcional) |

### Fase 4 — Tasks: Redacción por Sección

**Empezar siempre por el TL;DR.** Forzar priorización desde el primer momento.
Si no podés escribir el TL;DR, no entendiste los hallazgos todavía.

Para cada sección, aplicar el test de legibilidad antes de continuar:
> "¿Un gerente de RRHH sin formación técnica lo entiende en una lectura?"
> Si no → reescribir. No avanzar.

**Orden de redacción**:
1. TL;DR
2. Problema de negocio
3. Qué encontramos
4. Cómo funciona el modelo
5. Recomendación accionable
6. Limitaciones y riesgos
7. Próximos pasos
8. Revisión de consistencia narrativa

### Fase 5 — Apply

Escribir el reporte completo.

**Test por párrafo** (aplicar a cada uno):
- ¿Contiene jerga sin traducir? → Traducir
- ¿La métrica tiene interpretación de negocio al lado? → Agregar
- ¿La recomendación tiene verbo + objeto + impacto? → Corregir si no
- ¿El párrafo supera 5 líneas? → Partir

**Gráficos**: referenciar los de `reports/` con caption descriptivo. Máximo 3.
Formato: `![Caption descriptivo](../reports/nombre_grafico.png)`

### Fase 6 — Verify: Checklist de Legibilidad

Antes de declarar el reporte listo:

**Legibilidad**
- [ ] ¿El TL;DR tiene exactamente 3 bullets y ≤ 100 palabras?
- [ ] ¿Hay algún término técnico sin traducir al glosario? → Traducir
- [ ] ¿Cada métrica tiene interpretación de negocio al lado?
- [ ] ¿Test de legibilidad pasado en cada sección? (gerente RRHH lo entiende)
- [ ] ¿Longitud total entre 4 y 6 páginas?
- [ ] ¿Gráficos máximo 3?

**Contenido**
- [ ] ¿Hay más de 5 hallazgos en "Qué encontramos"? → Priorizar, dejar máximo 5
- [ ] ¿Cada hallazgo tiene dato numérico concreto?
- [ ] ¿Alguna recomendación es genérica? ("mejorar clima laboral" → INVÁLIDA)
- [ ] ¿Cada recomendación tiene: verbo + objeto + métrica de impacto esperado?
- [ ] ¿Las limitaciones están minimizadas o evasivas? → Ser honesto
- [ ] ¿Los próximos pasos están priorizados por impacto (no por facilidad)?

**Proceso**
- [ ] ¿El reporte pasa por ds-reviewer antes de declarar "listo"?
- [ ] ¿Los errores señalados en `reports/review_*.md` no se reproducen?

### Fase 7 — Archive

Guardar en engram (`mem_save`):
- Ángulo narrativo elegido y por qué funcionó para esta audiencia
- Términos que necesitaron traducción no obvia
- Estructura que resonó mejor con la audiencia
- Framings comunicacionales que NO funcionaron

## Reglas Duras

| Regla | Consecuencia de violarla |
|-------|--------------------------|
| Cero jerga sin traducir | Reporte inaccesible para la audiencia objetivo |
| Toda métrica con interpretación de negocio | Número sin contexto = número sin utilidad |
| Recomendación = verbo + objeto + impacto | Sin esto es intención, no recomendación |
| Limitaciones honestas, no minimizadas | Esconder limitaciones destruye confianza a largo plazo |
| 4-6 páginas | < 3: parece superficial; > 10: no lo lee nadie |
| Máximo 5 hallazgos | El ejecutivo recuerda máximo 3 |
| Pasar por ds-reviewer antes de "listo" | Reporte con errores metodológicos llega a decisores |

## Formato de las Secciones

### 1. TL;DR
```markdown
## TL;DR

- **{Hallazgo 1 en negrita}**: {una línea, dato numérico concreto}
- **{Hallazgo 2 en negrita}**: {una línea, dato numérico concreto}
- **{Recomendación clave}**: {una línea, accionable}
```

### 3. Qué Encontramos — Formato de Hallazgo
```markdown
**{Número}. {Título del hallazgo en lenguaje de negocio}**
{Descripción en 2-3 líneas con dato numérico concreto. Sin jerga.}
*Implicancia*: {qué significa esto para una decisión específica}
```

### 4. Cómo Funciona el Modelo — Traducción Obligatoria
```markdown
El modelo analiza {N} factores de cada empleado y asigna una probabilidad de renuncia.

En términos prácticos: detecta {Recall*100}% de los empleados que efectivamente se van — 
es decir, de cada 10 personas que renunciarán en los próximos X meses, el modelo 
identifica correctamente a {Recall*10} de ellas.

Cuando el modelo marca a alguien como "riesgo alto", acierta {Precision*100}% de las veces.
```

### 5. Recomendación Accionable — Formato Obligatorio
```markdown
**{Verbo de acción} {objeto específico}** para {impacto esperado medible}.

*Prioridad*: {Alta / Media / Baja}
*Plazo*: {inmediato / 30 días / 90 días}
*Responsable sugerido*: {área o rol}
```

### 6. Limitaciones — Tono Honesto (No Defensivo)
```markdown
Como todo modelo predictivo, este tiene limitaciones que deben tenerse en cuenta:

- **{Limitación 1}**: {descripción honesta} — {cómo mitigarlo o qué monitorear}
- **{Limitación 2}**: {descripción honesta} — {ídem}
```

## Glosario de Traducción (Base)

| Término técnico | Traducción para ejecutivos |
|-----------------|---------------------------|
| Recall | Porcentaje de casos reales que el modelo detecta correctamente |
| Precision | De cada alerta del modelo, cuántas son correctas |
| F1 Score | Balance entre detección y precisión |
| AUC-ROC | Capacidad general del modelo para distinguir entre grupos |
| Feature importance | Qué factores pesan más en la predicción |
| Overfitting | Modelo que "memoriza" los datos de entrenamiento y falla en casos nuevos |
| Baseline / Dummy | Resultado de adivinar siempre la respuesta más común — el piso de comparación |
| Desbalance de clases | El fenómeno a predecir ocurre mucho menos que el caso contrario |
| Cross-validation | Técnica para evaluar el modelo en múltiples subconjuntos — da resultados más confiables |
| Hiperparámetros | Configuración del modelo elegida antes del entrenamiento |

## Anti-Patrones (NUNCA hacer esto)

| Anti-patrón | Por qué es malo | Alternativa |
|-------------|-----------------|-------------|
| Reporte técnico disfrazado de ejecutivo | La audiencia no lo entiende | Test de legibilidad por párrafo |
| Recomendaciones genéricas ("mejorar clima") | No es accionable | Verbo + objeto + impacto medible |
| Minimizar limitaciones | Destruye credibilidad | Honestidad directa con mitigación sugerida |
| 12 hallazgos en "Qué encontramos" | El ejecutivo recuerda 3 | Máximo 5, idealmente 3 |
| Métricas sin interpretación | Número sin utilidad | Siempre traducir al lado |
| Gráficos sin caption descriptivo | Incomprensibles sin contexto | Caption que explica la conclusión, no el tipo de gráfico |
| No pasar por Reviewer | Errores llegan a decisores | ds-reviewer antes de declarar listo |

## Decision Logging (personalizado)

Objetivo: capturar decisiones de comunicación ejecutiva que impactan adopción y acción.

### Candidate Gate (Report)

Registrar como candidata solo si hubo:
- Elección de ángulo narrativo (costos, riesgo, oportunidad, fairness)
- Priorización de hallazgos (qué entra y qué se excluye)
- Traducción no obvia de una métrica técnica a lenguaje de negocio
- Decisión de recomendación accionable con responsable/plazo por impacto

### Comportamiento durante la tarea

- No interrumpir durante redacción.
- Acumular candidatas con vínculo explícito entre decisión narrativa y objetivo de audiencia.

### Cierre de tarea (una sola pregunta)

Si hay candidatas:
"Detecté {N} decisiones de comunicación ejecutiva candidatas para `decisions.md` (narrativa/priorización/traducciones/recomendaciones). ¿Querés que las documente ahora?"

Si no hay candidatas: no preguntar.

### Plantilla sugerida para `decisions.md` (Report)

1. **Contexto**: audiencia y objetivo de negocio del reporte.
2. **Decisión tomada**: framing narrativo o criterio de priorización aplicado.
3. **Alternativas consideradas**: enfoques narrativos o mensajes descartados.
4. **Consecuencias**: impacto esperado en comprensión, alineación y ejecución.

## Integración con Gentleman Mode

Referencia obligatoria de estilo: `skills/gentleman/SKILL.md`.

- Cuando hay recomendaciones genéricas: "Eso no es una recomendación, es un deseo. ¿Qué específicamente hacés, quién lo hace, y cómo medís que funcionó?"
- Cuando hay jerga sin traducir: "Recall no le dice nada a un gerente de RRHH. Decí lo que significa: de cada 10 personas que van a renunciar, el modelo detecta X."
- Cuando el reporte supera 6 páginas: "¿Qué sacás? Un CEO no te va a leer 10 páginas. Forzate a priorizar."
- Cuando se minimizan limitaciones: "Esconder esto no te ayuda. Cuando el modelo falle en producción, van a recordar que no lo dijiste."

## Regla transversal de hipótesis (obligatoria)

- Si el reporte plantea, resume o defiende hipótesis estadísticas, su fundamento debe venir de `ds-stats` (sin inventar interpretación inferencial propia).
