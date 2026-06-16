"""Evaluation metrics for all models.

Produces reports/metrics.json in the format:
{
  "engagement": { "mae": ..., "rmse": ..., "r2": ... },
  "performance": { ... },
  "dropout": { "accuracy": ..., "precision": ..., "recall": ..., "f1": ..., "roc_auc": ..., "classification_report": ..., "confusion_matrix": ... },
  "frustration": { ... },
  "clustering": { "silhouette_score": ..., "cluster_distribution": ... },
  "anomaly_detection": { "n_samples": ..., "n_anomalies": ..., "anomaly_rate": ... }
}
"""

import json
import os
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_absolute_error, mean_squared_error, r2_score,
    confusion_matrix, classification_report, silhouette_score,
)
from typing import Dict, Any

REPORTS_DIR = "reports"


def evaluate_regression(model, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
    y_pred = model.predict(X_test)
    return {
        "mae": round(float(mean_absolute_error(y_test, y_pred)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4),
        "r2": round(float(r2_score(y_test, y_pred)), 4),
    }


def evaluate_binary_classification(
    model, X_test: np.ndarray, y_test: np.ndarray,
) -> Dict[str, Any]:
    y_pred = model.predict(X_test)
    result: Dict[str, Any] = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "classification_report": classification_report(
            y_test, y_pred, output_dict=True, zero_division=0
        ),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }
    if len(np.unique(y_test)) == 2:
        y_proba = model.predict_proba(X_test)[:, 1]
        result["precision"] = round(
            float(precision_score(y_test, y_pred, zero_division=0)), 4
        )
        result["recall"] = round(
            float(recall_score(y_test, y_pred, zero_division=0)), 4
        )
        result["f1"] = round(
            float(f1_score(y_test, y_pred, zero_division=0)), 4
        )
        try:
            result["roc_auc"] = round(float(roc_auc_score(y_test, y_proba)), 4)
        except Exception:
            result["roc_auc"] = 0.5
    return result


def evaluate_multiclass_classification(
    model, X_test: np.ndarray, y_test: np.ndarray,
) -> Dict[str, Any]:
    y_pred = model.predict(X_test)
    return {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "classification_report": classification_report(
            y_test, y_pred, output_dict=True, zero_division=0
        ),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }


def evaluate_clustering(model, scaler, X: np.ndarray) -> Dict[str, Any]:
    X_scaled = scaler.transform(X)
    labels = model.predict(X_scaled)
    sil = silhouette_score(X_scaled, labels) if len(np.unique(labels)) > 1 else 0.0
    cluster_counts = {}
    for i in range(model.n_clusters):
        cluster_counts[f"cluster_{i}"] = int(np.sum(labels == i))
    return {
        "silhouette_score": round(float(sil), 4),
        "n_clusters": model.n_clusters,
        "cluster_distribution": cluster_counts,
        "n_samples": len(X),
    }


def evaluate_anomaly(model, scaler, X: np.ndarray) -> Dict[str, Any]:
    X_scaled = scaler.transform(X)
    preds = model.predict(X_scaled)
    n_anomalies = int(np.sum(preds == -1))
    return {
        "n_samples": len(X),
        "n_anomalies": n_anomalies,
        "anomaly_rate": round(n_anomalies / len(X), 4) if len(X) > 0 else 0.0,
    }


def save_metrics_json(metrics: Dict[str, Any]) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, "metrics.json")
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)
    return path


def save_training_summary(metrics: Dict[str, Any]) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    path = os.path.join(REPORTS_DIR, "training_summary.md")
    lines = ["# RoboLearn — ML Pipeline Training Summary\n"]

    for model_name, data in metrics.items():
        lines.append(f"\n## {model_name.capitalize()}\n")
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, float):
                    lines.append(f"- **{k}**: {v:.4f}")
                elif isinstance(v, dict) and "mae" in v:
                    for sk, sv in v.items():
                        if isinstance(sv, float):
                            lines.append(f"- **{sk}**: {sv:.4f}")
                        else:
                            lines.append(f"- **{sk}**: {sv}")
                else:
                    lines.append(f"- **{k}**: {v}")

    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path
