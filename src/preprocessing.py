"""
Preparación de datos para el modelo de churn.

Funciones reutilizables de limpieza, feature engineering y transformación.
Diseñadas para ser fit-on-train: las estadísticas (medianas, percentiles, categorías)
se calculan SOLO con train y se aplican a test, para evitar data leakage.

Pipeline lógico:
    1. clean_categories      -> unifica categorías inconsistentes (sin leakage)
    2. train_test_split      -> estratificado (en el notebook)
    3. fit_impute_values / apply_impute   -> mediana fit en train
    4. fit_outlier_caps / apply_caps      -> percentil 99 fit en train
    5. add_features          -> feature engineering row-wise (post-imputación)
    6. OneHotEncoder         -> fit en train (en el notebook)
"""
import pandas as pd

RANDOM_STATE = 42
TARGET = "Churn"
ID_COL = "CustomerID"

# Columnas numéricas con nulos (todas 4.5–5.5%) -> imputación por mediana
NUM_NULL_COLS = [
    "Tenure", "WarehouseToHome", "HourSpendOnApp",
    "OrderAmountHikeFromlastYear", "CouponUsed", "OrderCount", "DaySinceLastOrder",
]

# Columnas con outliers extremos en la cola derecha -> cap en percentil 99
OUTLIER_COLS = ["Tenure", "WarehouseToHome", "NumberOfAddress"]

# Categóricas nominales (sin orden natural) -> One-Hot Encoding
CAT_NOMINAL = [
    "PreferredLoginDevice", "PreferredPaymentMode", "Gender",
    "PreferedOrderCat", "MaritalStatus",
]


def clean_categories(df: pd.DataFrame) -> pd.DataFrame:
    """Unifica categorías que representan lo mismo escrito distinto.

    No usa estadísticas del dataset, así que es seguro aplicarlo antes del split.
    """
    df = df.copy()
    # Mismo medio de pago escrito de dos formas (ver decisions.md)
    df["PreferredPaymentMode"] = df["PreferredPaymentMode"].replace(
        {"CC": "Credit Card", "COD": "Cash on Delivery"}
    )
    # 'Phone' y 'Mobile Phone' son el mismo dispositivo
    df["PreferredLoginDevice"] = df["PreferredLoginDevice"].replace(
        {"Phone": "Mobile Phone"}
    )
    # 'Mobile' y 'Mobile Phone' son la misma categoría de producto
    df["PreferedOrderCat"] = df["PreferedOrderCat"].replace(
        {"Mobile": "Mobile Phone"}
    )
    return df


def fit_impute_values(train_df: pd.DataFrame, cols=NUM_NULL_COLS) -> dict:
    """Calcula la mediana de cada columna usando SOLO train."""
    return {c: float(train_df[c].median()) for c in cols}


def apply_impute(df: pd.DataFrame, values: dict) -> pd.DataFrame:
    """Imputa nulos con las medianas calculadas en train."""
    df = df.copy()
    for col, median in values.items():
        df[col] = df[col].fillna(median)
    return df


def fit_outlier_caps(train_df: pd.DataFrame, cols=OUTLIER_COLS, q: float = 0.99) -> dict:
    """Calcula el percentil `q` de cada columna usando SOLO train."""
    return {c: float(train_df[c].quantile(q)) for c in cols}


def apply_caps(df: pd.DataFrame, caps: dict) -> pd.DataFrame:
    """Cap-ea (winsoriza) los valores por encima del percentil calculado en train."""
    df = df.copy()
    for col, cap in caps.items():
        df[col] = df[col].clip(upper=cap)
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering row-wise (sin leakage; aplicar tras imputar).

    Variables derivadas de las hipótesis del EDA:
      - CashbackPerOrder : cashback promedio por orden (incentivo financiero, H5)
      - CouponPerOrder   : intensidad de uso de cupones por orden
      - AppHoursPerDevice: horas en app por dispositivo registrado (engagement)
      - IsNewCustomer    : cliente con <=3 meses de tenure (riesgo temprano, H1)
    """
    df = df.copy()
    # OrderCount tiene mínimo 1, no hay división por cero
    df["CashbackPerOrder"] = df["CashbackAmount"] / df["OrderCount"]
    df["CouponPerOrder"] = df["CouponUsed"] / df["OrderCount"]
    df["AppHoursPerDevice"] = df["HourSpendOnApp"] / df["NumberOfDeviceRegistered"]
    df["IsNewCustomer"] = (df["Tenure"] <= 3).astype(int)
    return df
