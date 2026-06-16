import pytest
import numpy as np


class TestAnomalyDetector:
    def test_train(self, anomaly_detector, synthetic_dataset):
        from application.services.ml.synthetic_dataset import extract_features_for_anomaly
        X = []
        for sid in synthetic_dataset["student_id"].unique():
            deltas = extract_features_for_anomaly(synthetic_dataset, sid)
            if deltas is not None:
                X.append(deltas)
        if len(X) < 5:
            pytest.skip("Not enough samples")
        X_arr = np.array(X)
        result = anomaly_detector.train(X_arr)
        assert result["n_samples"] > 0
        assert result["n_anomalies"] >= 0
        assert result["anomaly_rate"] > 0

    def test_predict(self, anomaly_detector, synthetic_dataset):
        from application.services.ml.synthetic_dataset import extract_features_for_anomaly
        for sid in synthetic_dataset["student_id"].unique()[:5]:
            deltas = extract_features_for_anomaly(synthetic_dataset, sid)
            if deltas is not None:
                result = anomaly_detector.predict(deltas)
                assert "is_anomaly" in result
                assert "anomaly_score" in result
                assert "risk" in result
                break

    def test_extract_deltas(self, anomaly_detector):
        history = [
            {"week": 1, "session_days": 5, "total_sessions": 10, "total_time_minutes": 300,
             "exercise_attempts": 8, "passed_exercises": 6, "error_rate": 0.2,
             "forum_interactions": 3, "content_views": 7},
            {"week": 2, "session_days": 2, "total_sessions": 3, "total_time_minutes": 60,
             "exercise_attempts": 1, "passed_exercises": 0, "error_rate": 0.8,
             "forum_interactions": 0, "content_views": 2},
            {"week": 3, "session_days": 0, "total_sessions": 0, "total_time_minutes": 0,
             "exercise_attempts": 0, "passed_exercises": 0, "error_rate": 1.0,
             "forum_interactions": 0, "content_views": 0},
        ]
        deltas = anomaly_detector.extract_deltas(history)
        assert deltas is not None
        assert len(deltas) == 16

    def test_single_week_returns_none(self, anomaly_detector):
        history = [{"week": 1, "session_days": 5}]
        deltas = anomaly_detector.extract_deltas(history)
        assert deltas is None
