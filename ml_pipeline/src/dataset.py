"""Longitudinal synthetic dataset generation for RoboLearn ML pipeline."""

import numpy as np
import pandas as pd
from scipy.special import expit as sigmoid
from typing import Dict, Tuple

N_STUDENTS = 10_000
N_WEEKS = 16
RANDOM_SEED = 42

ARCHETYPES: Dict[str, Dict] = {
    "high": {
        "weight": 0.30,
        "ability": (0.90, 0.06),
        "motivation": (0.92, 0.06),
        "diligence": (0.90, 0.06),
        "dropout_bias": -9.0,
    },
    "medium": {
        "weight": 0.40,
        "ability": (0.75, 0.08),
        "motivation": (0.78, 0.08),
        "diligence": (0.75, 0.08),
        "dropout_bias": -8.0,
    },
    "low": {
        "weight": 0.15,
        "ability": (0.65, 0.09),
        "motivation": (0.65, 0.09),
        "diligence": (0.65, 0.09),
        "dropout_bias": -8.0,
    },
    "burnout": {
        "weight": 0.15,
        "ability": (0.82, 0.08),
        "motivation": (0.85, 0.08),
        "diligence": (0.82, 0.08),
        "dropout_bias": -8.0,
    },
}

FEATURE_NAMES: list[str] = [
    "session_days", "total_sessions", "total_time_minutes",
    "exercise_attempts", "passed_exercises", "error_rate",
    "forum_interactions", "content_views",
]

TARGET_NAMES: list[str] = [
    "engagement_score", "frustration_score", "performance_score",
    "dropout_prob", "dropout",
]


