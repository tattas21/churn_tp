# Talking points — Defensa oral 15 min

> Guía de qué decir en cada slide. **No leer las slides** — usar como apoyo, hablar sobre ellas.
> Total estimado: 14 min de presentación + 1 min buffer + Q&A.

---

## Slide 1 — Título (30s)

**Qué decir:**
- Buenos días/tardes. Soy Bautista Ríos, junto con Tomás y Agustín presentamos el TP de Churn de Clientes.
- Aclarar el rol: **somos analistas de retención, no programadores**. El foco es qué hicimos con la herramienta, no cómo se construyó técnicamente.
- Pedir confirmación de que el formato de 15 min está bien y si prefieren preguntas al final o intercaladas.

**Pregunta probable:** "¿Quién hizo qué parte?" → Cubrimos todas las fases en equipo, con roles rotativos.

---

## Slide 2 — Problema de negocio (1 min)

**Qué decir:**
- Leer literal la pregunta del gerente comercial (citarla, no improvisar).
- El **17%** no es solo número técnico: son **945 clientes que se fueron el año pasado** sobre una base de 5,630.
- Adquirir un cliente nuevo cuesta entre 5 y 7 veces más que retener uno existente (estándar de la industria del e-commerce).
- Cada churner que no detectamos se traduce en un costo de adquisición que la empresa tiene que afrontar para volver al mismo volumen de base.

**Pregunta probable:** "¿De dónde sale el 5-7×?" → Estándar de la industria, validado por estudios de Bain & Company y Harvard Business Review.

---

## Slide 3 — El dataset (1 min)

**Qué decir:**
- Dataset público de e-commerce con 5,630 clientes y 20 columnas.
- El target es Churn binario: 16.8% positivo, 83.2% negativo → **clase desbalanceada**, que es lo que nos llevó a elegir Recall como métrica primaria (volveremos en slide 10).
- Calidad de datos: 7 columnas tienen entre 4 y 5% de nulos, y 3 columnas tenían categorías duplicadas (CC vs Credit Card, etc.) que tuvimos que unificar antes de modelar.
- Variables clave: Tenure, días desde última orden, queja, cashback, satisfacción.

**Pregunta probable:** "¿Por qué tanto énfasis en el desbalance?" → Porque si no lo considero, una métrica como accuracy va a engañarme.

---

## Slide 4 — EDA + 6 hipótesis (1.5 min)

**Qué decir:**
- Antes de modelar, formulamos **6 hipótesis con lógica de negocio**.
- Cada una se testeó con un test estadístico (Mann-Whitney U para continuas, Chi-cuadrado para categóricas) y un gráfico.
- 4 confirmadas (Tenure, Complain, Cashback, Single).
- **2 resultados raros**: H3 (inactividad NO predice churn) y H4 (satisfacción ALTA en churners). Estos los investigamos en profundidad — no aceptamos el resultado a ciegas.

**Pregunta probable:** "¿Qué test usaste y por qué?" → Mann-Whitney U para comparar distribuciones de variables continuas entre grupos (no asume normalidad). Chi-cuadrado para variables categóricas.

---

## Slide 5 — H3/H4 investigación (1.5 min)

**Qué decir:**
- H3 dijo que la inactividad **no** predice churn — incluso al revés: los churneados ordenaron MÁS recientemente.
- **No acepté el resultado**: hice una investigación de seguimiento (notebook `01b`).
- Encontré que **Tenure es un confundidor**: los clientes nuevos churnean masivo (50%) Y por construcción tienen pocos días sin comprar (acaban de registrarse).
- El verdadero patrón es **"compra reciente + queja"** = 39% churn vs 7% en "lejano + sin queja".
- **Conclusión accionable**: la regla histórica del equipo comercial "email a los 15 días sin compra" no se sostiene empíricamente. Hay que cambiarla.

**Pregunta probable:** "Y la H4 (satisfacción)?" → Misma lógica: investigué y encontré que la satisfacción auto-reportada tiene poder predictivo 25× menor que Tenure. La gente reporta satisfacción alta pero igual se va, posiblemente por precio o conveniencia.

---

## Slide 6 — Feature engineering (1 min)

**Qué decir:**
- 7 candidatas evaluadas en el notebook `02b`. Las puertas que tenían que pasar (escritas ANTES de ver resultados):
  1. Información mutua con churn ≥ 0.005
  2. Correlación con features existentes ≤ 0.85 (no redundancia)
  3. Lift de Recall en CV con Random Forest
- Solo 2 pasaron: `OrdersPerMonth` (órdenes por mes de antigüedad) y `CashbackPerMonth` (cashback por mes de antigüedad).
- **Hallazgo retrospectivo poderoso**: estas 2 features terminaron #1 y #3 en feature importance del modelo final. El protocolo funcionó.

