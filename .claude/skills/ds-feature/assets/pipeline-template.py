"""
Feature Engineering Pipeline — Template
Generado por ds-feature skill

USO:
    from src.features.pipeline import build_pipeline, run_pipeline
    preprocessor, X_train, X_test, y_train, y_test = run_pipeline()
"""

import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import (
    StandardScaler, RobustScaler, OrdinalEncoder, OneHotEncoder
)
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.model_selection import train_test_split

# ── Configuración ──────────────────────────────────────────────────────────────
RAW_DATA_PATH = "data/raw/dataset.csv"
TRAIN_OUTPUT   = "data/processed/features_train.parquet"
TEST_OUTPUT    = "data/processed/features_test.parquet"
TARGET_COL     = "target"  # cambiar según dataset
RANDOM_STATE   = 42
TEST_SIZE      = 0.2

# ── Columnas por tipo ──────────────────────────────────────────────────────────
# Completar según handoff_to_modeler.md
COLS_TO_DROP         = []   # leakage, constantes, identificadores
NUMERIC_ROBUST       = []   # numéricas con outliers severos
NUMERIC_STANDARD     = []   # numéricas normales o log-transformadas
CATEGORICAL_LOW      = []   # categóricas nominales, cardinalidad <= 15
CATEGORICAL_HIGH     = []   # categóricas nominales, cardinalidad > 15
ORDINAL_FEATURES     = []   # categóricas ordinales
ORDINAL_CATEGORIES   = []   # lista de listas con el orden para cada ordinal
COLS_NULL_FLAG       = []   # columnas donde null > 20% — crear flag antes de imputar


def add_null_flags(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Agrega columnas flag para nulls significativos."""
    for col in cols:
        df[f"{col}_was_null"] = df[col].isnull().astype(int)
    return df


def build_pipeline() -> ColumnTransformer:
    """Construye el ColumnTransformer con todas las transformaciones."""

    numeric_robust_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", RobustScaler()),
    ])

    numeric_standard_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])

    categorical_low_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    ordinal_transformer = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OrdinalEncoder(
            categories=ORDINAL_CATEGORIES,
            handle_unknown="use_encoded_value",
            unknown_value=-1,
        )),
    ])

    transformers = []
    if NUMERIC_ROBUST:
        transformers.append(("num_robust", numeric_robust_transformer, NUMERIC_ROBUST))
    if NUMERIC_STANDARD:
        transformers.append(("num_standard", numeric_standard_transformer, NUMERIC_STANDARD))
    if CATEGORICAL_LOW:
        transformers.append(("cat_low", categorical_low_transformer, CATEGORICAL_LOW))
    if ORDINAL_FEATURES:
        transformers.append(("ordinal", ordinal_transformer, ORDINAL_FEATURES))

    preprocessor = ColumnTransformer(
        transformers=transformers,
        remainder="drop",  # dropea todo lo que no está listado explícitamente
    )

    return preprocessor


def run_pipeline():
    """
    Ejecuta el pipeline completo:
    1. Carga datos
    2. Agrega null flags
    3. Dropea columnas prohibidas
    4. Split ANTES de transformar
    5. Fitea sobre train, transforma train y test
    6. Guarda parquets
    """
    # 1. Carga
    df = pd.read_csv(RAW_DATA_PATH)
    print(f"Dataset cargado: {df.shape}")

    # 2. Null flags (ANTES del split para no perder la señal)
    df = add_null_flags(df, COLS_NULL_FLAG)

    # 3. Separar X e y
    X = df.drop(columns=[TARGET_COL] + COLS_TO_DROP, errors="ignore")
    y = df[TARGET_COL]

    # 4. Split PRIMERO — regla crítica
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    print(f"Train: {X_train.shape} | Test: {X_test.shape}")

    # 5. Pipeline — fit solo en train
    preprocessor = build_pipeline()
    X_train_proc = preprocessor.fit_transform(X_train, y_train)
    X_test_proc  = preprocessor.transform(X_test)  # solo transform

    # 6. Obtener nombres de columnas del output
    feature_names = preprocessor.get_feature_names_out()

    # 7. Convertir a DataFrame y guardar
    train_df = pd.DataFrame(X_train_proc, columns=feature_names)
    train_df[TARGET_COL] = y_train.values
    test_df  = pd.DataFrame(X_test_proc, columns=feature_names)
    test_df[TARGET_COL]  = y_test.values

    train_df.to_parquet(TRAIN_OUTPUT, index=False)
    test_df.to_parquet(TEST_OUTPUT, index=False)
    print(f"Guardado: {TRAIN_OUTPUT} ({train_df.shape})")
    print(f"Guardado: {TEST_OUTPUT} ({test_df.shape})")

    return preprocessor, X_train_proc, X_test_proc, y_train, y_test


if __name__ == "__main__":
    run_pipeline()
