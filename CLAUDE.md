# Churn TP — Contexto del proyecto

## Problema de negocio
Predecir qué clientes de un e-commerce están por irse (churn) antes de que se vayan. Binary classification: `Churn = 1` (se fue) vs `Churn = 0` (sigue activo).

## Dataset
- **Archivo:** `data/raw/E_Commerce_Dataset.csv`
- **Filas:** 5,630 clientes
- **Target:** `Churn` (16.8% positivo → dataset desbalanceado)
- **Variables:** 20 columnas (tenure, comportamiento de compra, satisfacción, etc.)

## Estructura del proyecto
```
churn_tp/
├── .claude/commands/      # Skills del proyecto
├── data/raw/              # CSV original (NO modificar)
├── data/processed/        # dataset_limpio.csv (output del EDA) + train/test (con/sin Complain)
├── notebooks/
│   ├── 01_EDA_Churn.ipynb        # EDA + 6 hipótesis + limpieza de categorías → dataset_limpio.csv
│   ├── 02_Preparacion_Datos.ipynb # Carga base limpia, split, imputación, outliers, FE, one-hot
│   └── 03_Modeling_Churn.ipynb   # Baseline (DT) + Random Forest
├── reports/               # Gráficos generados por los notebooks
├── models/                # Modelos serializados (.pkl) — gitignored
├── src/                   # Utilidades reutilizables (preprocessing.py)
├── decisions.md           # Decisiones documentadas del proyecto
└── requirements.txt
```

## Decisiones clave
1. **Métrica principal: Recall** — minimizar falsos negativos (churners no detectados)
2. **Split estratificado** — preserva 16.8% de churn en train y test
3. **Split ANTES de imputar** — medianas y percentiles fit solo en train (evita leakage)
4. **One-Hot Encoding** para categóricas nominales (no LabelEncoder)
5. **Cap de outliers al percentil 99** (Tenure, WarehouseToHome, NumberOfAddress)
6. **Feature engineering**: CashbackPerOrder, CouponPerOrder, AppHoursPerDevice, IsNewCustomer
7. **`class_weight='balanced'`** en Random Forest — compensa el desbalance
8. **Variable `Complain` en vigilancia** — base guardada con y sin ella para comparar (riesgo de leakage)

Ver el detalle de cada decisión en `decisions.md`.

## Entorno
- Python en Miniconda: `/Users/tomasattas/miniconda3/`
- Instalar dependencias: `pip install -r requirements.txt`
- Kernel de Jupyter: `Python 3 (ipykernel)` desde Miniconda

## Skills disponibles
- `/add-decision` — Agrega decisión documentada a `decisions.md`
- `/check-checkpoint` — Verifica estado de los checkpoints del TP
- `/eda-churn` — Guía el análisis exploratorio: distribuciones, hipótesis, correlaciones, outliers
- `/ml-churn` — Guía el modelado: comparación de modelos, feature engineering, tuning, métricas
- `/negocio-ecommerce` — Contexto de negocio: RFM, cohortes, impacto económico, recomendaciones de retención

Ver todos los links de referencia en `recursos_github.md`.
