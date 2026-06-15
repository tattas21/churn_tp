# Design Brief — Defensas Oral TP Churn de Clientes

> **Para una IA de diseño** (Claude Artifacts, v0, Lovable, etc.).
> Producir **dos archivos HTML long-scroll** consistentes en estilo visual pero con audiencias y contenido distinto.
> Material disponible: este brief + 9 PNGs en `reports/` (descritas al final).

---

## 1. El proyecto en 30 segundos

TP académico (Inteligencia Artificial Aplicada a Negocios, Licenciatura en Negocios y Tecnología, 1er cuatrimestre 2026). Construimos un modelo de predicción de churn de clientes para un e-commerce con 5,630 clientes y 17% de churn anual.

El equipo **no es de ingeniería técnica** — son analistas de negocio. La consigna del gerente comercial fue: *"¿Podemos detectar quiénes están por irse antes de que dejen de comprar? ¿Por qué nos dejan?"*. Construimos la herramienta (Random Forest, 95% Recall en test) y descubrimos 4 hallazgos accionables.

La defensa académica requiere **dos presentaciones distintas** para dos audiencias distintas.

---

## 2. Output esperado

**Dos archivos HTML long-scroll**, single-file (sin dependencias externas excepto fonts de Google):

| Archivo | Audiencia | Duración oral | Tono |
|---|---|---|---|
| `defense_executive.html` | Gerente comercial (negocio) | ~7 min | Cero jerga, foco en plata e impacto, narrativa de "qué hacemos con esto" |
| `defense_technical.html` | Evaluador técnico (cátedra) | ~10-12 min | Metodología, rigor, decisiones documentadas, iteración |

**Importante**: ambos comparten **mismo sistema de diseño** (paleta, tipografía, componentes, hero, footer) para que se vean como del mismo proyecto. Solo cambia el contenido y el énfasis narrativo.

**Restricciones técnicas**:
- Single HTML file por deck (CSS embebido o vía CDN solo para fonts)
- Responsive (mobile/tablet/desktop)
- Long-scroll vertical (NO slides con viewport fijo — esto resuelve el problema del intento anterior con reveal.js que cortaba contenido)
- Anchor navigation lateral (sticky sidebar con enlaces a cada sección, o navegación top sticky)
- Exportable a PDF vía `Cmd+P` con paginación limpia
- Idioma: español
- Tabla de números siempre legible
- Imágenes con `max-width: 100%`

---

## 3. Audiencias

### Audiencia 1 — Gerente comercial (deck ejecutivo)

**Quién es:** decisor de negocio sin formación técnica. Le importa qué hacer con la herramienta, no cómo se construyó.
**Qué le interesa:** plata, ROI, segmentos accionables, palancas claras.
**Qué le aburre:** F1 score, hiperparámetros, gráficos de PR curves, hablar de Bayesian optimization.
**Cómo le hablamos:** analogías ("el radar del hospital"), métricas traducidas ("detecta 95 de cada 100 churners"), recomendaciones con verbo + objeto + impacto + plazo + responsable.

### Audiencia 2 — Evaluador técnico (deck técnico)

**Quién es:** profesor de la cátedra que evalúa rigor metodológico.
**Qué le interesa:** decisiones documentadas, validación, anti-leakage, iteración, honestidad sobre limitaciones.
**Qué le aburre:** marketing-speak, conclusiones sin evidencia, "el modelo funciona muy bien".
**Cómo le hablamos:** decisiones con justificación cuantitativa, referencias explícitas a `decisions.md`, tablas con métricas y std, narrativa del proceso iterativo.

---

## 4. Sistema de diseño (compartido entre ambos decks)

### Tipografía

- **Headings**: `Inter` (700 / 600) — moderna, alta legibilidad
- **Body**: `Inter` (400 / 500)
- **Mono** (para código y números): `JetBrains Mono` o `SF Mono` fallback
- **Cargar desde Google Fonts**: `Inter:wght@400;500;600;700` + `JetBrains Mono:wght@400;600`

