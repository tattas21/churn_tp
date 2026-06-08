---
name: ds-stats
description: >
  Skill de estadística para data science: marco descriptivo e inferencial, elección e interpretación de tests, intervalos de confianza, α/p-valor, supuestos de modelos lineales, diseño A/B y trampas frecuentes de interpretación. No sustituye al Explorer (EDA) ni al Feature (transformaciones).
  Trigger: cuando el usuario pide estadística, tests, intervalos de confianza, p-valor, teorema del límite central, muestreo, A/B, supuestos (normalidad, heterocedasticidad, linealidad, multicolinealidad), correlación vs causalidad, penetración vs distribución, o dice "/ds-stats", "qué test uso", "interpretar IC".
license: Apache-2.0
metadata:
  author: agus-chaud
  version: "1.0.0"
---

## When to Use

- Elección o **interpretación profunda** de tests, intervalos y razonamiento inferencial (más allá de la tabla operativa del EDA)
- Explicar **α, p-valor, una vs dos colas**, y cuándo **t** vs **z** (medias vs proporciones)
- **Teorema del límite central**, error típico, **intervalos de confianza** (medias y proporciones), **tamaño de muestra**
- **Diseño y análisis de A/B** (proporciones, cola única)
- **Supuestos** de técnicas estadísticas clásicas: normalidad, heterocedasticidad, linealidad, multicolinealidad (diagnóstico vs **remedio en código**)
- Trampas: **correlación vs causalidad**, **penetración vs distribución**, **absoluto vs relativo**, mala escala en gráficos
- Bootstrapping / bagging a nivel **conceptual** (enlace con modelos de ensamble)

## Límites (no duplicar otras skills)

| Skill | Rol | ds-stats NO hace |
|-------|-----|------------------|
| **ds-explorer** | EDA, calidad, hipótesis de negocio con tests concretos y reportes (`eda.md`, `hipotesis.md`) | Sustituir el flujo EDA ni generar el notebook de exploración |
| **ds-dq** | Diagnóstico/corrección pandas (`calidad-de-datos.md`), nulos duplicados tipos `.str` | Sustituir marco inferencial ni diseño experimental |
| **ds-feature** | Pipeline de transformaciones train/test, parquet, `pipeline.py` | Implementar escalers/imputers salvo que el usuario pida código explícito de ejemplo |
| **ds-model** | Entrenar, CV, feature selection | Competir con el Modeler en selección de variables o métricas de modelo |

**Regla**: ds-stats **orienta y explica**; el código de producción de features y modelos sigue en ds-feature / ds-model.

## Marco conceptual

- **Descriptiva**: resumir y visualizar lo observado.
- **Inferencial**: cuánto pueden extrapolarse las conclusiones a la población; casi siempre se trabaja con **muestras**. Las técnicas inferenciales asumen muestreo **aleatorio** y sin sesgo — en datos empresariales hay que evaluar hasta qué punto aplica.
- **Población** (*N*, parámetros) vs **muestra** (*n*, estadísticos).
- **Escalas**: nominal → ordinal → intervalo/discreta → razón/continua; en práctica **categóricas vs numéricas** determina gráficos y tests.

## Descriptiva (recordatorio)

- Categóricas: frecuencias, tablas cruzadas, chi² para independencia en tablas de contingencia.
- Numéricas: tendencia central (media, mediana, medias geométrica/armónica/winsorizada cuando aplique), dispersión (varianza, DE, CV), correlación **Pearson** (lineal, supuestos) vs **Spearman** (monotonía, rangos).
- **R²** = correlación al cuadrado (interpretación en modelos lineales).
- Correlación **no implica** causalidad (tiempo, variables confusoras, correlación parcial/espuria).

## Inferencial

### Distribuciones (idea práctica)

- Discretas: **Bernoulli**, **Binomial** (`rvs`, `cdf`), **Poisson** (eventos por intervalo; colas y sucesos raros).
- Continuas: **Normal** (μ, σ); **t de Student** (muestras pequeñas / σ desconocida); **F** (varianzas en otros contrastes).

### Teorema del límite central

- La distribución de **medias muestrales** tiende a **normal** aunque la población no lo sea (bajo condiciones habituales).
- **Error típico** de la media: \( \sigma / \sqrt{n} \); en la práctica σ suele estimarse con la **desviación muestral**.

### Intervalos de confianza

