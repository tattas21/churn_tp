# Reporte de Calidad de Datos

**Dataset**: {path}
**Fecha**: {fecha}
**Shape**: {filas} × {columnas}

---

## 1. Completitud

| Columna | Nulls | % Nulo | Acción sugerida |
|---------|-------|--------|-----------------|
| {col} | {n} | {%} | {imputar media / mediana / moda / dropear / flagear} |

## 2. Columnas Constantes o Cuasi-Constantes

| Columna | Varianza | Valor dominante | % dominante | Acción |
|---------|----------|-----------------|-------------|--------|
| {col} | {valor} | {valor} | {%} | Dropear |

## 3. Duplicados

- Duplicados exactos: {N} filas ({%})
- Duplicados por subset de columnas clave: {descripción}

## 4. Outliers

| Columna | Método | N outliers | % | Límites | Acción sugerida |
|---------|--------|-----------|---|---------|-----------------|
| {col} | IQR | {n} | {%} | [{lower}, {upper}] | {winsorizar / investigar / dropear} |

## 5. Sospechosos de Leakage

| Columna | Razón de sospecha | Correlación con target | Decisión |
|---------|-------------------|----------------------|----------|
| {col} | {conceptualmente viene después del evento} | {valor} | {dropear / investigar} |

## 6. Resumen de Acciones Requeridas

| Prioridad | Acción | Columnas afectadas |
|-----------|--------|-------------------|
| Alta | Dropear por leakage | {cols} |
| Alta | Imputar nulls | {cols} |
| Media | Tratar outliers | {cols} |
| Baja | Revisar cardinalidad | {cols} |