### Paleta

```
Primary (azul ejecutivo):       #1a5490
Primary dark:                   #0f3a66
Accent (rojo para énfasis):     #e74c3c
Success / detección:            #27ae60
Warning:                        #f39c12
Neutral 900 (texto principal):  #1f2937
Neutral 700 (texto secundario): #4b5563
Neutral 500 (texto sutil):      #9ca3af
Neutral 100 (fondo cards):      #f3f4f6
Neutral 50 (fondo página):      #fafafa
Border:                         #e5e7eb
```

Sugerencia: usar gradientes muy sutiles en el hero (`linear-gradient(135deg, #1a5490, #0f3a66)`).

### Layout

- Max-width del contenido: **1100px** centrado
- Padding lateral: **24px mobile / 48px desktop**
- Separación entre secciones: **96px** vertical
- Espaciado interno cards: **24-32px**
- Bordes redondeados: **12px** para cards, **6px** para botones

### Componentes que se necesitan

1. **Hero section**: gradiente sutil, título grande, kicker, equipo, fecha. Botón CTA opcional ("Descargar PDF").
2. **Section divider**: línea fina horizontal con kicker (texto pequeño en caps) sobre el título de la sección.
3. **KPI card**: número GRANDE (60-80px), label arriba (pequeño caps), descripción debajo (negocio). Variant: con gradiente o liso.
4. **Insight card** (para hallazgos): número (1, 2, 3...) en círculo a la izquierda, título + 2 líneas, opción de imagen al costado.
5. **Recommendation card**: título con verbo + objeto, badges (prioridad alta/media/baja, plazo), métrica de impacto, responsable.
6. **Quote/blockquote**: borde izquierdo azul, fondo claro, italic.
7. **Comparison table**: header con color primary, rows con hover suave, alguna celda destacada (ganador en verde).
8. **Two-column section**: gráfico a la izquierda + texto a la derecha (alternar lados entre secciones).
9. **Limitation / risk card**: borde izquierdo en color warning, texto honesto.
10. **Sticky navigation sidebar** (desktop) o **top bar** (mobile): lista de secciones con scroll spy.

### Microinteracciones (sutiles, no decorativas)

- Fade-in suave de secciones al hacer scroll (intersection observer)
- Hover en cards: leve elevación (transform y box-shadow)
- Anchor links suaves (`scroll-behavior: smooth`)
- Botón "Volver arriba" flotante después de scrollear >800px

### Lo que NO queremos

- ❌ Animaciones excesivas que distraigan
- ❌ Carruseles, sliders
- ❌ Modales/popups
- ❌ Iconos genéricos de stock (FontAwesome estilo 2010)
- ❌ Stock photos
- ❌ Comic Sans, gradientes setentosos, sombras grandes

---

## 5. Visual assets disponibles (9 PNGs en `reports/`)

| Archivo | Qué muestra | Usar en |
|---|---|---|
| `01b_h3_investigacion.png` | Heatmap Tenure × DSL + distribución por Complain (investigación de la anomalía H3) | Deck **técnico** (sección investigación H3/H4) |
| `01b_h4_investigacion.png` | Heatmap Tenure × Score + distribución por Complain (anomalía H4) | Deck **técnico** (misma sección) |
| `02b_fe_correlaciones.png` | Heatmap de correlaciones de candidatas FE vs features existentes (gate de redundancia) | Deck **técnico** (sección FE) — opcional |
| `02b_fe_rf_benchmark.png` | Bar chart Recall + AUC por escenario (baseline + cada candidata + ALL 7) | Deck **técnico** (sección FE) |
| `03_cv_inicial.png` | Bar chart Recall + PR-AUC por modelo (Dummy, DT, RF, XGB) | Deck **técnico** (sección comparación modelos) |
| `03_pr_curves.png` | Precision-Recall + ROC curves del ganador en test | **Ambos decks** (técnico: rigor; ejecutivo: muestra performance) |
| `03_feature_importance.png` | Top 15 features built-in del ganador | Deck **técnico** (sección SHAP/feature importance) |
| `03_shap_summary.png` | SHAP summary plot (bar + dot) — global | **Ambos decks** (ejecutivo: qué predice; técnico: análisis SHAP) |
| `03_shap_local_ejemplos.png` | 2 SHAP waterfall plots (1 True Positive + 1 False Negative) | Deck **técnico** (sección SHAP local) |

