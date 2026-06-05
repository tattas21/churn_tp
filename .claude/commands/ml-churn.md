# ml-churn

Skill de Machine Learning para el proyecto de churn de ecommerce. Guía el análisis, entrenamiento y evaluación de modelos con foco en Recall sobre clientes churners.

## Contexto del proyecto
- Dataset: `data/raw/E_Commerce_Dataset.csv` (5,630 clientes, 20 variables)
- Target: `Churn` (16.8% positivo → desbalanceado)
- Métrica principal: **Recall** (minimizar falsos negativos = churners no detectados)
- Variable en vigilancia: `Complain` (posible data leakage)

## Lo que hacés cuando te invocan

Dependiendo del argumento del usuario:

### Sin argumento / "qué sigue"
Revisá el notebook `02_Modeling_Churn.ipynb` y reportá:
- Qué modelos están entrenados
- Métricas actuales (Recall, Precision, F1, AUC-ROC)
- Próximo experimento recomendado

### "baseline" o "comparar modelos"
Guiá la construcción de una comparación entre:
1. **Logistic Regression** (baseline lineal, interpretable)
2. **Decision Tree** (baseline no-lineal)
3. **Random Forest** (ensemble, robusto)
4. **XGBoost / Gradient Boosting** (mejor rendimiento esperado)

Para cada modelo, usá `class_weight='balanced'` o SMOTE antes del fit. Evaluá con `classification_report` y `roc_auc_score`.

### "feature engineering"
Sugerí features nuevas basadas en el dataset:
- Ratios: `SatisfactionScore / Tenure`, `OrderCount / Tenure`
- Flags binarios: `MultiDevice = CityTier > 1`, `HasComplain`
- Interacciones: `Tenure * OrderAmountHikeFromlastYear`
- Encoding: OrdinalEncoder para `PreferredLoginDevice`, `PreferredPaymentMode`, `Gender`

Siempre verificá primero qué variables ya existen en el CSV con `df.columns`.

### "hiperparámetros" o "tuning"
Guiá el uso de `GridSearchCV` o `RandomizedSearchCV` con:
- `cv=StratifiedKFold(n_splits=5)` (estratificado por el desbalance)
- `scoring='recall'` (métrica objetivo)
- Grids sugeridos por modelo (Random Forest: n_estimators, max_depth, min_samples_leaf; XGBoost: learning_rate, max_depth, n_estimators, subsample)

### "imbalance" o "desbalance"
Explicá y guiá las opciones:
1. `class_weight='balanced'` — automático, sin generar datos sintéticos
2. `SMOTE` — genera sintéticos en train. **Importante: aplicar SOLO sobre train, nunca sobre test**
3. Umbral de decisión: ajustar `threshold` en `predict_proba` para aumentar Recall a costa de Precision

### "evaluar" o "métricas"
Generá o revisá:
- `confusion_matrix` con visualización
- `classification_report` (Precision, Recall, F1 por clase)
- `roc_auc_score` y curva ROC
- Precision-Recall curve (más informativa que ROC en datasets desbalanceados)
- Feature importances del modelo final

## Reglas
- Nunca uses `accuracy` como métrica principal — el desbalance la hace engañosa
- Siempre evaluá sobre el test set que NO tocaste durante el tuning
- Documentá cada experimento en `decisions.md` con `/add-decision`
- Si encontrás data leakage potencial, advertí antes de continuar

## Referencias
- [Churn-Prediction-Ecommerce-ML](https://github.com/Khizer-Data/Churn-Prediction-Ecommerce-ML) — pipeline completo con XGBoost, GridSearchCV y PCA
- [predict-customer-churn (Featuretools)](https://github.com/Featuretools/predict-customer-churn) — framework general con automated feature engineering
- [Customer-Churn-Analysis (rohitkulkarni08)](https://github.com/rohitkulkarni08/Customer-Churn-Analysis) — comparación LR, RF, KNN, SVM, XGBoost con SMOTE
