#!/usr/bin/env python3
"""04_train_unsupervised.py — Train KMeans clustering and IsolationForest anomaly detection.

Loads dataset from data/robolearn_dataset.parquet.
Trains:
  - KMeans(n_clusters=4) + StandardScaler + PCA(2)
  - IsolationForest + StandardScaler
Saves models to models/.
Appends evaluation to reports/metrics.json.
"""

import json
import os
import sys
import logging

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
import joblib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml_pipeline.src.dataset import FEATURE_NAMES
from ml_pipeline.src.features import extract_for_clustering, extract_for_anomaly
from ml_pipeline.src.metrics import (
    evaluate_clustering,
    evaluate_anomaly,
)
from ml_pipeline.src.export import save_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DATA_DIR = "data"
PARQUET_PATH = os.path.join(DATA_DIR, "robolearn_dataset.parquet")
MODEL_DIR = "models"
REPORTS_DIR = "reports"


def main():
    logger.info("Loading dataset...")
    df = pd.read_parquet(PARQUET_PATH)
    student_ids = df["student_id"].unique()

    # --- Prepare features ---
    cluster_X_list = []
    for sid in student_ids:
        feats = extract_for_clustering(df, sid)
        if feats is not None:
            cluster_X_list.append(feats)
    cluster_X = np.array(cluster_X_list)
    logger.info(f"Clustering features: {cluster_X.shape}")

    anomaly_X_list = []
    for sid in student_ids:
        deltas = extract_for_anomaly(df, sid)
        if deltas is not None:
            anomaly_X_list.append(deltas)
    anomaly_X = np.array(anomaly_X_list)
    logger.info(f"Anomaly features: {anomaly_X.shape}")

    # --- KMeans Clustering ---
    logger.info("Training KMeans(n_clusters=4)...")
    cluster_scaler = StandardScaler()
    X_scaled = cluster_scaler.fit_transform(cluster_X)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    kmeans.fit(X_scaled)

    pca = PCA(n_components=2, random_state=42)
    pca.fit(X_scaled)

    joblib.dump(kmeans, os.path.join(MODEL_DIR, "cluster_model.pkl"))
    joblib.dump(cluster_scaler, os.path.join(MODEL_DIR, "cluster_scaler.pkl"))
    joblib.dump(pca, os.path.join(MODEL_DIR, "cluster_pca.pkl"))
    logger.info("Saved cluster_model.pkl + cluster_scaler.pkl + cluster_pca.pkl")

    cluster_metrics = evaluate_clustering(kmeans, cluster_scaler, cluster_X)
    logger.info(f"  Silhouette: {cluster_metrics['silhouette_score']:.4f}")
    logger.info(f"  Distribution: {cluster_metrics['cluster_distribution']}")

    # --- IsolationForest ---
    logger.info("Training IsolationForest...")
    anomaly_scaler = StandardScaler()
    X_anom_scaled = anomaly_scaler.fit_transform(anomaly_X)

    iso = IsolationForest(
        n_estimators=200,
        contamination=0.1,
        random_state=42,
        n_jobs=-1,
    )
    iso.fit(X_anom_scaled)

    joblib.dump(iso, os.path.join(MODEL_DIR, "anomaly_model.pkl"))
    joblib.dump(anomaly_scaler, os.path.join(MODEL_DIR, "anomaly_scaler.pkl"))
    logger.info("Saved anomaly_model.pkl + anomaly_scaler.pkl")

    anomaly_metrics = evaluate_anomaly(iso, anomaly_scaler, anomaly_X)
    logger.info(f"  Anomalies: {anomaly_metrics['n_anomalies']} ({anomaly_metrics['anomaly_rate']*100:.1f}%)")

    # --- Append to metrics.json ---
    os.makedirs(REPORTS_DIR, exist_ok=True)
    metrics_path = os.path.join(REPORTS_DIR, "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            all_metrics = json.load(f)
    else:
        all_metrics = {}

    all_metrics["clustering"] = cluster_metrics
    all_metrics["anomaly_detection"] = anomaly_metrics

    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2)
    logger.info(f"Updated: {metrics_path}")

    logger.info("Unsupervised training complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