**Sugerencia**: en el deck ejecutivo, simplificar las imágenes con un caption descriptivo de negocio. Ej.: para `03_shap_summary.png` → caption: *"Los 3 factores que más pesan: cuánto compra el cliente por mes, hace cuánto que es cliente, cuánto cashback recibe por mes."*

---

## 6. Contenido — `defense_executive.html` (~7 secciones)

### Hero
- **Título**: "Predicción de Churn de Clientes"
- **Subtítulo**: "Reporte ejecutivo para gerencia comercial"
- **Kicker arriba**: "TP Final · Inteligencia Artificial Aplicada a Negocios"
- **Equipo**: Bautista Rios · Tomás Attas · Agustín Venutolo · Francisco Cavanna · Agustin Picciolo
- **Fecha**: Junio 2026
- **CTA opcional**: "Imprimir / Descargar PDF" (botón que ejecuta `window.print()`)

### Sección 1 — El problema (con KPI hero)
- Quote grande del gerente: *"¿Podemos detectar quiénes están por irse antes de que dejen de comprar? ¿Por qué nos dejan?"*
- KPI cards (3 columnas):
  - **17%** — Churn de la base anual
  - **945** — Clientes perdidos el año pasado
  - **5-7×** — Más caro adquirir que retener (estándar industria)
- Texto debajo: 2-3 líneas conectando los números con el costo real.

### Sección 2 — Qué descubrimos (4 hallazgos en cards)

Card 1: **La tasa mensual de actividad es el predictor más fuerte**
- Un cliente con pocas órdenes y poco cashback POR mes de antigüedad es el de mayor riesgo. La métrica que importa no es "cuánto compra" sino "cuánto compra para los meses que lleva con nosotros".

Card 2: **Los primeros 3 meses concentran el mayor riesgo**
- Clientes nuevos (≤3 meses): ~50% churn vs <10% en clientes con más de un año. La ventana de onboarding es el momento de máxima palanca.

Card 3: **La regla "email a 15 días sin compra" NO se sostiene**
- Los datos muestran que los clientes que se van compraron **MÁS recientemente** (mediana 2 días vs 4 días). El verdadero patrón es "compra reciente + queja sin resolver" = 39% churn vs 7% en el escenario opuesto.

Card 4: **La satisfacción auto-reportada NO predice churn**
- Los clientes que se van reportan score **más alto** (3.4 vs 3.0). Indicador a re-evaluar antes de usar como gatillo de campañas.

Imagen sugerida: `03_shap_summary.png` con caption simplificado.

### Sección 3 — La herramienta
- Quote grande: *"Detecta 95 de cada 100 clientes que se van — con tiempo para intervenir."*
- KPI cards (2 columnas grandes):
  - **95.3%** Recall — "Sobre 190 churners reales, detectó 181"
  - **81.2%** Precision — "De cada 10 alertas, 8 son reales"
- Imagen: `03_pr_curves.png` con caption: *"Performance del modelo sobre clientes que no había visto antes."*
- 2-3 líneas explicando que la herramienta puede revisar la base completa cada noche y producir una lista priorizada.

### Sección 4 — 4 recomendaciones accionables (cards con prioridad y plazo)

Card A — **Reorientar campañas hacia tasa mensual de actividad**
- Badge: 🔴 Alta · 30 días · Marketing Retención
- Métrica: ≥85% Recall en las alertas (vs <50% con la regla de 15 días)

Card B — **Atención one-on-one para nuevos con queja**
- Badge: 🔴 Alta · Inmediato · Customer Success
- Métrica: reducir churn del segmento de 39% a 25%

