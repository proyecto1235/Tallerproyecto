#!/usr/bin/env python3
"""02_train_models.py — Train 4 supervised ML models using sliding windows.

Loads dataset from data/robolearn_dataset.parquet.
Builds 12 sliding windows with temporal split (train: weeks 5-13, test: weeks 14-16).
Trains: Engagement, Performance (RandomForestRegressor),
         Dropout, Frustration (RandomForestClassifier).
Saves model + scaler + features.json to models/ for each predictor.
"""

import os
import sys
import logging

import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml_pipeline.src.windows import build_sliding_windows
from ml_pipeline.src.models import (
    train_engagement,
    train_performance,
    train_dropout,
    train_frustration,
    FEATURE_NAMES_ENG_PERF,
    FEATURE_NAMES_CLF,
)
from ml_pipeline.src.export import save_model

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
    logger.info(f"Loaded {len(df):,} rows, {df['student_id'].nunique():,} students")

    logger.info("Building sliding windows (12 windows, temporal split)...")
    windows = build_sliding_windows(df)
    for task, splits in windows.items():
        n_train = len(splits["train"][0])
        n_test = len(splits["test"][0])
        logger.info(f"  {task}: train={n_train}, test={n_test}")

    # --- Engagement ---
    logger.info("Training EngagementPredictor (RandomForestRegressor)...")
    X_train, y_train = windows["engagement"]["train"]
    model, scaler = train_engagement(X_train, y_train)
    save_model(model, scaler, FEATURE_NAMES_ENG_PERF, "engagement")
    logger.info("  Saved engagement_model.pkl + scaler + features")

    # --- Performance ---
    logger.info("Training PerformancePredictor (RandomForestRegressor)...")
    X_train, y_train = windows["performance"]["train"]
    model, scaler = train_performance(X_train, y_train)
    save_model(model, scaler, FEATURE_NAMES_ENG_PERF, "performance")
    logger.info("  Saved performance_model.pkl + scaler + features")

    # --- Dropout ---
    logger.info("Training DropoutPredictor (RandomForestClassifier)...")
    X_train, y_train = windows["dropout"]["train"]
    model, scaler = train_dropout(X_train, y_train)
    save_model(model, scaler, FEATURE_NAMES_CLF, "dropout")
    logger.info("  Saved dropout_model.pkl + scaler + features")

    # --- Frustration ---
    logger.info("Training FrustrationPredictor (RandomForestClassifier)...")
    X_train, y_train = windows["frustration"]["train"]
    model, scaler = train_frustration(X_train, y_train)
    save_model(model, scaler, FEATURE_NAMES_CLF, "frustration")
    logger.info("  Saved frustration_model.pkl + scaler + features")

    logger.info("Supervised training complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
