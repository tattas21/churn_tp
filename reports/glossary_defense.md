# Glosario para la defensa oral

> Los 13 términos del glosario de la rúbrica (págs 11-12) + 1 bonus.
> Cada uno tiene 3 secciones: definición técnica, cómo explicarlo al gerente, y ejemplo aplicado al proyecto.
> **Práctica:** poder decir los 3 niveles SIN LEER. Si no podés, usar `/grill-me` o `/gentleman` para repasar.

---

## Sobre el problema

### Churn

- **Técnico:** evento en que un cliente deja de comprarnos / cancela el servicio.
- **Para el gerente:** "Como un alumno que se borra del gimnasio sin avisar — pagaba todos los meses, ahora no más."
- **En el proyecto:** target binario `Churn` (1 = se fue, 0 = sigue activo). 16.8% de la base churneó el año pasado = 945 clientes de 5,630.

---

### Class imbalance (desbalance de clases)

- **Técnico:** una clase del target aparece sustancialmente menos que la otra. En clasificación, típicamente la clase positiva (lo que queremos detectar) es la minoría.
- **Para el gerente:** "Si decís que todos son diestros, acertás 90% de las veces — pero no aprendiste a distinguir nada. Lo mismo si predecís 'nadie churna': te da 83% de acierto sin servir para nada."
- **En el proyecto:** 83% no-churn / 17% churn. Tratamiento: `class_weight='balanced'` en RF/DT, `scale_pos_weight` en XGBoost, y Recall como métrica primaria en lugar de Accuracy.

---

### Leakage (fuga de información)

- **Técnico:** cuando el modelo se entrena con información que en la realidad no estaría disponible al momento de hacer la predicción.
- **Para el gerente:** "Estudiar con las respuestas del examen al lado. Funciona perfecto en el lab — falla apenas el modelo va a producción y no tiene esa información."
- **En el proyecto:** dos casos:
  - **Riesgo no validable** con `Complain` (no sabemos si la queja se registra antes o después del churn). Postura conservadora: la dropeamos.
  - **Prevención sistemática** en el pipeline: split ANTES de imputar, todas las estadísticas (medianas, percentiles, encoders) se fitean SOLO con train.

---

## Sobre el experimento

### Train/test split

- **Técnico:** dividir el dataset en dos subconjuntos. Train (típicamente 80%) para entrenar el modelo. Test (típicamente 20%) para evaluarlo en datos que nunca vio.
- **Para el gerente:** "El examen sorpresa que el modelo no puede ver hasta el final. Si entrenás y evaluás con los mismos datos, parece que sabe todo — pero falla apenas le mostrás un caso nuevo."
- **En el proyecto:** `test_size=0.2`, `stratify=y`, `random_state=42`. Train: 4504 clientes. Test: 1126 clientes.

---

### Stratified (estratificado)

- **Técnico:** el split respeta la proporción de cada clase del target en ambos subconjuntos.
- **Para el gerente:** "Que ambas porciones de la torta tengan el mismo porcentaje de chocolate. Si el dataset tiene 17% de churn, tanto train como test van a tener cerca del 17%."
- **En el proyecto:** sin stratify, por azar podríamos terminar con 19% churn en train y 11% en test. El modelo aprendería un mundo y se evaluaría en otro. Estratificar garantiza distribución idéntica: train 16.83% / test 16.87%.

---

## Sobre los modelos

### Baseline / Dummy

- **Técnico:** el modelo más simple posible. Predice siempre la clase mayoritaria o aleatoria. Sirve como **piso de comparación** — si un modelo complejo no le gana al dummy, algo está mal.
- **Para el gerente:** "Si el modelo complejo no le gana a tirar una moneda al aire para cada cliente, algo salió muy mal. Sirve para validar que el modelo está aprendiendo algo real."
- **En el proyecto:** `DummyClassifier(strategy='most_frequent')` predice siempre "no churn" → 83% accuracy, **0% Recall**. Confirma que accuracy engaña en datasets desbalanceados.

---

### Decision Tree (árbol de decisión)

- **Técnico:** modelo que hace preguntas sí/no en cascada hasta clasificar. Cada split divide los datos por una variable.
- **Para el gerente:** "Un cuestionario: ¿Tenure menor a 6 meses? → sí → ¿hizo Complain? → sí → riesgo alto. Fácil de leer y explicar."
- **En el proyecto:** obligatorio per rúbrica. Recall CV 0.7652 — 8 puntos por debajo de RF. Sirve para interpretabilidad pero no es el modelo final.

---

### Random Forest

- **Técnico:** ensemble de muchos árboles de decisión, cada uno entrenado en una muestra bootstrap de los datos. Predicción = voto mayoritario (clasificación) o promedio (regresión).
- **Para el gerente:** "En vez de preguntarle a un médico, le preguntás a 500 distintos y votan. Más robusto, mejor que cualquiera por separado."
- **En el proyecto:** ganador. RF V1 tuneado: `n_estimators=1469, max_depth=50, min_samples_leaf=3, max_features=0.978`. Recall CV 0.8629, Recall test 0.9526.

