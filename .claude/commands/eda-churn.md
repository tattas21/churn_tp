# eda-churn

Skill de Análisis Exploratorio de Datos (EDA) para el proyecto de churn de ecommerce. Guía la exploración sistemática del dataset para generar hipótesis accionables.

## Contexto del proyecto
- Dataset: `data/raw/E_Commerce_Dataset.csv` (5,630 clientes, 20 columnas)
- Target: `Churn` (0 = activo, 1 = se fue) — 16.8% positivo
- Notebook de EDA: `notebooks/01_EDA_Churn.ipynb`
- Reportes: `reports/` (hipótesis en `01_hipotesis.md`, gráficos en PNG)

## Variables del dataset (referencia rápida)
- **Comportamiento:** `Tenure`, `OrderCount`, `DaySinceLastOrder`, `CouponUsed`, `CashbackAmount`
- **Satisfacción:** `SatisfactionScore`, `Complain`
- **Perfil:** `CityTier`, `Gender`, `MaritalStatus`, `NumberOfAddress`, `NumberOfDeviceRegistered`
- **Preferencias:** `PreferredLoginDevice`, `PreferredOrderCat`, `PreferredPaymentMode`
- **Financiero:** `WarehouseToHome`, `HourSpendOnApp`, `OrderAmountHikeFromlastYear`

## Lo que hacés cuando te invocan

### Sin argumento / "por dónde empiezo"
Guiá el EDA en este orden:
1. Carga y shape: `df.shape`, `df.dtypes`, `df.head()`
2. Calidad de datos: `df.isnull().sum()`, duplicados
3. Distribución del target: `df['Churn'].value_counts(normalize=True)`
4. Overview numérico: `df.describe()`

### "distribuciones" o "univariado"
Para variables numéricas: histogramas con `df.hist(figsize=(15,12))` y boxplots por `Churn`.
Para variables categóricas: `value_counts()` y barplots con porcentaje de churn por categoría.
Guardá cada gráfico en `reports/` con nombre descriptivo.

### "correlaciones"
- Heatmap de correlaciones: `sns.heatmap(df.corr(), annot=True, cmap='coolwarm')`
- Correlación punto-biserial de cada variable con `Churn` (usando `scipy.stats.pointbiserialr`)
- Identificá variables con correlación > 0.3 o < -0.3 como candidatas fuertes

### "bivariado" o "hipótesis"
Para cada hipótesis, mostrá:
1. El grupo comparado (churners vs no-churners)
2. Estadística descriptiva por grupo
3. Test de significancia: `scipy.stats.mannwhitneyu` (numéricas) o `chi2_contingency` (categóricas)
4. Visualización: boxplot o barplot con error bars

**Hipótesis base a explorar (si no hay ninguna todavía):**
- H1: Clientes con menor `Tenure` tienen mayor churn
- H2: Clientes con `Complain=1` tienen mayor churn (⚠️ posible leakage)
- H3: Menor `SatisfactionScore` → más churn
- H4: Clientes con pocas órdenes (`OrderCount` bajo) → más churn
- H5: `CityTier` afecta el churn (diferente experiencia logística)

### "missing values" o "nulos"
- Calculá % de nulos por columna
- Para columnas con < 5% nulos: imputar con mediana (numéricas) o moda (categóricas)
- Para columnas con > 20% nulos: evaluar si vale la pena conservar
- Nunca imputar ANTES de separar train/test para evitar data leakage

### "outliers"
- Usá IQR: `Q1 = df[col].quantile(0.25); Q3 = df[col].quantile(0.75); IQR = Q3 - Q1`
- Marcá outliers extremos (> Q3 + 3*IQR)
- Comparar si los outliers tienen mayor tasa de churn antes de eliminarlos

### "resumen" o "reporte"
Generá un resumen con:
- Las 5 variables más correlacionadas con Churn
- Hipótesis confirmadas y refutadas
- Variables candidatas para feature engineering
- Alertas de calidad de datos (nulos, outliers, posible leakage)

## Reglas
- Siempre verificá `df['Churn'].dtype` — debe ser int64, no object
- Guardá gráficos en `reports/` con `plt.savefig('reports/nombre.png', bbox_inches='tight')`
- Documentá cada hallazgo importante en `reports/01_hipotesis.md`
- Nunca modifiques `data/raw/E_Commerce_Dataset.csv`

## Referencias
- [eda_user_churn (mshakhomirov)](https://github.com/mshakhomirov/eda_user_churn) — EDA para churn con Python y BigQuery SQL
- [Churn-Prediction-Customer-Segmentation-in-E-Commerce (MariaDimopoulou)](https://github.com/MariaDimopoulou/Churn-Prediction-Customer-Segmentation-in-E-Commerce) — EDA extenso con análisis bivariado y multivariado
- [Churn-Analysis-Ecommerce-Customer (archie-cm)](https://github.com/archie-cm/Churn-Analysis-Ecommerce-Customer) — EDA con recomendaciones de negocio y dashboard
