"""Reproducible training script for the churn model.

Entrena el ganador (RandomForest V1 tuneado) sobre `data/processed/train_sin_complain.csv`,
evalúa en `test_sin_complain.csv` y serializa el modelo en `models/`.

Decisiones de modelado (todas documentadas en `decisions.md`):
  - Dataset: SIN Complain (postura conservadora por riesgo de leakage no validable)
  - Métrica primaria: Recall (clase 1 = Churn)
  - Cross-validation: StratifiedKFold(5, random_state=42)
  - Ganador: RandomForest V1 tuneado (n_estimators=1469, max_depth=50,
    min_samples_leaf=3, max_features=0.978) elegido tras 3 rondas iterativas
    de BayesSearchCV (ver notebook 03 secciones 16-20).
    Lift vs defaults: +2.34% Recall CV, con MENOR gap train-CV (0.1371 vs 0.1569).
  - Test set tocado dos veces (defaults primero, V1 después) — documentado
    como limitación en notebook 03 sección 20.

Uso:
    python src/models/train.py
"""
from __future__ import annotations

import pickle
from pathlib import Path
import time

import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (
    f1_score, recall_score, precision_score, average_precision_score,
    roc_auc_score, classification_report, confusion_matrix,
)

RANDOM_STATE = 42
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)


def load_data():
    train = pd.read_csv(DATA_DIR / "train_sin_complain.csv")
    test = pd.read_csv(DATA_DIR / "test_sin_complain.csv")
    return train, test


def evaluate_cv(model, X, y) -> dict:
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    scoring = ["recall", "precision", "f1", "average_precision", "roc_auc"]
    results = cross_validate(model, X, y, cv=cv, scoring=scoring, n_jobs=-1)
    return {
        "recall_mean": results["test_recall"].mean(),
        "recall_std": results["test_recall"].std(),
        "precision_mean": results["test_precision"].mean(),
        "f1_mean": results["test_f1"].mean(),
        "pr_auc_mean": results["test_average_precision"].mean(),
        "roc_auc_mean": results["test_roc_auc"].mean(),
    }


def evaluate_test(model, X_test, y_test) -> dict:
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    return {
        "recall": recall_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
        "pr_auc": average_precision_score(y_test, y_proba),
        "roc_auc": roc_auc_score(y_test, y_proba),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "classification_report": classification_report(y_test, y_pred,
                                                       target_names=["Activo", "Churneo"]),
    }


def main() -> None:
    print("=== Churn TP — train pipeline ===\n")

    train, test = load_data()
    X_train = train.drop(columns=["Churn"])
    y_train = train["Churn"]
    X_test = test.drop(columns=["Churn"])
    y_test = test["Churn"]
    print(f"Train: {train.shape[0]:,} x {train.shape[1]}")
    print(f"Test:  {test.shape[0]:,} x {test.shape[1]}")
    print(f"Churn rate train: {y_train.mean()*100:.2f}%")

    # Baseline (referencia)
    print("\n[1/3] Baseline (DummyClassifier)")
    dummy = DummyClassifier(strategy="most_frequent", random_state=RANDOM_STATE)
    dummy_cv = evaluate_cv(dummy, X_train, y_train)
    print(f"  Recall CV: {dummy_cv['recall_mean']:.4f}")

    # Ganador: RandomForest V1 tuneado (documentado en decisions.md y notebook 03)
    print("\n[2/3] Ganador (RandomForest V1 tuneado) — CV en train")
    winner = RandomForestClassifier(
        n_estimators=1469,
        max_depth=50,
        min_samples_leaf=3,
        max_features=0.978,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    t0 = time.time()
    winner_cv = evaluate_cv(winner, X_train, y_train)
    cv_time = time.time() - t0
    print(f"  Recall CV: {winner_cv['recall_mean']:.4f} +/- {winner_cv['recall_std']:.4f}")
    print(f"  PR-AUC CV: {winner_cv['pr_auc_mean']:.4f}")
    print(f"  Tiempo CV: {cv_time:.1f}s")

    # Test set: una sola vez al final
    print("\n[3/3] Evaluacion final en test (una sola vez)")
    winner.fit(X_train, y_train)
    test_metrics = evaluate_test(winner, X_test, y_test)
    print(f"  Recall:    {test_metrics['recall']:.4f}")
    print(f"  Precision: {test_metrics['precision']:.4f}")
    print(f"  F1:        {test_metrics['f1']:.4f}")
    print(f"  PR-AUC:    {test_metrics['pr_auc']:.4f}")
    print(f"  AUC-ROC:   {test_metrics['roc_auc']:.4f}")
    cm = test_metrics["confusion_matrix"]
    print(f"  Matriz de confusion: TN={cm[0][0]}, FP={cm[0][1]}, FN={cm[1][0]}, TP={cm[1][1]}")

    # Serializar (gitignored)
    winner_path = MODELS_DIR / "RandomForest_V1_winner.pkl"
    dummy_fit = dummy.fit(X_train, y_train)
    dummy_path = MODELS_DIR / "dummy_baseline.pkl"
    pickle.dump(winner, open(winner_path, "wb"))
    pickle.dump(dummy_fit, open(dummy_path, "wb"))
    print(f"\nModelos serializados:")
    print(f"  {winner_path}")
    print(f"  {dummy_path}")


if __name__ == "__main__":
    main()
