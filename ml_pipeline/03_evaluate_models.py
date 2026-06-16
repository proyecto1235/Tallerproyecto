#!/usr/bin/env python3
"""03_evaluate_models.py — Evaluate all models and generate metrics report.

Loads dataset + saved models.
Evaluates on temporal test set (target weeks 14-16).
Produces:
  - reports/metrics.json
  - reports/training_summary.md
"""

import os
import sys
import logging

import pandas as pd
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml_pipeline.src.windows import build_sliding_windows
from ml_pipeline.src.metrics import (
    evaluate_regression,
    evaluate_binary_classification,
    evaluate_multiclass_classification,
    save_metrics_json,
    save_training_summary,
)
from ml_pipeline.src.export import load_model, load_scaler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DATA_DIR = "data"
PARQUET_PATH = os.path.join(DATA_DIR, "robolearn_dataset.parquet")


def main():
    logger.info("Loading dataset...")
    df = pd.read_parquet(PARQUET_PATH)

    logger.info("Building sliding windows for evaluation...")
    windows = build_sliding_windows(df)

    metrics: dict = {}

    # --- Engagement ---
    logger.info("Evaluating EngagementPredictor...")
    model = load_model("engagement")
    scaler = load_scaler("engagement")
    X_test, y_test = windows["engagement"]["test"]
    if len(X_test) > 0 and model is not None:
        X_test_scaled = scaler.transform(X_test)
        metrics["engagement"] = evaluate_regression(model, X_test_scaled, y_test)
        logger.info(f"  R²={metrics['engagement']['r2']:.4f}")
    else:
        metrics["engagement"] = {"error": "no_test_data_or_model"}
        logger.warning("  Skipped (no data or model)")

    # --- Performance ---
    logger.info("Evaluating PerformancePredictor...")
    model = load_model("performance")
    scaler = load_scaler("performance")
    X_test, y_test = windows["performance"]["test"]
    if len(X_test) > 0 and model is not None:
        X_test_scaled = scaler.transform(X_test)
        metrics["performance"] = evaluate_regression(model, X_test_scaled, y_test)
        logger.info(f"  R²={metrics['performance']['r2']:.4f}")
    else:
        metrics["performance"] = {"error": "no_test_data_or_model"}
        logger.warning("  Skipped (no data or model)")

    # --- Dropout ---
    logger.info("Evaluating DropoutPredictor...")
    model = load_model("dropout")
    scaler = load_scaler("dropout")
    X_test, y_test = windows["dropout"]["test"]
    if len(X_test) > 0 and model is not None and len(np.unique(y_test)) >= 2:
        X_test_scaled = scaler.transform(X_test)
        metrics["dropout"] = evaluate_binary_classification(model, X_test_scaled, y_test)
        logger.info(f"  AUC={metrics['dropout'].get('roc_auc', 'N/A')}")
    else:
        metrics["dropout"] = {"error": "no_test_data_or_model"}
        logger.warning("  Skipped (no data/model/classes)")

    # --- Frustration ---
    logger.info("Evaluating FrustrationPredictor...")
    model = load_model("frustration")
    scaler = load_scaler("frustration")
    X_test, y_test = windows["frustration"]["test"]
    if len(X_test) > 0 and model is not None:
        X_test_scaled = scaler.transform(X_test)
        metrics["frustration"] = evaluate_multiclass_classification(
            model, X_test_scaled, y_test
        )
        logger.info(f"  Accuracy={metrics['frustration']['accuracy']:.4f}")
    else:
        metrics["frustration"] = {"error": "no_test_data_or_model"}
        logger.warning("  Skipped (no data or model)")

    # --- Save reports ---
    json_path = save_metrics_json(metrics)
    logger.info(f"Metrics saved: {json_path}")

    md_path = save_training_summary(metrics)
    logger.info(f"Summary saved: {md_path}")

    logger.info("Evaluation complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
