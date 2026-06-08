"""
Model Training Script — Template
Generado por ds-model skill

USO:
    python src/models/train.py

REPRODUCE el entrenamiento completo end-to-end con seeds fijos.
"""

import pandas as pd
import numpy as np
import pickle
import csv
import os
from pathlib import Path

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (
    f1_score, recall_score, precision_score,
    average_precision_score, make_scorer
)
from sklearn.pipeline import Pipeline

# ── Configuración ──────────────────────────────────────────────────────────────
TRAIN_PATH   = "data/processed/features_train.parquet"
TEST_PATH    = "data/processed/features_test.parquet"
TARGET_COL   = "target"  # cambiar según dataset
RANDOM_STATE = 42
CV_FOLDS     = 5
MODELS_DIR   = Path("models")
RUNS_LOG     = "reports/runs_log.csv"

# Criterio de selección del ganador — ESCRITO ANTES DE VER RESULTADOS
# Cambiar según la spec del proyecto
WINNER_METRIC   = "recall"   # métrica que decide el ganador
WINNER_CRITERIA = "maximizar recall de clase positiva (costo FN > FP)"

MODELS_DIR.mkdir(exist_ok=True)

# ── Scoring ────────────────────────────────────────────────────────────────────
scoring = {
    "f1":        make_scorer(f1_score, zero_division=0),
    "recall":    make_scorer(recall_score, zero_division=0),
    "precision": make_scorer(precision_score, zero_division=0),
    "pr_auc":    make_scorer(average_precision_score, needs_proba=True),
}

# ── Candidatos ────────────────────────────────────────────────────────────────
# Importar el pipeline del Feature Agent
# from src.features.pipeline import build_pipeline
# preprocessor = build_pipeline()

def get_candidates(preprocessor=None):
    """
    Define los modelos candidatos.
    Cada uno es un Pipeline completo con el mismo preprocessor.
    Modificar según la propuesta aprobada en Fase 1.
    """
    candidates = {
        "dummy_baseline": DummyClassifier(strategy="most_frequent"),
        "logistic": Pipeline([
            # ("preprocessor", preprocessor),  # descomentar si se usa
            ("clf", LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
                random_state=RANDOM_STATE,
            )),
        ]),
        "random_forest": Pipeline([
            # ("preprocessor", preprocessor),
            ("clf", RandomForestClassifier(
                class_weight="balanced",
                n_estimators=100,
                random_state=RANDOM_STATE,
                n_jobs=-1,
            )),
        ]),
        # Agregar más modelos según la propuesta
    }
    return candidates


def evaluate_cv(candidates: dict, X_train, y_train) -> dict:
    """Evalúa todos los candidatos con CV estratificada."""
    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    results = {}

    for name, model in candidates.items():
        print(f"  Evaluando {name}...")
        cv_results = cross_validate(
            model, X_train, y_train,
            cv=cv,
            scoring=scoring,
            return_train_score=True,
            n_jobs=-1,
        )
        results[name] = {
            metric: {
                "mean": cv_results[f"test_{metric}"].mean(),
                "std":  cv_results[f"test_{metric}"].std(),
            }
            for metric in scoring
        }
        results[name]["fit_time"] = cv_results["fit_time"].mean()

    return results


def log_runs(results: dict, log_path: str):
    """Guarda los resultados de CV en un CSV."""
    rows = []
    for name, metrics in results.items():
        row = {"modelo": name}
        for metric, vals in metrics.items():
            if isinstance(vals, dict):
                row[f"{metric}_mean"] = round(vals["mean"], 4)
                row[f"{metric}_std"]  = round(vals["std"], 4)
            else:
                row[metric] = round(vals, 4)
        rows.append(row)

    fieldnames = rows[0].keys()
    with open(log_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Runs log guardado: {log_path}")


def select_winner(results: dict, metric: str = WINNER_METRIC) -> str:
    """
    Aplica el criterio escrito en la Spec para elegir el ganador.
    NO se elige mirando los resultados — se aplica el criterio predefinido.
    """
    # Excluir el dummy baseline de la elección del ganador
    candidates = {k: v for k, v in results.items() if k != "dummy_baseline"}
    winner = max(candidates, key=lambda m: candidates[m][metric]["mean"])
    return winner


def evaluate_test(model, X_test, y_test) -> dict:
    """
    Evaluación final en test set.
    LLAMAR UNA SOLA VEZ — al final de todo.
    """
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None

    metrics = {
        "f1":        round(f1_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred, zero_division=0), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "pr_auc":    round(average_precision_score(y_test, y_prob), 4) if y_prob is not None else None,
    }
    return metrics


def main():
    # ── Carga ──────────────────────────────────────────────────────────────────
    print("Cargando datos procesados...")
    train_df = pd.read_parquet(TRAIN_PATH)
    test_df  = pd.read_parquet(TEST_PATH)

    X_train = train_df.drop(columns=[TARGET_COL])
    y_train = train_df[TARGET_COL]
    X_test  = test_df.drop(columns=[TARGET_COL])
    y_test  = test_df[TARGET_COL]

    print(f"Train: {X_train.shape} | Test: {X_test.shape}")
    print(f"Desbalance train: {y_train.value_counts(normalize=True).to_dict()}")

    # ── CV ─────────────────────────────────────────────────────────────────────
    print(f"\nEvaluando candidatos con CV estratificada ({CV_FOLDS} folds)...")
    candidates = get_candidates()
    results = evaluate_cv(candidates, X_train, y_train)
    log_runs(results, RUNS_LOG)

    # ── Selección del ganador ──────────────────────────────────────────────────
    print(f"\nCriterio de selección: {WINNER_CRITERIA}")
    winner_name = select_winner(results, WINNER_METRIC)
    print(f"Ganador: {winner_name}")
    print(f"  {WINNER_METRIC}: {results[winner_name][WINNER_METRIC]['mean']:.4f} ± {results[winner_name][WINNER_METRIC]['std']:.4f}")

    # ── Fit final del ganador en todo train ────────────────────────────────────
    winner_model = candidates[winner_name]
    winner_model.fit(X_train, y_train)

    # ── Serializar ─────────────────────────────────────────────────────────────
    model_path = MODELS_DIR / f"{winner_name}.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(winner_model, f)
    print(f"Modelo guardado: {model_path}")

    # También guardar baseline
    baseline = candidates["dummy_baseline"]
    baseline.fit(X_train, y_train)
    with open(MODELS_DIR / "dummy_baseline.pkl", "wb") as f:
        pickle.dump(baseline, f)

    # ── Evaluación en test — UNA SOLA VEZ ─────────────────────────────────────
    print("\n" + "="*50)
    print("EVALUACIÓN FINAL EN TEST SET (una sola vez)")
    print("="*50)
    test_metrics = evaluate_test(winner_model, X_test, y_test)
    for metric, val in test_metrics.items():
        print(f"  {metric}: {val}")

    baseline_test = evaluate_test(baseline, X_test, y_test)
    print(f"\nBaseline en test: {baseline_test}")

    return winner_model, results, test_metrics


if __name__ == "__main__":
    main()