---

## Sobre las métricas

### Accuracy

- **Técnico:** porcentaje total de aciertos sobre el total de casos.
- **Para el gerente:** "Suena buenísimo en datasets balanceados, miente en los desbalanceados. Decir 'nadie churna' da 83% de aciertos pero detecta cero churners. Es inútil para esto."
- **En el proyecto:** la reporto solo como informativo (0.98 en test). **NUNCA** como métrica principal.

---

### Recall (sensibilidad / true positive rate)

- **Técnico:** de todos los casos positivos reales, ¿qué fracción detectó el modelo? TP / (TP + FN).
- **Para el gerente:** "El radar del hospital: de cada 10 personas que iban a churnear, ¿a cuántas detectamos? Mejor radar = menos pérdidas."
- **En el proyecto:** métrica PRIMARIA. Recall en test = 95.3% → detectó 181 de 190 churners reales. La consigna justifica priorizar Recall por costo asimétrico.

---

### Precision (positive predictive value)

- **Técnico:** de todas las predicciones positivas del modelo, ¿qué fracción son verdaderos positivos? TP / (TP + FP).
- **Para el gerente:** "De cada 10 personas que mandamos a tratamiento, ¿cuántas lo necesitaban realmente? Si es 8 de 10, estamos bien."
- **En el proyecto:** Precision en test = 81.2%. De 223 alertas del modelo, 181 son churners reales (42 falsas alarmas). Trade-off deliberado para subir Recall.

---

### F1 score

- **Técnico:** media armónica de Precision y Recall. Penaliza más los desbalances que la media simple.
- **Para el gerente:** "Una nota que combina las dos anteriores. Si una de las dos está mal, F1 baja. Sirve para tener una sola nota."
- **En el proyecto:** F1 test = 0.876. Lo reporto pero la métrica primaria sigue siendo Recall.

---

### SHAP values

- **Técnico:** valores de Shapley aplicados a explicabilidad de modelos. Para cada predicción, descompone la contribución de cada feature al resultado final (suma de SHAP values + valor base = predicción).
- **Para el gerente:** "El ticket del supermercado: no solo el total final, sino qué producto contribuyó cuánto al total. Para cada cliente, podemos ver qué factores empujaron la predicción de riesgo."
- **En el proyecto:** uso SHAP globalmente (qué features pesan más en general — slide 12) y localmente (por qué para ESTE cliente específico la predicción fue X — Apéndice).

---

## Bonus

### BayesSearchCV (Bayesian optimization)

- **Técnico:** algoritmo de búsqueda de hiperparámetros que usa un modelo gaussiano sobre las evaluaciones previas para decidir qué configuración probar a continuación. Más eficiente que GridSearchCV y RandomizedSearchCV en espacios continuos.
- **Para el gerente:** "En vez de probar todas las combinaciones (que tarda años) o tirar dardos al azar, aprende de las pruebas anteriores. 'Si probaste 100 cosas y la mejor fue esta zona, vamos a buscar más cerca de ahí.'"
- **En el proyecto:** lo usé para tunear RF y XGBoost. Hice 3 rondas: 30 iters, 100 iters expandidos, 50 iters narrow. La iteración fue clave para descubrir que los best_params estaban pegados a los boundaries del search space original.

---

## Cómo practicar este glosario

1. **Decirlos en voz alta** — los tres niveles (técnico, gerente, proyecto) de cada uno.
2. **Sin leer** — si necesitás leer, todavía no lo tenés.
3. **En orden aleatorio** — el evaluador no va a preguntarte en el orden de esta lista.
4. **Con presión** — usar `/grill-me` que va a interrogarte con preguntas seguidas.

**Tiempo objetivo:** 30 segundos por término. Si tardás más, la respuesta es muy técnica para una defensa oral.

---

## Donde defender cada decisión

Si el evaluador pregunta por una decisión específica, todas están documentadas en `decisions.md`:

| Tema | Decisión en `decisions.md` | Slide(s) |
|---|---|---|
| Por qué Recall | #1 — Elección de métrica | 10 |
| Por qué dropear Complain | #19 — Drop definitivo Complain | 7 |
| Por qué stratified split | #5 — Split estratificado | 3 |
| Por qué imputación con mediana | #7 — Imputación con mediana | 7 |
| Por qué OHE y no OrdinalEncoder | #9 — One-Hot Encoding | 7 |
| Por qué RF como familia | #17 — RF como familia ganadora | 8 |
| Por qué RF V1 tuneado | #18 — Adopción RF V1 tras iteración | 9 |
| Por qué descartar tuneado al principio | (en #18, narrativa) | 9 |

**Si te preguntan algo que no recordás de memoria**, podés decir: *"Esa decisión está documentada en `decisions.md` con su contexto completo — ¿querés que la abra?"*. Eso muestra que sabés dónde está la información y no estás improvisando.
