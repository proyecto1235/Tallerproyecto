import pytest
import numpy as np
import pandas as pd


class TestFeatureExtraction:
    def test_extract_engagement(self, dataset):
        from ml_pipeline.src.features import extract_for_engagement
        sid = dataset["student_id"].iloc[0]
        features, target = extract_for_engagement(dataset, sid, target_week=5)
        assert features is not None
        assert len(features) == 8 * 4
        assert 0 <= target <= 1

    def test_extract_performance(self, dataset):
        from ml_pipeline.src.features import extract_for_performance
        sid = dataset["student_id"].iloc[0]
        features, target = extract_for_performance(dataset, sid, target_week=5)
        assert features is not None
        assert 0 <= target <= 1

    def test_extract_dropout(self, dataset):
        from ml_pipeline.src.features import extract_for_dropout
        sid = dataset["student_id"].iloc[0]
        features, target = extract_for_dropout(dataset, sid, target_week=5)
        assert features is not None
        assert target in (0, 1)

    def test_extract_frustration(self, dataset):
        from ml_pipeline.src.features import extract_for_frustration
        sid = dataset["student_id"].iloc[0]
        features, target = extract_for_frustration(dataset, sid, target_week=5)
        assert features is not None
        assert target in (0, 1, 2)

    def test_extract_clustering(self, dataset):
        from ml_pipeline.src.features import extract_for_clustering
        sid = dataset["student_id"].iloc[0]
        features = extract_for_clustering(dataset, sid)
        assert features is not None
        assert len(features) == 8

    def test_extract_clustering_empty_student(self, dataset):
        from ml_pipeline.src.features import extract_for_clustering
        result = extract_for_clustering(dataset, -999)
        assert result is None

    def test_extract_anomaly(self, dataset):
        from ml_pipeline.src.features import extract_for_anomaly
        sid = dataset["student_id"].iloc[0]
        features = extract_for_anomaly(dataset, sid, window_size=4)
        assert features is not None
        assert len(features) == 4 * 8

    def test_extract_anomaly_insufficient_data(self, dataset):
        from ml_pipeline.src.features import extract_for_anomaly
        sid = max(dataset["student_id"]) + 9999
        result = extract_for_anomaly(dataset, sid, window_size=4)
        assert result is None

    def test_extract_anomaly_window_size_zero(self):
        from ml_pipeline.src.features import extract_for_anomaly
        df = pd.DataFrame({"student_id": [1, 1], "week": [1, 2]})
        for col in ["session_days", "total_sessions", "total_time_minutes",
                    "exercise_attempts", "passed_exercises", "error_rate",
                    "forum_interactions", "content_views"]:
            df[col] = 0.0
        result = extract_for_anomaly(df, 1, window_size=5)
        assert result is None

    def test_no_data_leakage(self, dataset):
        from ml_pipeline.src.features import (
            extract_for_engagement, extract_for_performance,
        )

        for extract_fn in [extract_for_engagement, extract_for_performance]:
            all_X = []
            all_y = []
            for sid in dataset["student_id"].unique()[:100]:
                f, t = extract_fn(dataset, sid, 5)
                if f is not None:
                    all_X.append(f)
                    all_y.append(t)
            if len(all_X) < 10:
                continue
            X_arr = np.array(all_X)
            y_arr = np.array(all_y)
            for i in range(X_arr.shape[1]):
                col = X_arr[:, i]
                if np.std(col) < 1e-8 or np.std(y_arr) < 1e-8:
                    continue
                corr = abs(np.corrcoef(col, y_arr)[0, 1])
                assert corr < 0.99, f"Leakage in feature {i}"

    def test_window_features_flat_success(self):
        from ml_pipeline.src.features import _window_features_flat
        df = pd.DataFrame({"session_days": [1, 2, 3, 4], "total_sessions": [5, 6, 7, 8],
                           "total_time_minutes": [9, 10, 11, 12], "exercise_attempts": [13, 14, 15, 16],
                           "passed_exercises": [17, 18, 19, 20], "error_rate": [0.1, 0.2, 0.3, 0.4],
                           "forum_interactions": [21, 22, 23, 24], "content_views": [25, 26, 27, 28]})
        result = _window_features_flat(df)
        assert result is not None
        assert len(result) == 8 * 4

    def test_window_features_flat_insufficient_data(self):
        from ml_pipeline.src.features import _window_features_flat
        df = pd.DataFrame({"session_days": [1, 2], "total_sessions": [3, 4],
                           "total_time_minutes": [5, 6], "exercise_attempts": [7, 8],
                           "passed_exercises": [9, 10], "error_rate": [0.1, 0.2],
                           "forum_interactions": [11, 12], "content_views": [13, 14]})
        result = _window_features_flat(df)
        assert result is None

    def test_window_features_mean_success(self):
        from ml_pipeline.src.features import _window_features_mean
        df = pd.DataFrame({"session_days": [1, 2, 3, 4], "total_sessions": [5, 6, 7, 8],
                           "total_time_minutes": [9, 10, 11, 12], "exercise_attempts": [13, 14, 15, 16],
                           "passed_exercises": [17, 18, 19, 20], "error_rate": [0.1, 0.2, 0.3, 0.4],
                           "forum_interactions": [21, 22, 23, 24], "content_views": [25, 26, 27, 28]})
        result = _window_features_mean(df)
        assert result is not None
        assert len(result) == 8

    def test_window_features_mean_insufficient_data(self):
        from ml_pipeline.src.features import _window_features_mean
        df = pd.DataFrame({"session_days": [1], "total_sessions": [2],
                           "total_time_minutes": [3], "exercise_attempts": [4],
                           "passed_exercises": [5], "error_rate": [0.1],
                           "forum_interactions": [6], "content_views": [7]})
        result = _window_features_mean(df)
        assert result is None

    def test_frustration_class(self):
        from ml_pipeline.src.features import _frustration_class
        assert _frustration_class(0.8) == 2
        assert _frustration_class(0.5) == 1
        assert _frustration_class(0.2) == 0

    def test_extract_no_target_week(self, dataset):
        from ml_pipeline.src.features import extract_for_engagement
        sid = dataset["student_id"].iloc[0]
        features, target = extract_for_engagement(dataset, sid, target_week=99)
        assert features is None
        assert target is None

    def test_extract_insufficient_window(self, dataset):
        from ml_pipeline.src.features import extract_for_engagement
        features, target = extract_for_engagement(dataset, student_id=99999, target_week=5)
        assert features is None
        assert target is None

    def test_extract_window_ok_no_target(self, dataset):
        from ml_pipeline.src.features import (
            extract_for_engagement, extract_for_performance,
            extract_for_dropout, extract_for_frustration,
        )
        sid = dataset["student_id"].iloc[0]
        for fn in [extract_for_engagement, extract_for_performance, extract_for_dropout, extract_for_frustration]:
            f, t = fn(dataset, sid, target_week=7)
            assert f is None
            assert t is None

    def test_extract_dropout_window_check(self, dataset):
        from ml_pipeline.src.features import extract_for_dropout
        f, t = extract_for_dropout(dataset, student_id=99999, target_week=5)
        assert f is None
        assert t is None

    def test_extract_frustration_window_check(self, dataset):
        from ml_pipeline.src.features import extract_for_frustration
        f, t = extract_for_frustration(dataset, student_id=99999, target_week=5)
        assert f is None
        assert t is None

    def test_extract_performance_window_check(self, dataset):
        from ml_pipeline.src.features import extract_for_performance
        f, t = extract_for_performance(dataset, student_id=99999, target_week=5)
        assert f is None
        assert t is None