Card C — **Onboarding estructurado de 90 días**
- Badge: 🟡 Media · 90 días · CS + Producto
- Métrica: reducir churn de nuevos de 50% a 30%

Card D — **Re-evaluar satisfacción como gatillo**
- Badge: 🟢 Baja · 30 días · Analytics
- Métrica: ahorro de campañas mal dirigidas

### Sección 5 — Limitaciones (honestidad)

3 cards con borde warning:
- **Sobre la variable Complain**: no podemos confirmar el timing — la dropeamos por riesgo de leakage. Si se valida, recuperamos ~1% más de detección.
- **Sobre falsas alarmas**: 1 de cada 5 alertas no se materializa. ~42 contactos innecesarios cada 223 alertas. Costo bajo pero a tener en cuenta para no saturar la base.
- **Sobre causalidad**: el modelo identifica patrones, no causas. Validar campañas con A/B testing antes de escalar.

### Sección 6 — Próximos pasos

Lista numerada (ordenada por impacto):
1. Validar timing de Complain con equipo de datos (semana 1)
2. Activar campañas por tasa mensual de actividad y medir a 30/60/90 días
3. A/B testing de las acciones B y C
4. Re-entrenar el modelo trimestralmente con datos frescos
5. Análisis profundo del segmento Single (26.7% churn)

### Footer
- Link al repo: `github.com/tattas21/churn_tp`
- "Reporte completo, código y decisiones disponibles para validación"
- Año

---

## 7. Contenido — `defense_technical.html` (~12 secciones)

### Hero
- **Título**: "Predicción de Churn — Reporte Técnico"
- **Subtítulo**: "Metodología, decisiones e iteración"
- **Kicker**: "TP Final · Defensa técnica"
- **Equipo + fecha**: igual al deck ejecutivo
- **CTA**: botón "Ver código en GitHub" + "Descargar PDF"

### Sección 1 — Dataset y calidad de datos
- KPI cards:
  - **5,630** clientes
  - **20** columnas (1 ID + 1 target + 18 features)
  - **16.83%** churn (clase positiva — desbalance)
  - **7 cols con nulos** (4–5% cada una)
- Tabla compacta de columnas clave con tipo y % nulos
- Nota: 3 columnas tenían categorías duplicadas (CC/Credit Card, COD/Cash on Delivery, Phone/Mobile Phone) — unificadas en `clean_categories()`

### Sección 2 — EDA: 6 hipótesis de negocio

Tabla con columnas: Hipótesis · Test estadístico · Resultado · Status (badge color)

| H | Hipótesis | Test | Resultado | Status |
|---|---|---|---|---|
| H1 | Tenure bajo → churn | Mann-Whitney U | 3.4m churn vs 11.5m activo, p<1e-6 | ✅ Confirmada |
| H2 | Complain → churn | Chi-cuadrado | Chi²=350.9, p<1e-6 | ⚠️ Confirmada con leakage |
| H3 | Inactividad → churn | Mann-Whitney U | Mediana churn 2d < activo 4d | ❌ REFUTADA — investigada |
| H4 | Baja satisfacción → churn | Mann-Whitney U | Score churn 3.4 > activo 3.0 | ⚠️ Contraintuitivo — investigado |
| H5 | Bajo cashback → churn | Mann-Whitney U | $160 churn vs $181 activo, p<1e-6 | ✅ Confirmada |
| H6 | Single → churn | Chi-cuadrado | 26.7% vs 11.5% Married, p≈1e-41 | ✅ Confirmada |

### Sección 3 — Investigación H3/H4 (la pieza fuerte de la defensa)

Two-column: imagen `01b_h3_investigacion.png` a la izquierda, texto a la derecha.

- **H3 invertido era engañoso**: Tenure es confundidor. Los clientes nuevos churnean 50% Y por construcción tienen pocos días sin comprar. La mezcla "inclina" la mediana.
- **El verdadero patrón**: "compra reciente + queja" = 39% churn vs 7% en "lejano + sin queja".
- **Implicancia de negocio**: la regla "email a 15 días" se retira.

