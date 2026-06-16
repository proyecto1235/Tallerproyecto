import pytest
import pandas as pd
import numpy as np


class TestSlidingWindows:
    def test_window_count(self, dataset):
        from ml_pipeline.src.windows import build_sliding_windows
        windows = build_sliding_windows(dataset)

        for task in ["engagement", "performance", "dropout", "frustration"]:
            assert task in windows
            train_X, train_y = windows[task]["train"]
            test_X, test_y = windows[task]["test"]
            assert len(train_X) > 0
            assert len(train_y) > 0
            assert len(train_X) == len(train_y)

    def test_temporal_split(self, dataset):
        from ml_pipeline.src.windows import build_sliding_windows, TRAIN_MAX_WEEK
        windows = build_sliding_windows(dataset)
        eng = windows["engagement"]
        train_X, train_y = eng["train"]
        test_X, test_y = eng["test"]

        n_train_expected = sum(
            1 for sid in dataset["student_id"].unique()
            for tw in range(5, TRAIN_MAX_WEEK + 1)
            if len(dataset[(dataset["student_id"] == sid) & (dataset["week"] < tw) & (dataset["week"] >= tw - 4)]) >= 4
        )
        assert len(train_X) > 0

    def test_frustration_class_method(self):
        from ml_pipeline.src.windows import _frustration_class
        assert _frustration_class(0.7) == 2
        assert _frustration_class(0.4) == 1
        assert _frustration_class(0.1) == 0
        assert _frustration_class(0.6) == 1
        assert _frustration_class(0.35) == 0

    def test_extract_for_student_insufficient_window(self):
        from ml_pipeline.src.windows import _extract_for_student
        df = pd.DataFrame({"student_id": [1, 1], "week": [1, 2],
                           "session_days": [1, 2], "total_sessions": [3, 4],
                           "total_time_minutes": [5, 6], "exercise_attempts": [7, 8],
                           "passed_exercises": [9, 10], "error_rate": [0.1, 0.2],
                           "forum_interactions": [11, 12], "content_views": [13, 14],
                           "engagement_score": [0.5, 0.6], "performance_score": [0.5, 0.6],
                           "frustration_score": [0.3, 0.4], "dropout_prob": [0.1, 0.2],
                           "dropout": [0, 0]})
        result = _extract_for_student(df, 5)
        assert result[0] is None

    def test_extract_for_student_missing_target_week(self):
        from ml_pipeline.src.windows import _extract_for_student
        df = pd.DataFrame({"student_id": [1, 1, 1, 1], "week": [1, 2, 3, 4],
                           "session_days": [1, 2, 3, 4], "total_sessions": [3, 4, 5, 6],
                           "total_time_minutes": [5, 6, 7, 8], "exercise_attempts": [7, 8, 9, 10],
                           "passed_exercises": [9, 10, 11, 12], "error_rate": [0.1, 0.2, 0.3, 0.4],
                           "forum_interactions": [11, 12, 13, 14], "content_views": [13, 14, 15, 16],
                           "engagement_score": [0.5, 0.6, 0.7, 0.8],
                           "performance_score": [0.5, 0.6, 0.7, 0.8],
                           "frustration_score": [0.3, 0.4, 0.5, 0.6],
                           "dropout_prob": [0.1, 0.2, 0.3, 0.4],
                           "dropout": [0, 0, 0, 0]})
        result = _extract_for_student(df, 99)
        assert result[0] is None

    def test_single_student_dataset(self):
        from ml_pipeline.src.dataset import generate_dataset
        from ml_pipeline.src.windows import build_sliding_windows
        small = generate_dataset(n_students=1, n_weeks=8, seed=42)
        windows = build_sliding_windows(small)
        for task in ["engagement", "performance"]:
            train_X, train_y = windows[task]["train"]
            test_X, test_y = windows[task]["test"]
            assert len(train_X) > 0

    def test_temporal_split_produces_test_data(self):
        from ml_pipeline.src.dataset import generate_dataset
        from ml_pipeline.src.windows import build_sliding_windows, TRAIN_MAX_WEEK
        df = generate_dataset(n_students=10, n_weeks=16, seed=42)
        windows = build_sliding_windows(df)
        for task in ["engagement", "performance", "dropout", "frustration"]:
            test_X, test_y = windows[task]["test"]
            assert len(test_X) > 0, f"No test data for {task}"
            assert len(test_y) > 0
