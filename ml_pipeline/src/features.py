"""Feature extraction functions for all ML models.

All functions use only observable features (FEATURE_NAMES) as input.
No target variables leak into feature vectors.
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple

from ml_pipeline.src.dataset import FEATURE_NAMES


def _frustration_class(fr_score: float) -> int:
    if fr_score > 0.6:
        return 2
    if fr_score > 0.35:
        return 1
    return 0


def _window_features_flat(df: pd.DataFrame) -> np.ndarray | None:
    """Extract flat feature vector from a 4-week sorted window (regression models)."""
    if len(df) < 4:
        return None
    return df[FEATURE_NAMES].values.flatten()


def _window_features_mean(df: pd.DataFrame) -> np.ndarray | None:
    """Extract mean feature vector from a 4-week window (classification models)."""
    if len(df) < 4:
        return None
    return df[FEATURE_NAMES].mean(axis=0).values


def extract_for_engagement(
    df: pd.DataFrame, student_id: int, target_week: int = 5
) -> Tuple[Optional[np.ndarray], Optional[float]]:
    window = df[
        (df["student_id"] == student_id)
        & (df["week"] < target_week)
        & (df["week"] >= target_week - 4)
    ].sort_values("week")
    if len(window) < 4:
        return None, None
    target_row = df[
        (df["student_id"] == student_id) & (df["week"] == target_week)
    ]
    if len(target_row) == 0:
        return None, None
    features = window[FEATURE_NAMES].values.flatten()
    target = target_row["engagement_score"].values[0]
    return features, target


def extract_for_performance(
    df: pd.DataFrame, student_id: int, target_week: int = 5
) -> Tuple[Optional[np.ndarray], Optional[float]]:
    window = df[
        (df["student_id"] == student_id)
        & (df["week"] < target_week)
        & (df["week"] >= target_week - 4)
    ].sort_values("week")
    if len(window) < 4:
        return None, None
    target_row = df[
        (df["student_id"] == student_id) & (df["week"] == target_week)
    ]
    if len(target_row) == 0:
        return None, None
    features = window[FEATURE_NAMES].values.flatten()
    target = target_row["performance_score"].values[0]
    return features, target


def extract_for_dropout(
    df: pd.DataFrame, student_id: int, target_week: int = 5
) -> Tuple[Optional[np.ndarray], Optional[int]]:
    window = df[
        (df["student_id"] == student_id)
        & (df["week"] < target_week)
        & (df["week"] >= target_week - 4)
    ].sort_values("week")
    if len(window) < 4:
        return None, None
    features = window[FEATURE_NAMES].mean(axis=0).values
    target_row = df[
        (df["student_id"] == student_id) & (df["week"] == target_week)
    ]
    if len(target_row) == 0:
        return None, None
    target = target_row["dropout"].values[0]
    return features, target


def extract_for_frustration(
    df: pd.DataFrame, student_id: int, target_week: int = 5
) -> Tuple[Optional[np.ndarray], Optional[int]]:
    window = df[
        (df["student_id"] == student_id)
        & (df["week"] < target_week)
        & (df["week"] >= target_week - 4)
    ].sort_values("week")
    if len(window) < 4:
        return None, None
    features = window[FEATURE_NAMES].mean(axis=0).values
    target_row = df[
        (df["student_id"] == student_id) & (df["week"] == target_week)
    ]
    if len(target_row) == 0:
        return None, None
    fr_score = target_row["frustration_score"].values[0]
    target = _frustration_class(fr_score)
    return features, target


def extract_for_clustering(
    df: pd.DataFrame, student_id: int
) -> Optional[np.ndarray]:
    student_data = df[df["student_id"] == student_id]
    if len(student_data) == 0:
        return None
    return student_data[FEATURE_NAMES].mean(axis=0).values


def extract_for_anomaly(
    df: pd.DataFrame, student_id: int, window_size: int = 4
) -> Optional[np.ndarray]:
    student_data = df[df["student_id"] == student_id].sort_values("week")
    if len(student_data) < window_size + 1:
        return None
    recent = student_data.tail(window_size + 1)
    deltas = []
    for i in range(1, len(recent)):
        delta = (
            recent.iloc[i][FEATURE_NAMES].values
            - recent.iloc[i - 1][FEATURE_NAMES].values
        )
        deltas.append(delta)
    return np.array(deltas).flatten()