Y abajo otra two-column con `01b_h4_investigacion.png`:
- **H4 contraintuitivo es real**: score se mueve monotónicamente con churn (11.5% → 23.8%) pero la información mutua es 25× menor que Tenure. Score noisy.

### Sección 4 — Feature engineering empíricamente validado

Two-column: `02b_fe_rf_benchmark.png` + texto.

- **Protocolo**: 7 candidatas, 3 gates (MI ≥ 0.005 + redundancia ≤ 0.85 + lift de Recall en RF) — **escritas ANTES de ver resultados**.
- **2 adoptadas**: `OrdersPerMonth`, `CashbackPerMonth`. Ambas terminaron #1 y #3 en feature importance del modelo final.
- **5 descartadas** con razón cuantitativa (tabla compacta):
  - `RecentPurchaseWithComplaint`, `NewCustomerComplaint` — pasaban gates pero degradaban Recall (RF las encuentra natively)
  - `HighSatisfaction`, `MultiAddress`, `Dormant` — MI < 0.005

### Sección 5 — Pipeline anti-leakage

Diagrama visual del flujo (ASCII o un diagrama hecho con CSS):
```
raw CSV → clean_categories → split estratificado → impute median (fit-on-train)
   → cap p99 (fit-on-train) → add_features (row-wise) → OneHotEncoder (fit-on-train) → 4 CSVs
```

- Énfasis: **todo se fittea SOLO con train**, se aplica a test.
- Audit de Complain: re-entrenamos el ganador en `con_complain` y medimos gap. Resultado: **+0.79% Recall** → drop confirmado (postura conservadora frente a leakage no validable).

### Sección 6 — Comparación de 4 modelos (5-fold CV)

Imagen `03_cv_inicial.png` + tabla:

| Modelo | Recall CV (mean ± std) | PR-AUC CV | Notas |
|---|---|---|---|
| DummyClassifier | 0.000 ± 0.000 | 0.168 | Baseline obligatorio — accuracy 83% pero Recall 0 |
| DecisionTree | 0.765 ± 0.038 | 0.667 | Obligatorio per rúbrica — interpretable pero -8 pts |
| **RandomForest** | **0.843 ± 0.032** | **0.909** | **Ganador (familia)** — mejor Recall + menor varianza |
| XGBoost | 0.834 ± 0.043 | 0.901 | Cerca pero perdió por varianza y desempate |

### Sección 7 — Tuning iterativo (LA sección)

Narrativa visual: 3 cards horizontales con las 3 rondas + análisis.

Card 1 — **Ronda original** (n_iter=30)
- Recall: +1.88% (debajo del 2% threshold)
- Conclusión inicial: descartar tuneado
- **Auditoría**: 3 de 4 best_params pegados a boundaries → conclusión NO defendible

Card 2 — **V1 expanded** (n_iter=100, ranges expandidos)
- Recall: +2.34% ✅ supera 2%
- Pero XGBoost dio config sospechosa (`n_estimators=50` al piso) — local optimum

Card 3 — **V2 narrow** (n_iter=50, ranges targeted)
- Recall: +2.19% (estable, plateau confirmado en iter 27)
- XGBoost se estabilizó (`n_estimators=277` típico)

Footer de la sección: **Adopción final RF V1**.

### Sección 8 — Análisis de overfitting (gap train-CV)

Tabla:

| Config | Recall train | Recall CV | Gap | Verdict |
|---|---|---|---|---|
| RF default | 1.000 | 0.843 | +0.157 | Línea base |
| **RF V1 tuneado** | **1.000** | **0.863** | **+0.137** | **Mejor que default** |
| RF V2 tuneado | 1.000 | 0.862 | +0.139 | Cerca de V1 |
| XGB default | 1.000 | 0.834 | +0.166 | — |
| XGB V2 tuneado | 1.000 | 0.856 | +0.144 | Mejor que XGB default |

