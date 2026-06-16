import numpy as np
import pandas as pd
from scipy.special import expit as sigmoid
from typing import Dict, Tuple

N_STUDENTS = 10_000
N_WEEKS = 16
RANDOM_SEED = 42

ARCHETYPES = {
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

FEATURE_NAMES = [
    "session_days", "total_sessions", "total_time_minutes",
    "exercise_attempts", "passed_exercises", "error_rate",
    "forum_interactions", "content_views",
]

TARGET_NAMES = [
    "engagement_score", "frustration_score", "performance_score",
    "dropout_prob", "dropout",
]


def generate_dataset(
    n_students: int = N_STUDENTS,
    n_weeks: int = N_WEEKS,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    np.random.seed(seed)
    rng = np.random.default_rng(seed)

    archetype_names = list(ARCHETYPES.keys())
    archetype_weights = [ARCHETYPES[a]["weight"] for a in archetype_names]
    archetype_assignments = rng.choice(archetype_names, size=n_students, p=archetype_weights)

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
        base_motivation = rng.normal(params["motivation"][0], params["motivation"][1], n_mask)
        base_diligence = rng.normal(params["diligence"][0], params["diligence"][1], n_mask)

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

    effective_diligence = np.where(archetypes == "burnout", burnout_diligence, diligence)
    effective_motivation = np.where(archetypes == "burnout", burnout_motivation, motivation)
    effective_ability = np.where(archetypes == "burnout", burnout_ability, ability)

    session_days = rng.poisson(effective_diligence * 7).astype(float)
    session_days = np.clip(session_days, 0, 7)

    total_sessions = np.maximum(
        1,
        np.round(rng.gamma(3, 2, size=n_students * n_weeks) * effective_ability).astype(float),
    )
    total_sessions = np.clip(total_sessions, 0, 50)

    total_time_minutes = total_sessions * (
        20 + rng.gamma(2, 10, size=n_students * n_weeks)
    )
    total_time_minutes = np.clip(total_time_minutes, 0, 3000)

    exercise_attempts = np.maximum(
        0,
        np.round(rng.normal(effective_motivation * 25, 8)).astype(float),
    )
    exercise_attempts = np.clip(exercise_attempts, 0, 80)

    fatigue_penalty = np.clip(1.0 - fatigue * 0.3 * (1 - effective_ability), 0.3, 1.0)
    pass_prob = np.clip(effective_ability * fatigue_penalty, 0.01, 0.99)
    passed_exercises = rng.binomial(
        exercise_attempts.astype(np.int64),
        pass_prob,
    ).astype(float)
    passed_exercises = np.clip(passed_exercises, 0, exercise_attempts)

    error_rate = np.clip(
        1.0 - effective_ability * fatigue_penalty + rng.normal(0, 0.05, n_students * n_weeks),
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

    df = pd.DataFrame({
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
    })

    _compute_latent_variables(df)
    _apply_dropout(df)

    return df


def _compute_latent_variables(df: pd.DataFrame):
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

    z_frustration = _zscore(frustration)

    performance = sigmoid(
        0.45 * z_passed
        + 0.35 * _zscore(engagement)
        - 0.20 * z_error
        + 0.60
        + np.random.normal(0, 0.05, len(df))
    )

    z_performance = _zscore(performance)

    df["engagement_score"] = engagement.astype(np.float32)
    df["frustration_score"] = frustration.astype(np.float32)
    df["performance_score"] = performance.astype(np.float32)


def _apply_dropout(df: pd.DataFrame):
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

    # Cumulative frustration effect: running mean of past frustration
    fr_arr = df["frustration_score"].values.reshape(-1, 1)
    cum_fr = np.zeros(len(df))
    for sid in df["student_id"].unique():
        mask = df["student_id"] == sid
        idxs = np.where(mask)[0]
        for i, idx in enumerate(idxs):
            if i == 0:
                cum_fr[idx] = fr_arr[idx, 0]
            else:
                cum_fr[idx] = 0.7 * cum_fr[idxs[i - 1]] + 0.3 * fr_arr[idx, 0]
    z_cum_fr = _zscore(cum_fr)

    logit = (
        0.6 * z_frustration
        + 0.3 * z_cum_fr
        - 0.3 * z_engagement
        - 0.2 * z_performance
        + dbias
        + np.random.normal(0, 0.10, len(df))
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


def extract_features_for_engagement(
    df: pd.DataFrame, student_id: int, target_week: int = 5
) -> Tuple[np.ndarray, float]:
    window = df[(df["student_id"] == student_id) & (df["week"] < target_week) & (df["week"] >= target_week - 4)]
    if len(window) < 4:
        return None, None
    window = window.sort_values("week")
    features = window[FEATURE_NAMES].values.flatten()
    target_row = df[(df["student_id"] == student_id) & (df["week"] == target_week)]
    if len(target_row) == 0:
        return None, None
    target = target_row["engagement_score"].values[0]
    return features, target


def extract_features_for_performance(
    df: pd.DataFrame, student_id: int, target_week: int = 5
) -> Tuple[np.ndarray, float]:
    window = df[(df["student_id"] == student_id) & (df["week"] < target_week) & (df["week"] >= target_week - 4)]
    if len(window) < 4:
        return None, None
    window = window.sort_values("week")
    features = window[FEATURE_NAMES].values.flatten()
    target_row = df[(df["student_id"] == student_id) & (df["week"] == target_week)]
    if len(target_row) == 0:
        return None, None
    target = target_row["performance_score"].values[0]
    return features, target


def extract_features_for_dropout(
    df: pd.DataFrame, student_id: int, target_week: int = 5
) -> Tuple[np.ndarray, int]:
    window = df[(df["student_id"] == student_id) & (df["week"] < target_week) & (df["week"] >= target_week - 4)]
    if len(window) < 4:
        return None, None
    features = window[FEATURE_NAMES].mean(axis=0).values
    target_row = df[(df["student_id"] == student_id) & (df["week"] == target_week)]
    if len(target_row) == 0:
        return None, None
    target = target_row["dropout"].values[0]
    return features, target


def extract_features_for_frustration(
    df: pd.DataFrame, student_id: int, target_week: int = 5
) -> Tuple[np.ndarray, int]:
    window = df[(df["student_id"] == student_id) & (df["week"] < target_week) & (df["week"] >= target_week - 4)]
    if len(window) < 4:
        return None, None
    features = window[FEATURE_NAMES].mean(axis=0).values
    target_row = df[(df["student_id"] == student_id) & (df["week"] == target_week)]
    if len(target_row) == 0:
        return None, None
    fr_score = target_row["frustration_score"].values[0]
    target = 0
    if fr_score > 0.6:
        target = 2
    elif fr_score > 0.35:
        target = 1
    return features, target


def extract_features_for_clustering(df: pd.DataFrame, student_id: int) -> np.ndarray:
    student_data = df[df["student_id"] == student_id]
    if len(student_data) == 0:
        return None
    return student_data[FEATURE_NAMES].mean(axis=0).values


def extract_features_for_anomaly(
    df: pd.DataFrame, student_id: int, window_size: int = 4
) -> np.ndarray:
    student_data = df[df["student_id"] == student_id].sort_values("week")
    if len(student_data) < window_size + 1:
        return None
    recent = student_data.tail(window_size + 1)
    deltas = []
    for i in range(1, len(recent)):
        delta = recent.iloc[i][FEATURE_NAMES].values - recent.iloc[i - 1][FEATURE_NAMES].values
        deltas.append(delta)
    return np.array(deltas).flatten()


def extract_for_student(student_df: pd.DataFrame, target_week: int = 16):
    """Extract all 6 feature sets from a pre-filtered student DataFrame (16 rows).
    Avoids repeated DataFrame filtering for batch prediction."""
    if len(student_df) == 0:
        return None

    window = student_df[(student_df["week"] < target_week) & (student_df["week"] >= target_week - 4)]
    has_history = len(window) >= 4

    if has_history:
        window = window.sort_values("week")

        eng_feat = window[FEATURE_NAMES].values.flatten()
        perf_feat = window[FEATURE_NAMES].values.flatten()
        drop_feat = window[FEATURE_NAMES].mean(axis=0).values
        fr_feat = window[FEATURE_NAMES].mean(axis=0).values
    else:
        eng_feat = perf_feat = drop_feat = fr_feat = None

    cluster_feat = student_df[FEATURE_NAMES].mean(axis=0).values

    recent = student_df.sort_values("week").tail(5)
    if len(recent) >= 2:
        deltas = []
        for i in range(1, len(recent)):
            delta = recent.iloc[i][FEATURE_NAMES].values - recent.iloc[i - 1][FEATURE_NAMES].values
            deltas.append(delta)
        anomaly_feat = np.array(deltas).flatten()
    else:
        anomaly_feat = None

    return {
        "engagement": eng_feat,
        "performance": perf_feat,
        "dropout": drop_feat,
        "frustration": fr_feat,
        "clustering": cluster_feat,
        "anomaly": anomaly_feat,
    }


def build_training_data(
    df: pd.DataFrame, target_week: int = 5
) -> Dict[str, Tuple[np.ndarray, np.ndarray]]:
    student_ids = df["student_id"].unique()
    result = {
        "engagement": ([], []),
        "performance": ([], []),
        "dropout": ([], []),
        "frustration": ([], []),
    }

    eng_X, eng_y = [], []
    perf_X, perf_y = [], []
    drop_X, drop_y = [], []
    fr_X, fr_y = [], []

    for sid in student_ids:
        for task in ["engagement", "performance", "dropout", "frustration"]:
            if task == "engagement":
                f, t = extract_features_for_engagement(df, sid, target_week)
                if f is not None:
                    eng_X.append(f)
                    eng_y.append(t)
            elif task == "performance":
                f, t = extract_features_for_performance(df, sid, target_week)
                if f is not None:
                    perf_X.append(f)
                    perf_y.append(t)
            elif task == "dropout":
                f, t = extract_features_for_dropout(df, sid, target_week)
                if f is not None:
                    drop_X.append(f)
                    drop_y.append(t)
            elif task == "frustration":
                f, t = extract_features_for_frustration(df, sid, target_week)
                if f is not None:
                    fr_X.append(f)
                    fr_y.append(t)

    result["engagement"] = (np.array(eng_X), np.array(eng_y))
    result["performance"] = (np.array(perf_X), np.array(perf_y))
    result["dropout"] = (np.array(drop_X), np.array(drop_y))
    result["frustration"] = (np.array(fr_X), np.array(fr_y))

    return result


def build_training_data_sliding(
    df: pd.DataFrame,
) -> Dict[str, Dict[str, Tuple[np.ndarray, np.ndarray]]]:
    """
    Build training data using sliding windows:
    - 12 windows: (1,2,3,4)->5, (2,3,4,5)->6, ..., (12,13,14,15)->16
    - Temporal split:
      Train: windows 1-9 (target weeks 5-13)
      Test:  windows 10-12 (target weeks 14-16)
    """
    student_ids = df["student_id"].unique()
    max_week = int(df["week"].max())

    result = {}
    for task, extract_fn in [
        ("engagement", extract_features_for_engagement),
        ("performance", extract_features_for_performance),
        ("dropout", extract_features_for_dropout),
        ("frustration", extract_features_for_frustration),
    ]:
        train_X, train_y = [], []
        test_X, test_y = [], []

        for sid in student_ids:
            for target_week in range(5, max_week + 1):
                f, t = extract_fn(df, sid, target_week)
                if f is None:
                    continue
                if target_week <= 13:
                    train_X.append(f)
                    train_y.append(t)
                else:
                    test_X.append(f)
                    test_y.append(t)

        result[task] = {
            "train": (np.array(train_X), np.array(train_y)),
            "test": (np.array(test_X), np.array(test_y)),
        }

    return result
