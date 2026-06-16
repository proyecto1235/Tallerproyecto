"""Model training functions for all supervised ML models."""

import os
import numpy as np
from sklearn.ensemble import (
    RandomForestRegressor,
    RandomForestClassifier,
)
from sklearn.preprocessing import StandardScaler
from typing import Tuple

# Use N_ESTIMATORS env var or default to 100 for reasonable pipeline speed
_N_ESTIMATORS = int(os.environ.get("ML_N_ESTIMATORS", "100"))
_MAX_DEPTH_REG = int(os.environ.get("ML_MAX_DEPTH", "15"))

FEATURE_NAMES_ENG_PERF: list[str] = [
    "session_days_w1", "total_sessions_w1", "total_time_minutes_w1",
    "exercise_attempts_w1", "passed_exercises_w1", "error_rate_w1",
    "forum_interactions_w1", "content_views_w1",
    "session_days_w2", "total_sessions_w2", "total_time_minutes_w2",
    "exercise_attempts_w2", "passed_exercises_w2", "error_rate_w2",
    "forum_interactions_w2", "content_views_w2",
    "session_days_w3", "total_sessions_w3", "total_time_minutes_w3",
    "exercise_attempts_w3", "passed_exercises_w3", "error_rate_w3",
    "forum_interactions_w3", "content_views_w3",
    "session_days_w4", "total_sessions_w4", "total_time_minutes_w4",
    "exercise_attempts_w4", "passed_exercises_w4", "error_rate_w4",
    "forum_interactions_w4", "content_views_w4",
]

FEATURE_NAMES_CLF: list[str] = [
    "session_days_mean", "total_sessions_mean", "total_time_minutes_mean",
    "exercise_attempts_mean", "passed_exercises_mean", "error_rate_mean",
    "forum_interactions_mean", "content_views_mean",
]


def train_engagement(
    X_train: np.ndarray, y_train: np.ndarray,
) -> Tuple[RandomForestRegressor, StandardScaler]:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = RandomForestRegressor(
        n_estimators=_N_ESTIMATORS, max_depth=_MAX_DEPTH_REG, random_state=42, n_jobs=-1,
    )
    model.fit(X_scaled, y_train)
    return model, scaler


def train_performance(
    X_train: np.ndarray, y_train: np.ndarray,
) -> Tuple[RandomForestRegressor, StandardScaler]:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = RandomForestRegressor(
        n_estimators=_N_ESTIMATORS, max_depth=_MAX_DEPTH_REG, random_state=42, n_jobs=-1,
    )
    model.fit(X_scaled, y_train)
    return model, scaler


def train_dropout(
    X_train: np.ndarray, y_train: np.ndarray,
) -> Tuple[RandomForestClassifier, StandardScaler]:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = RandomForestClassifier(
        n_estimators=_N_ESTIMATORS, max_depth=10, random_state=42,
        class_weight="balanced", n_jobs=-1,
    )
    model.fit(X_scaled, y_train)
    return model, scaler


def train_frustration(
    X_train: np.ndarray, y_train: np.ndarray,
) -> Tuple[RandomForestClassifier, StandardScaler]:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    model = RandomForestClassifier(
        n_estimators=_N_ESTIMATORS, max_depth=10, random_state=42,
        class_weight="balanced", n_jobs=-1,
    )
    model.fit(X_scaled, y_train)
    return model, scaler
