# check-checkpoint

Verificá el estado de los checkpoints del TP de Churn. Revisá el proyecto y reportá qué está cumplido y qué falta.

## Checkpoints del TP

### Semana 1 — Setup y entendimiento (fecha: 05/06)
- [ ] El CSV se puede cargar y `df.head()` funciona → verificá que `data/raw/E_Commerce_Dataset.csv` existe
- [ ] Entorno virtual activo → verificá que seaborn, pandas, sklearn están instalados en Miniconda
- [ ] Primer commit hecho → corré `git log --oneline` y verificá que hay al menos un commit
- [ ] Repositorio en GitHub conectado → verificá si hay remote configurado con `git remote -v`

### Semana 1/2 — EDA (fecha: 05/06)
- [ ] Notebook `01_EDA_Churn.ipynb` existe en `notebooks/`
- [ ] Hay al menos 5 hipótesis documentadas en `reports/01_hipotesis.md`
- [ ] Hay gráficos en `reports/` (al menos 5 PNG)
- [ ] `decisions.md` tiene al menos 3 decisiones documentadas

### Semana 2 — Modelado (fecha: 12/06)
- [ ] Notebook `02_Modeling_Churn.ipynb` existe
- [ ] El split train/test estratificado está implementado
- [ ] Hay un modelo baseline
- [ ] Hay un modelo potente (Random Forest o similar)
- [ ] Las métricas usadas son Recall/Precision/F1/AUC-ROC (no solo Accuracy)

## Cómo verificar

Para cada checkpoint, revisá los archivos reales del proyecto. No asumas — comprobá. Reportá con ✅ si está cumplido, ❌ si falta, y ⚠️ si está parcialmente hecho.

Al final, decí cuál es el siguiente paso más urgente.