- **Media**: margen ≈ error típico × número de desviaciones según el **nivel de confianza** (en texto didáctico a veces ~2 DE para ~95 % si se usa la regla normal).
- **Proporciones**: error típico \( \sqrt{pq/n} \); intervalos para tasas de conversión, etc.
- Interpretación frecuentista: repetición del experimento / construcción del intervalo, no “probabilidad de que μ esté ahí” en sentido bayesiano simple.

### Muestreo

- Sigue siendo relevante con “big data”: desarrollo sobre **muestra aleatoria** y despliegue sobre todo el universo.
- Tamaño de muestra (poblaciones grandes): enlazar **z** del NC deseado, margen de error admisible y varianza conservadora (p.ej. **0,5×0,5** para proporciones).

### α y p-valor

- **α** = 1 − nivel de confianza (típico 0,05).
- **p-valor**: probabilidad (bajo **H0**) de un resultado tan extremo como el observado.
- Si **p < α**: se rechaza **H0** (resultado significativo a ese nivel); si **p ≥ α**: **no** rechazar H0 — **no** equivale a demostrar H0.
- **Una vs dos colas**: muchas implementaciones devuelven p **bilateral**; para una cola, ajustar según la convención acordada (p.ej. **p/2** cuando corresponde y el efecto va en la dirección correcta).

### Contrastes habituales (Python)

| Objetivo | Herramienta típica | Paquete |
|----------|-------------------|---------|
| Media vs valor | `scipy.stats.ttest_1samp` | scipy |
| Dos grupos (medias) | `scipy.stats.ttest_ind(..., equal_var=False)` | scipy |
| Proporción(es) | `statsmodels.stats.proportion.proportions_ztest` | statsmodels |

- **t** para medias cuando no hay σ poblacional; **z** para proporciones con **n** suficiente (regla práctica común *n* grande).

## Supuestos (modelos estadísticos clásicos)

- **Normalidad**: diagnosticar (histograma, **Q-Q** `probplot`); a veces transformar (log, raíz, etc.).
- **Heterocedasticidad**: varianza no constante; revisar dispersión y residuos; a menudo ligada a **no normalidad**.
- **Linealidad** predictora–target: correlaciones, dispersión, residuos; transformar o modelos no lineales.
- **Multicolinealidad**: correlación entre predictoras; evitar redundancia, PCA puntual, o selección en **ds-model**.

## Otros conceptos

- **Bootstrap**: remuestreo; idea base de **bagging** / **Random Forest**.
- **Penetración** (¿qué % del segmento tiene el rasgo?) vs **distribución** (¿qué % del total es ese segmento?) — no mezclar al narrar “quién compra más”.
- **Absoluto vs relativo**: bases pequeñas, ejes engañosos, porcentajes sin denominador.

## Integración con Gentleman Mode

Referencia obligatoria de estilo: `skills/gentleman/SKILL.md`.

- Insistir en **qué se puede concluir** con los datos y el diseño real (¿aleatoriedad? ¿confusores?).
- Separar **significación estadística** de **tamaño de efecto** y utilidad de negocio.

## Decision Logging (personalizado)

Objetivo: documentar decisiones inferenciales críticas para evitar interpretaciones inconsistentes.

### Candidate Gate (Stats)

Registrar como candidata solo si hubo:
- Elección de test inferencial entre alternativas válidas
- Decisión de una vs dos colas (y criterio adoptado)
- Definición de α, nivel de confianza o umbral de decisión no estándar
- Aceptación/rechazo de supuestos (normalidad, homocedasticidad, independencia) con impacto en el análisis

### Comportamiento durante la tarea

- No interrumpir durante la explicación o soporte estadístico.
- Acumular candidatas con evidencia mínima: hipótesis, test, supuesto y criterio de decisión.

### Cierre de tarea (una sola pregunta)

Si hay candidatas:
"Detecté {N} decisiones estadísticas candidatas para `decisions.md` (test/colas/alpha/supuestos). ¿Querés que las documente ahora?"

Si no hay candidatas: no preguntar.

### Plantilla sugerida para `decisions.md` (Stats)

1. **Contexto**: pregunta inferencial y tipo de variable/diseño.
2. **Decisión tomada**: test, cola, alpha o criterio adoptado.
3. **Alternativas consideradas**: tests o criterios alternativos evaluados.
4. **Consecuencias**: impacto en interpretación, robustez y decisiones de negocio.

## Regla transversal de hipótesis (obligatoria)

- Cualquier skill del ecosistema que necesite plantear o validar hipótesis debe apoyarse en `ds-stats` como referencia metodológica principal.