**Pregunta probable:** "¿Qué descartaste y por qué?" → 5 candidatas. Tres por baja MI (HighSatisfaction, MultiAddress, Dormant). Dos porque pasaban los gates pero EMPEORABAN el Recall del RF (interacciones DSL×Complain) — RF las encuentra solas.

---

## Slide 7 — Pipeline anti-leakage (1 min)

**Qué decir:**
- **El leakage es el error #1 a evitar.** Si el modelo "ve" información del test durante el entrenamiento, las métricas inflan y el modelo falla en producción.
- Disciplina: **fittear todo en train, aplicar a test**.
- Imputación de nulos: mediana calculada SOLO con train.
- Cap de outliers en percentil 99: SOLO con train.
- OneHotEncoder: SOLO con train.
- **Caso especial — Complain**: no podemos confirmar si la queja se registra antes o después del churn. Hicimos audit cuantitativo, el gap fue solo +0.79% en Recall, así que la **dropeamos**.

**Pregunta probable:** "Por qué no usaste Complain entonces?" → Postura conservadora ante riesgo de leakage. Si el equipo de datos confirma el timing, podemos re-incluirla y recuperar ~1% de Recall.

---

## Slide 8 — Comparación de modelos (1 min)

**Qué decir:**
- Comparamos 4 modelos en 5-fold cross-validation:
  - **Dummy** (baseline obligatorio): predice siempre "no churn". 83% accuracy, 0% Recall. Confirma que accuracy engaña.
  - **Decision Tree** (obligatorio per rúbrica): interpretable pero 8 puntos por debajo de RF.
  - **RandomForest** (ganador): mejor Recall + menor varianza entre folds.
  - **XGBoost**: muy cerca pero perdió por mayor varianza.

**Pregunta probable:** "¿Por qué RF y no XGBoost?" → Recall casi idéntico pero RF tiene std 0.032 vs 0.043 en XGBoost. Más estable. Y gana también el desempate por PR-AUC.

---

## Slide 9 — Tuning iterativo (1.5 min — LA SLIDE MÁS FUERTE)

**Qué decir:**
- Esta es la parte de la que más orgulloso estoy del proyecto.
- **Primera ronda** (n_iter=30): el tuneo dio +1.88% en Recall — debajo del 2% de mi regla. Conclusión inicial: "no tunear".
- **Pero auditoría**: vi que 3 de 4 hiperparámetros estaban pegados a los límites del search space. **Mi conclusión no era defendible.**
- **Segunda ronda** (n_iter=100 con ranges expandidos): cruzó el 2% (+2.34%). Pero seguían pegando boundaries.
- **Tercera ronda** (n_iter=50 con ranges narrow): confirmó el resultado anterior, plateau en iter 27.
- **Validación de overfitting**: medí gap train-CV de TODAS las configs. **Todos los tuneados overfittean MENOS que los defaults.** El miedo a "max_depth=99" no se materializó porque el ensemble compensa.
- **Adopté RF V1 tuneado.** No es solo número más alto: es número más alto CON mejor generalización.

**Pregunta probable:** "¿No es overfit con max_depth=50?" → No, lo medí. El gap train-CV es 0.1371, mejor que el default 0.1569. El ensemble de 1469 árboles con min_samples_leaf=3 compensa.

---

## Slide 10 — Por qué Recall (1 min)

**Qué decir:**
- Analogía para el gerente: **el radar de un hospital**. Querés no perderte ningún caso de cáncer, aunque a veces alertes con uno que no era. El costo de perder un caso de cáncer es muchísimo mayor que el costo de una segunda biopsia innecesaria.
- En churn aplica igual: perder un churner = costo de adquisición + valor recurrente perdido. Falsa alarma = un email innecesario.
- **Costo asimétrico → priorizar Recall.**
- Accuracy con desbalance miente: el dummy con 83% accuracy detecta CERO churners.

**Pregunta probable:** "¿Cuánto cuesta una falsa alarma?" → Bajo. Un email cuesta centavos, un cupón de descuento son pocos dólares marginales. Perder un cliente cuesta el equivalente a 5-7× el costo de adquirirlo.

---

## Slide 11 — Performance final (1 min)

**Qué decir:**
- En el test set, que el modelo NO había visto antes:
  - **Recall 95.3%**: detecta 181 de 190 churners reales.
  - **Precision 81.2%**: de cada 10 alertas, 8 son reales.
  - PR-AUC 0.96, AUC-ROC 0.99.
