"""Sliding windows and temporal split for the ML pipeline.

Generates 12 sliding windows:
  (weeks 1-4 -> 5), (2-5 -> 6), ..., (12-15 -> 16)

Temporal split:
  Train: target weeks 5-13 (windows 1-9)
  Test:  target weeks 14-16 (windows 10-12)
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple

from ml_pipeline.src.dataset import FEATURE_NAMES

TARGET_WEEK_RANGE = range(5, 17)
TRAIN_MAX_WEEK = 13


def _frustration_class(fr_score: float) -> int:
    if fr_score > 0.6:
        return 2
    if fr_score > 0.35:
        return 1
    return 0


def _extract_for_student(
    student_data: pd.DataFrame,
    target_week: int,
) -> Tuple:
    student_data = student_data.sort_values("week")
    window = student_data[
        (student_data["week"] < target_week)
        & (student_data["week"] >= target_week - 4)
    ]
    if len(window) < 4:
        return None, None, None, None, None, None

    target_row = student_data[student_data["week"] == target_week]
    if len(target_row) == 0:
        return None, None, None, None, None, None

    tr = target_row.iloc[0]
    flat_feats = window[FEATURE_NAMES].values.flatten()
    mean_feats = window[FEATURE_NAMES].mean(axis=0).values
    fr_target = _frustration_class(tr["frustration_score"])

    return (
        flat_feats, tr["engagement_score"],
        flat_feats, tr["performance_score"],
        mean_feats, tr["dropout"],
        mean_feats, fr_target,
    )


def build_sliding_windows(
    df: pd.DataFrame,
) -> Dict[str, Dict[str, Tuple[np.ndarray, np.ndarray]]]:
    student_groups = {sid: grp for sid, grp in df.groupby("student_id")}

    train_buffers: Dict[str, list] = {
        k: [] for k in ["engagement", "performance", "dropout", "frustration"]
    }
    test_buffers: Dict[str, list] = {
        k: [] for k in ["engagement", "performance", "dropout", "frustration"]
    }
    train_targets: Dict[str, list] = {
        k: [] for k in ["engagement", "performance", "dropout", "frustration"]
    }
    test_targets: Dict[str, list] = {
        k: [] for k in ["engagement", "performance", "dropout", "frustration"]
    }

    for sid, group in student_groups.items():
        for tw in TARGET_WEEK_RANGE:
            result = _extract_for_student(group, tw)
            if result[0] is None:
                continue

            eng_feat, eng_t, perf_feat, perf_t, drop_feat, drop_t, fr_feat, fr_t = result

            if tw <= TRAIN_MAX_WEEK:
                train_buffers["engagement"].append(eng_feat)
                train_targets["engagement"].append(eng_t)
                train_buffers["performance"].append(perf_feat)
                train_targets["performance"].append(perf_t)
                train_buffers["dropout"].append(drop_feat)
                train_targets["dropout"].append(drop_t)
                train_buffers["frustration"].append(fr_feat)
                train_targets["frustration"].append(fr_t)
            else:
                test_buffers["engagement"].append(eng_feat)
                test_targets["engagement"].append(eng_t)
                test_buffers["performance"].append(perf_feat)
                test_targets["performance"].append(perf_t)
                test_buffers["dropout"].append(drop_feat)
                test_targets["dropout"].append(drop_t)
                test_buffers["frustration"].append(fr_feat)
                test_targets["frustration"].append(fr_t)

    result = {}
    for task in ["engagement", "performance", "dropout", "frustration"]:
        result[task] = {
            "train": (
                np.array(train_buffers[task], dtype=np.float64),
                np.array(train_targets[task]),
            ),
            "test": (
                np.array(test_buffers[task], dtype=np.float64),
                np.array(test_targets[task]),
            ),
        }

    return result