def generate_dataset(
    n_students: int = N_STUDENTS,
    n_weeks: int = N_WEEKS,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    archetype_names = list(ARCHETYPES.keys())
    archetype_weights = [ARCHETYPES[a]["weight"] for a in archetype_names]
    archetype_assignments = rng.choice(
        archetype_names, size=n_students, p=archetype_weights
    )

    student_ids = np.repeat(np.arange(1, n_students + 1), n_weeks)
    weeks = np.tile(np.arange(1, n_weeks + 1), n_students)
    archetypes = np.repeat(archetype_assignments, n_weeks)

    ability = np.zeros(n_students * n_weeks)
    motivation = np.zeros(n_students * n_weeks)
    diligence = np.zeros(n_students * n_weeks)
    dropout_bias = np.zeros(n_students * n_weeks)

    for name in archetype_names:
        mask = archetypes == name
        n_mask = np.sum(mask) // n_weeks
        params = ARCHETYPES[name]
        base_ability = rng.normal(params["ability"][0], params["ability"][1], n_mask)
        base_motivation = rng.normal(
            params["motivation"][0], params["motivation"][1], n_mask
        )
        base_diligence = rng.normal(
            params["diligence"][0], params["diligence"][1], n_mask
        )
        ability[mask] = np.clip(np.repeat(base_ability, n_weeks), 0.05, 0.95)
        motivation[mask] = np.clip(np.repeat(base_motivation, n_weeks), 0.05, 0.95)
        diligence[mask] = np.clip(np.repeat(base_diligence, n_weeks), 0.05, 0.95)
        dropout_bias[mask] = np.repeat(
            np.full(n_mask, params["dropout_bias"]), n_weeks
        )

    week_float = weeks.astype(float)
    fatigue = np.minimum(1.0, week_float / 12.0)

    burnout_effect = np.where(
        (archetypes == "burnout") & (weeks > 8),
        (week_float - 8) * 0.12,
        0.0,
    )
    burnout_diligence = np.clip(diligence - burnout_effect * 0.2, 0.01, 0.95)
    burnout_motivation = np.clip(motivation - burnout_effect * 0.25, 0.01, 0.95)
    burnout_ability = np.clip(ability - burnout_effect * 0.10, 0.01, 0.95)

    effective_diligence = np.where(
        archetypes == "burnout", burnout_diligence, diligence
    )
    effective_motivation = np.where(
        archetypes == "burnout", burnout_motivation, motivation
    )
    effective_ability = np.where(archetypes == "burnout", burnout_ability, ability)

    session_days = rng.poisson(effective_diligence * 7).astype(float)
    session_days = np.clip(session_days, 0, 7)
    total_sessions = np.maximum(
        1,
        np.round(
            rng.gamma(3, 2, size=n_students * n_weeks) * effective_ability
        ).astype(float),
    )
    total_sessions = np.clip(total_sessions, 0, 50)
    total_time_minutes = total_sessions * (
        20 + rng.gamma(2, 10, size=n_students * n_weeks)
    )
    total_time_minutes = np.clip(total_time_minutes, 0, 3000)
    exercise_attempts = np.maximum(
        0, np.round(rng.normal(effective_motivation * 25, 8)).astype(float)
    )
    exercise_attempts = np.clip(exercise_attempts, 0, 80)

    fatigue_penalty = np.clip(
        1.0 - fatigue * 0.3 * (1 - effective_ability), 0.3, 1.0
    )
    pass_prob = np.clip(effective_ability * fatigue_penalty, 0.01, 0.99)
    passed_exercises = rng.binomial(
        exercise_attempts.astype(np.int64), pass_prob
    ).astype(float)
    passed_exercises = np.clip(passed_exercises, 0, exercise_attempts)

    error_rate = np.clip(
        1.0
        - effective_ability * fatigue_penalty
        + rng.normal(0, 0.05, n_students * n_weeks),
        0.0,
        1.0,
    )
    forum_interactions = np.maximum(
        0, np.round(rng.poisson(effective_motivation * 3)).astype(float)
    )
    forum_interactions = np.clip(forum_interactions, 0, 20)
    content_views = np.maximum(
        0, np.round(rng.poisson(effective_diligence * 7)).astype(float)
    )
    content_views = np.clip(content_views, 0, 30)

    df = pd.DataFrame(
        {
            "student_id": student_ids,
            "week": weeks,
            "archetype": archetypes,
            "session_days": session_days.astype(np.int32),
            "total_sessions": total_sessions.astype(np.int32),
            "total_time_minutes": total_time_minutes.astype(np.float32),
            "exercise_attempts": exercise_attempts.astype(np.int32),
            "passed_exercises": passed_exercises.astype(np.int32),
            "error_rate": error_rate.astype(np.float32),
            "forum_interactions": forum_interactions.astype(np.int32),
            "content_views": content_views.astype(np.int32),
        }
    )

    _compute_latent_variables(df)
    _apply_dropout(df)

    return df


def _compute_latent_variables(df: pd.DataFrame) -> None:
    passed_ratio = np.where(
        df["exercise_attempts"] > 0,
        df["passed_exercises"] / df["exercise_attempts"],
        0.0,
    )
    failed_ratio = 1.0 - passed_ratio
    fatigue = np.minimum(1.0, df["week"] / 12.0)

    z_session = _zscore(df["session_days"].values)
    z_time = _zscore(df["total_time_minutes"].values)
    z_passed = _zscore(passed_ratio)
    z_content = _zscore(df["content_views"].values)
    z_forum = _zscore(df["forum_interactions"].values)
    z_error = _zscore(df["error_rate"].values)
    z_failed = _zscore(failed_ratio)
    z_fatigue = _zscore(fatigue)

    engagement = sigmoid(
        0.50 * z_session
        + 0.40 * z_time
        + 0.40 * z_passed
        + 0.25 * z_content
        + 0.20 * z_forum
        + 2.80
        + np.random.normal(0, 0.03, len(df))
    )
    z_engagement = _zscore(engagement)

    frustration = sigmoid(
        0.25 * z_error
        + 0.20 * z_failed
        - 0.30 * z_engagement
        + 0.10 * z_fatigue
        - 0.20
        + np.random.normal(0, 0.05, len(df))
    )
    _zscore(frustration)

    performance = sigmoid(
        0.45 * z_passed
        + 0.35 * _zscore(engagement)
        - 0.20 * z_error
        + 0.60
        + np.random.normal(0, 0.05, len(df))
    )

    df["engagement_score"] = engagement.astype(np.float32)
    df["frustration_score"] = frustration.astype(np.float32)
    df["performance_score"] = performance.astype(np.float32)


def _apply_dropout(df: pd.DataFrame) -> None:
    archetype_bias_map = {
        name: ARCHETYPES[name]["dropout_bias"] for name in ARCHETYPES
    }
    dbias = df["archetype"].map(archetype_bias_map).values

    burnout_mask = (df["archetype"] == "burnout") & (df["week"] > 10)
    burnout_penalty = np.where(burnout_mask, (df["week"] - 10) * 0.20, 0.0)
    dbias = dbias + burnout_penalty

    z_frustration = _zscore(df["frustration_score"].values)
    z_engagement = _zscore(df["engagement_score"].values)
    z_performance = _zscore(df["performance_score"].values)

    logit = (
        0.4 * z_frustration
        - 0.3 * z_engagement
        - 0.2 * z_performance
        + dbias
        + np.random.normal(0, 0.15, len(df))
    )
    dropout_prob = sigmoid(logit)
    dropout_raw = np.random.binomial(1, dropout_prob)

    for sid in df["student_id"].unique():
        mask = df["student_id"] == sid
        student_weeks = df.loc[mask, "week"].values
        student_dropout = dropout_raw[mask.values]
        drop_week = None
        for w, d in zip(student_weeks, student_dropout):
            if d == 1:
                drop_week = w
                break
        if drop_week is not None:
            after_mask = mask & (df["week"] >= drop_week)
            dropout_raw[after_mask.values] = 1

    df["dropout_prob"] = dropout_prob.astype(np.float32)
    df["dropout"] = dropout_raw.astype(np.int32)

    for col in FEATURE_NAMES:
        df.loc[df["dropout"] == 1, col] = 0
    for col in TARGET_NAMES[:3]:
        df.loc[df["dropout"] == 1, col] = 0.0
    df.loc[df["dropout"] == 1, "dropout_prob"] = 1.0


def _zscore(arr: np.ndarray) -> np.ndarray:
    std = np.std(arr)
    if std == 0:
        return np.zeros_like(arr)
    return (arr - np.mean(arr)) / std


def get_dataset_stats(df: pd.DataFrame) -> Dict:
    return {
        "n_students": int(df["student_id"].nunique()),
        "n_weeks": int(df["week"].max()),
        "n_rows": len(df),
        "n_dropouts": int(df["dropout"].sum()),
        "dropout_rate": round(float(df["dropout"].mean()), 4),
        "archetype_distribution": {
            k: int(v)
            for k, v in df["archetype"].value_counts().to_dict().items()
        },
        "features": FEATURE_NAMES,
        "targets": TARGET_NAMES,
    }