- **Comparación con la práctica actual**: en ausencia del modelo, la decisión equivale a tirar una moneda para cada cliente. La herramienta multiplica varias veces la efectividad de cualquier campaña.
- **Trade-off explícito**: el modelo prioriza no perderse churners. Eso significa más falsas alarmas (42 vs 16 del default) pero también más detecciones reales (181 vs 179).

**Pregunta probable:** "¿No es sospechoso que el test sea mejor que el CV?" → Sí, lo declaré como limitación. El test fue 10 puntos mejor que el CV (Recall 0.95 vs 0.85). Posibles razones: split estratificado dejó un test favorable; entrené en el train completo (4504 rows) vs 3603 por fold en CV.

---

## Slide 12 — Insights de negocio (1.5 min)

**Qué decir:**
- Las 3 features más importantes para el modelo son: `CashbackPerMonth`, `Tenure`, `OrdersPerMonth`. Las dos features per-tenure son las que mi equipo construyó — validó el feature engineering.
- **Hallazgo 1**: el predictor más fuerte no es "cuánto compra", es **"cuánto compra POR mes de antigüedad"**. Cliente con un año y pocas órdenes = riesgo. Cliente nuevo con pocas órdenes = puede ser saludable.
- **Hallazgo 2**: los primeros 3 meses son la ventana de mayor riesgo (~50% churn). Onboarding es la palanca clave.
- **Hallazgo 3**: la regla "email a 15 días sin compra" NO se sostiene. El verdadero patrón es "compra reciente + queja".
- **Hallazgo 4**: la satisfacción auto-reportada NO predice churn — de hecho, los que se van reportan score MÁS alto. Indicador a re-evaluar.

**Pregunta probable:** "¿Cómo explicás que los que se quejan churnean más?" → Confirmado en H2. Pero ojo: lo más predictivo es "queja **+** cliente nuevo **+** compra reciente". El 39% de churn está en esa intersección.

---

## Slide 13 — Recomendaciones (1 min)

**Qué decir:**
- 4 acciones priorizadas por impacto esperado.
- Cada una tiene: **verbo + objeto + impacto medible + responsable + plazo**.
- **A** (alta prioridad, 30 días): reorientar campañas hacia tasa mensual de actividad.
- **B** (alta prioridad, inmediato): atención one-on-one para nuevos con queja (segmento del 39% churn).
- **C** (media prioridad, 90 días): onboarding estructurado de 90 días.
- **D** (baja prioridad, 30 días): dejar de usar satisfacción como gatillo.

**Pregunta probable:** "¿Cuál arrancarías primero?" → B y A. B es inmediato y de bajo costo (cambiar protocolo de atención). A es rápido de implementar y de alto impacto en detección.

---

## Slide 14 — Limitaciones + Q&A (1 min + buffer)

**Qué decir:**
- **Limitaciones honestas** (no defensivas):
  - Complain timing: no podemos validarlo, somos conservadores.
  - Generalización: re-entrenar trimestralmente con datos frescos.
  - Causalidad: el modelo identifica patrones, no causas. A/B testing antes de escalar.
  - Test set fue tocado dos veces (defaults + V1) — documentado.
- **Próximos pasos** ordenados por impacto:
  1. Validar timing de Complain (semana 1, alta prioridad).
  2. A/B test de las recomendaciones B y C.
  3. Re-entrenar trimestralmente.
  4. Análisis profundo del segmento Single (26.7% churn vs 16.8% base).
- **Cerrar**: "Gracias. ¿Preguntas?"

**Pregunta probable a Q&A:**
- "¿Por qué el RF V1 tuneado y no el default?" → Mejor Recall + mejor gap train-CV + plateau confirmado en V2.
- "¿Cómo medís el éxito en producción?" → Recall mensual sobre churners reales del mes siguiente. Si baja de 90%, re-entrenamos.
- "¿Qué harías con más tiempo?" → A/B test riguroso, validación del timing de Complain, análisis profundo del segmento Single, y monitoreo de drift de features en producción.

---

## Tips generales para la defensa

1. **Habla del proceso, no solo del resultado.** La rúbrica valora más entender que tener números altos.
2. **Si no sabés algo, decilo.** Mejor "no sé pero podría averiguarlo así" que inventar.
3. **Usá `decisions.md` como respaldo.** Si te preguntan algo específico, "esa decisión está documentada en `decisions.md`, lo puedo mostrar si querés".
4. **El glosario lo tenés que poder decir sin leer.** Practicalo con `/grill-me` o `/gentleman`.
5. **Cuando defendas la iteración del tuning (slide 9), hablalo como una historia.** "Primero pensé... después audité... después iteré... después validé... finalmente adopté."