Highlight: **TODOS los tuneados overfittean MENOS que sus defaults**. El miedo a `max_depth=50` no se materializó — el ensemble compensa.

### Sección 9 — Performance final en test (UNA sola evaluación)

Imagen `03_pr_curves.png` + tabla:

| Métrica | RF defaults (1ª eval) | RF V1 tuneado (2ª eval) |
|---|---|---|
| **Recall** | 0.9421 | **0.9526** |
| Precision | 0.9179 | 0.8117 |
| F1 | 0.9299 | 0.8765 |
| PR-AUC | 0.9839 | 0.9611 |
| AUC-ROC | 0.9964 | 0.9917 |

Matriz de confusión (mini-card 2×2): TN=894, FP=42, FN=9, **TP=181**.

Nota declarada: test set evaluado dos veces. Trade-off Recall↑/Precision↓ alineado con costo asimétrico.

### Sección 10 — SHAP global + local

Two-column o stack:
- Imagen `03_shap_summary.png` con explicación: top 3 features son `CashbackPerMonth`, `Tenure`, `OrdersPerMonth`.
- Imagen `03_shap_local_ejemplos.png`: explicación caso TP (modelo acertó) + caso FN (modelo se lo perdió y por qué).

### Sección 11 — Audit de Complain (leakage check)

Tabla simple:

| Métrica (CV) | Sin Complain | Con Complain | Gap |
|---|---|---|---|
| Recall | 0.8431 | 0.8509 | +0.0079 |
| PR-AUC | 0.9094 | 0.9289 | +0.0195 |

**Regla escrita ANTES**: gap ≤ 0.05 → drop confirmado. Resultado: drop. Cierre del loop "dos versiones de la base".

### Sección 12 — Limitaciones técnicas + próximos pasos

Two-column:

**Limitaciones**:
- Test set evaluado dos veces (declarado en `decisions.md` #18)
- Tuning leakage inherente al model selection
- Complain timing no validable (dataset público)
- Causalidad vs correlación

**Próximos pasos** (priorizados):
1. Validar timing Complain (recupera ~1% Recall)
2. Hold-out adicional para validación final
3. Re-entrenamiento trimestral
4. A/B testing de campañas
5. Profundización segmento Single (26.7% churn)

### Footer
- "19 decisiones documentadas en `decisions.md`"
- "Notebook ejecutable, script reproducible (`src/models/train.py`), modelos serializados"
- Link al repo

---

## 8. Equipo (para el hero de ambos decks)

Lista de autores, en este orden:

- **Bautista Rios** (sin acento)
- Tomás Attas
- Agustín Venutolo
- Francisco Cavanna
- Agustin Picciolo

Cátedra: Inteligencia Artificial Aplicada a Negocios
Carrera: Licenciatura en Negocios y Tecnología
Primer cuatrimestre 2026

---

## 9. Tips finales para la IA de diseño

1. **El deck ejecutivo no es un PowerPoint** — pensalo más como una landing page de Stripe o Linear. Long-scroll moderno, mucho whitespace, KPI cards grandes, tipografía generosa.
2. **El deck técnico no es un paper académico** — sigue el mismo lenguaje visual pero con más densidad de información: tablas, métricas, decisiones documentadas. Stripe Atlas, Vercel docs, Databricks blog son referencias mentales.
3. **No usar slides con viewport fijo** — el problema del intento anterior con reveal.js fue exactamente ese. Long-scroll resuelve.
4. **Cero `<script>` complejos** — solo lo mínimo (smooth scroll, scroll spy, botón "back to top"). Sin frameworks pesados.
5. **Charts**: los PNGs ya están listos, solo embedarlos con `<img>` y caption en `<figcaption>`. No re-renderizar gráficos con JS.
6. **Print stylesheet**: agregar `@media print` que oculte la sidebar/nav y deje el contenido en flujo limpio para `Cmd+P`.

---

*Brief generado para acompañar las 9 PNGs y producir 2 archivos HTML long-scroll consistentes en estilo, distintos en contenido y audiencia.*
