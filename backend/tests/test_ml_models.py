"""Tests for ML model classes - covers base_predictor, clustering, anomaly, and 4 predictors."""
import pytest
import numpy as np
import json
import os


class TestBasePredictor:
    def test_save_without_model(self, tmp_path, monkeypatch):
        from application.services.ml.base_predictor import BasePredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = BasePredictor("test_save")
        p._feature_names = ["a", "b"]
        p.save()
        assert os.path.exists(tmp_path / "test_save_scaler.pkl")
        assert os.path.exists(tmp_path / "test_save_features.json")
        assert os.path.exists(tmp_path / "test_save_trained.pkl")
        assert not os.path.exists(tmp_path / "test_save_model.pkl")
        with open(tmp_path / "test_save_features.json") as f:
            assert json.load(f) == ["a", "b"]

    def test_save_with_model(self, tmp_path, monkeypatch):
        from sklearn.ensemble import RandomForestClassifier
        from application.services.ml.base_predictor import BasePredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = BasePredictor("test_save2")
        p._model = RandomForestClassifier(n_estimators=2, random_state=42)
        p._is_trained = True
        p.save()
        assert os.path.exists(tmp_path / "test_save2_model.pkl")

    def test_load_exception(self, tmp_path, monkeypatch):
        from application.services.ml.base_predictor import BasePredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = BasePredictor("test_load_fail")
        os.makedirs(tmp_path, exist_ok=True)
        with open(tmp_path / "test_load_fail_scaler.pkl", "w") as f:
            f.write("not a pickle")
        loaded = p.load()
        assert loaded is False

    def test_load_success(self, tmp_path, monkeypatch):
        import joblib
        from sklearn.preprocessing import StandardScaler
        from application.services.ml.base_predictor import BasePredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        joblib.dump(StandardScaler(), tmp_path / "test_ok_scaler.pkl")
        with open(tmp_path / "test_ok_features.json", "w") as f:
            json.dump(["x", "y"], f)
        joblib.dump(True, tmp_path / "test_ok_trained.pkl")
        p = BasePredictor("test_ok")
        loaded = p.load()
        assert loaded is True
        assert p._feature_names == ["x", "y"]

    def test_get_feature_importances_no_model(self):
        from application.services.ml.base_predictor import BasePredictor
        p = BasePredictor("no_model_test")
        assert p.get_feature_importances() == []

    def test_get_feature_importances_no_attr(self, tmp_path, monkeypatch):
        from sklearn.cluster import KMeans
        from application.services.ml.base_predictor import BasePredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = BasePredictor("no_attr")
        p._model = KMeans(n_clusters=2, random_state=42, n_init=3)
        p._model.fit(np.random.rand(10, 2))
        assert p.get_feature_importances() == []

    def test_get_feature_importances_with_data(self, tmp_path, monkeypatch):
        from sklearn.ensemble import RandomForestClassifier
        from application.services.ml.base_predictor import BasePredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = BasePredictor("fi_test")
        X = np.random.rand(20, 3)
        y = np.random.randint(0, 2, 20)
        p._model = RandomForestClassifier(n_estimators=2, random_state=42)
        p._model.fit(X, y)
        p._feature_names = ["a", "b", "c"]
        fis = p.get_feature_importances()
        assert len(fis) == 3
        assert fis[0]["feature"] in ("a", "b", "c")
        assert 0 <= fis[0]["importance"] <= 1

    def test_get_feature_importances_fallback_names(self, tmp_path, monkeypatch):
        from sklearn.ensemble import RandomForestClassifier
        from application.services.ml.base_predictor import BasePredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = BasePredictor("fi_fallback")
        X = np.random.rand(20, 2)
        y = np.random.randint(0, 2, 20)
        p._model = RandomForestClassifier(n_estimators=2, random_state=42)
        p._model.fit(X, y)
        p._feature_names = ["only"]  # mismatch length
        fis = p.get_feature_importances()
        assert len(fis) == 2
        assert fis[0]["feature"] in ("f0", "f1")

    def test_load_with_model(self, tmp_path, monkeypatch):
        import joblib
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        from application.services.ml.base_predictor import BasePredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = BasePredictor("test_load_model")
        p._model = RandomForestClassifier(n_estimators=2, random_state=42)
        p._scaler = StandardScaler()
        p._feature_names = ["x"]
        p._is_trained = True
        p.save()
        p2 = BasePredictor("test_load_model")
        loaded = p2.load()
        assert loaded is True
        assert p2._model is not None

    def test_get_top_features(self, tmp_path, monkeypatch):
        from sklearn.ensemble import RandomForestClassifier
        from application.services.ml.base_predictor import BasePredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = BasePredictor("top_test")
        X = np.random.rand(20, 5)
        y = np.random.randint(0, 2, 20)
        p._model = RandomForestClassifier(n_estimators=2, random_state=42)
        p._model.fit(X, y)
        p._feature_names = ["a", "b", "c", "d", "e"]
        tops = p.get_top_features(3)
        assert len(tops) == 3
        assert tops[0] in ("a", "b", "c", "d", "e")

    def test_classifier_evaluate_binary(self, tmp_path, monkeypatch):
        from sklearn.ensemble import RandomForestClassifier
        from application.services.ml.base_predictor import ClassifierPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = ClassifierPredictor("clf_bin")
        X = np.array([[1, 0], [0, 1], [1, 1], [0, 0]])
        y = np.array([1, 0, 1, 0])
        X_test = X.copy()
        y_test = y.copy()
        p._model = RandomForestClassifier(n_estimators=2, random_state=42)
        p._model.fit(X, y)
        result = p.evaluate(X_test, y_test)
        assert "accuracy" in result
        assert "roc_auc" in result
        assert "precision" in result
        assert "recall" in result
        assert "f1" in result
        assert "classification_report" in result
        assert "confusion_matrix" in result

    def test_classifier_evaluate_binary_roc_auc_fallback(self, tmp_path, monkeypatch):
        from sklearn.ensemble import RandomForestClassifier
        from application.services.ml.base_predictor import ClassifierPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = ClassifierPredictor("clf_roc_fail")
        X = np.random.rand(10, 2)
        y = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1])  # very imbalanced
        p._model = RandomForestClassifier(n_estimators=2, random_state=42, max_depth=2)
        p._model.fit(X, y)
        result = p.evaluate(X, y)
        assert "roc_auc" in result

    def test_classifier_evaluate_binary_roc_auc_exception(self, tmp_path, monkeypatch):
        from application.services.ml.base_predictor import ClassifierPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        monkeypatch.setattr("application.services.ml.base_predictor.roc_auc_score", lambda *a, **kw: (_ for _ in ()).throw(ValueError("test")))
        p = ClassifierPredictor("clf_roc_exc")
        X = np.random.rand(10, 2)
        y = np.random.randint(0, 2, 10)
        p._model = type("FakeModel", (), {
            "predict": lambda self, x: np.random.randint(0, 2, len(x)),
            "predict_proba": lambda self, x: np.random.rand(len(x), 2),
        })()
        result = p.evaluate(X, y)
        assert result["roc_auc"] == 0.5

    def test_classifier_evaluate_multiclass(self, tmp_path, monkeypatch):
        from sklearn.ensemble import RandomForestClassifier
        from application.services.ml.base_predictor import ClassifierPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = ClassifierPredictor("clf_multi")
        X = np.random.rand(15, 2)
        y = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2])
        p._model = RandomForestClassifier(n_estimators=2, random_state=42, max_depth=2)
        p._model.fit(X, y)
        result = p.evaluate(X, y)
        assert "accuracy" in result
        assert "roc_auc" not in result
        assert "precision" not in result

    def test_regressor_evaluate(self, tmp_path, monkeypatch):
        from sklearn.ensemble import RandomForestRegressor
        from application.services.ml.base_predictor import RegressorPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = RegressorPredictor("reg_test")
        X = np.random.rand(10, 2)
        y = np.random.rand(10)
        p._model = RandomForestRegressor(n_estimators=2, random_state=42)
        p._model.fit(X, y)
        result = p.evaluate(X, y)
        assert "mae" in result
        assert "rmse" in result
        assert "r2" in result
        assert 0 <= result["r2"] <= 1 or result["r2"] < 0  # r2 can be negative


class TestClustering:
    def test_predict_not_trained(self):
        from application.services.ml.clustering import LearningClustering
        c = LearningClustering()
        c._is_trained = False
        result = c.predict(np.zeros(8))
        assert result["cluster_id"] == -1
        assert result["cluster_name"] == "unknown"

    def test_batch_predict_not_trained(self):
        from application.services.ml.clustering import LearningClustering
        c = LearningClustering()
        c._is_trained = False
        result = c.batch_predict(np.zeros((3, 8)))
        assert result == []

    def test_batch_predict_trained(self, tmp_path, monkeypatch):
        from application.services.ml.clustering import LearningClustering
        monkeypatch.setattr("application.services.ml.clustering.MODEL_DIR", str(tmp_path))
        c = LearningClustering(n_clusters=2)
        X = np.random.rand(20, 8)
        c.train(X)
        result = c.batch_predict(X[:3])
        assert len(result) == 3
        for r in result:
            assert "cluster_id" in r
            assert "cluster_name" in r
            assert "cluster_description" in r

    def test_pca_projection_not_trained(self):
        from application.services.ml.clustering import LearningClustering
        c = LearningClustering()
        c._is_trained = False
        c._pca = None
        result = c.get_pca_projection(np.zeros((3, 8)))
        assert result == {"pca1": [], "pca2": [], "labels": []}

    def test_load_exception(self, tmp_path, monkeypatch):
        from application.services.ml.clustering import LearningClustering
        monkeypatch.setattr("application.services.ml.clustering.MODEL_DIR", str(tmp_path))
        os.makedirs(tmp_path, exist_ok=True)
        with open(tmp_path / "cluster_model.pkl", "w") as f:
            f.write("corrupt")
        c = LearningClustering()
        assert c._is_trained is False

    def test_train_then_save_then_load(self, tmp_path, monkeypatch):
        from application.services.ml.clustering import LearningClustering
        monkeypatch.setattr("application.services.ml.clustering.MODEL_DIR", str(tmp_path))
        c = LearningClustering(n_clusters=2)
        X = np.random.rand(15, 8)
        result = c.train(X)
        assert result["n_samples"] == 15
        assert result["n_clusters"] == 2
        # Re-create to test _load
        c2 = LearningClustering(n_clusters=2)
        assert c2._is_trained is True

    def test_get_summary(self, tmp_path, monkeypatch):
        from application.services.ml.clustering import LearningClustering
        monkeypatch.setattr("application.services.ml.clustering.MODEL_DIR", str(tmp_path))
        c = LearningClustering(n_clusters=2)
        X = np.random.rand(10, 8)
        c.train(X)
        summary = c.get_summary(X)
        assert len(summary) == 2
        total = sum(s["count"] for s in summary)
        assert total == 10


class TestAnomaly:
    def test_predict_not_trained(self):
        from application.services.ml.anomaly_detector import AnomalyDetector
        a = AnomalyDetector()
        a._is_trained = False
        result = a.predict(np.zeros(16))
        assert result["risk"] == "unknown"
        assert result["is_anomaly"] is False

    def test_batch_predict_not_trained(self):
        from application.services.ml.anomaly_detector import AnomalyDetector
        a = AnomalyDetector()
        a._is_trained = False
        result = a.batch_predict(np.zeros((3, 16)))
        assert len(result) == 3
        for r in result:
            assert r["risk"] == "unknown"

    def test_batch_predict_trained(self, tmp_path, monkeypatch):
        from application.services.ml.anomaly_detector import AnomalyDetector
        monkeypatch.setattr("application.services.ml.anomaly_detector.MODEL_DIR", str(tmp_path))
        a = AnomalyDetector()
        X = np.random.rand(50, 16)
        a.train(X)
        results = a.batch_predict(X[:5])
        assert len(results) == 5
        for r in results:
            assert r["risk"] in ("low", "medium", "high")

    def test_train_and_save(self, tmp_path, monkeypatch):
        from application.services.ml.anomaly_detector import AnomalyDetector
        monkeypatch.setattr("application.services.ml.anomaly_detector.MODEL_DIR", str(tmp_path))
        a = AnomalyDetector()
        X = np.random.rand(50, 16)
        result = a.train(X)
        assert result["n_samples"] == 50
        assert result["n_anomalies"] >= 0
        assert os.path.exists(tmp_path / "anomaly_model.pkl")
        assert os.path.exists(tmp_path / "anomaly_scaler.pkl")

    def test_extract_deltas_insufficient(self):
        from application.services.ml.anomaly_detector import AnomalyDetector
        a = AnomalyDetector()
        # Single week -> None
        assert a.extract_deltas([{"week": 1}]) is None
        # Only one delta after diff -> None (need 2+ deltas)
        assert a.extract_deltas([
            {"week": 1, "session_days": 5},
            {"week": 2, "session_days": 3},
        ]) is None

    def test_extract_deltas_success(self):
        from application.services.ml.anomaly_detector import AnomalyDetector
        a = AnomalyDetector()
        result = a.extract_deltas([
            {"week": 1, "session_days": 5, "total_sessions": 10, "total_time_minutes": 300,
             "exercise_attempts": 8, "passed_exercises": 6, "error_rate": 0.2,
             "forum_interactions": 3, "content_views": 7},
            {"week": 2, "session_days": 2, "total_sessions": 3, "total_time_minutes": 60,
             "exercise_attempts": 1, "passed_exercises": 0, "error_rate": 0.8,
             "forum_interactions": 0, "content_views": 2},
            {"week": 3, "session_days": 0, "total_sessions": 0, "total_time_minutes": 0,
             "exercise_attempts": 0, "passed_exercises": 0, "error_rate": 1.0,
             "forum_interactions": 0, "content_views": 0},
        ])
        assert result is not None
        assert len(result) == 16  # 2 deltas * 8 features

    def test_predict_risk_levels(self, tmp_path, monkeypatch):
        from application.services.ml.anomaly_detector import AnomalyDetector
        monkeypatch.setattr("application.services.ml.anomaly_detector.MODEL_DIR", str(tmp_path))
        a = AnomalyDetector()
        X = np.random.rand(100, 16)
        a.train(X)
        result = a.predict(np.random.rand(16))
        assert result["risk"] in ("low", "medium", "high")

    def test_predict_risk_medium(self, tmp_path, monkeypatch):
        from application.services.ml.anomaly_detector import AnomalyDetector
        monkeypatch.setattr("application.services.ml.anomaly_detector.MODEL_DIR", str(tmp_path))
        a = AnomalyDetector()
        a._model = type("FakeModel", (), {
            "predict": lambda self, x: np.array([-1]),
            "score_samples": lambda self, x: np.array([-0.3]),
        })()
        a._scaler = type("FakeScaler", (), {
            "transform": lambda self, x: x,
        })()
        a._is_trained = True
        result = a.predict(np.random.rand(16))
        assert result["is_anomaly"] is True
        assert result["risk"] == "medium"

    def test_predict_risk_high(self, tmp_path, monkeypatch):
        from application.services.ml.anomaly_detector import AnomalyDetector
        monkeypatch.setattr("application.services.ml.anomaly_detector.MODEL_DIR", str(tmp_path))
        a = AnomalyDetector()
        a._model = type("FakeModel", (), {
            "predict": lambda self, x: np.array([-1]),
            "score_samples": lambda self, x: np.array([-0.5]),
        })()
        a._scaler = type("FakeScaler", (), {
            "transform": lambda self, x: x,
        })()
        a._is_trained = True
        result = a.predict(np.random.rand(16))
        assert result["is_anomaly"] is True
        assert result["risk"] == "high"

    def test_batch_predict_risk_medium(self, tmp_path, monkeypatch):
        from application.services.ml.anomaly_detector import AnomalyDetector
        monkeypatch.setattr("application.services.ml.anomaly_detector.MODEL_DIR", str(tmp_path))
        a = AnomalyDetector()
        a._model = type("FakeModel", (), {
            "predict": lambda self, x: np.array([-1, 1, -1]),
            "score_samples": lambda self, x: np.array([-0.3, 0.1, -0.5]),
        })()
        a._scaler = type("FakeScaler", (), {
            "transform": lambda self, x: x,
        })()
        a._is_trained = True
        results = a.batch_predict(np.random.rand(3, 16))
        assert results[0]["is_anomaly"] is True
        assert results[0]["risk"] == "medium"
        assert results[1]["is_anomaly"] is False
        assert results[1]["risk"] == "low"
        assert results[2]["is_anomaly"] is True
        assert results[2]["risk"] == "high"

    def test_load_exception(self, tmp_path, monkeypatch):
        from application.services.ml.anomaly_detector import AnomalyDetector
        monkeypatch.setattr("application.services.ml.anomaly_detector.MODEL_DIR", str(tmp_path))
        os.makedirs(tmp_path, exist_ok=True)
        with open(tmp_path / "anomaly_model.pkl", "w") as f:
            f.write("corrupt")
        a = AnomalyDetector()
        assert a._is_trained is False


class TestDropoutPredictor:
    def test_train(self, tmp_path, monkeypatch):
        from application.services.ml.dropout_predictor import DropoutPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = DropoutPredictor()
        X = np.random.rand(50, 8)
        y = np.random.randint(0, 2, 50)
        result = p.train(X, y)
        assert "test" in result
        assert "cv_roc_auc_mean" in result
        assert "cv_roc_auc_std" in result
        assert "feature_importances" in result
        assert result["n_samples"] == 50
        assert result["class_distribution"]["no_dropout"] + result["class_distribution"]["dropout"] > 0

    def test_train_with_test_override(self, tmp_path, monkeypatch):
        from application.services.ml.dropout_predictor import DropoutPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = DropoutPredictor()
        X = np.random.rand(30, 8)
        y = np.random.randint(0, 2, 30)
        X_test = np.random.rand(10, 8)
        y_test = np.random.randint(0, 2, 10)
        result = p.train(X, y, X_test_override=X_test, y_test_override=y_test)
        assert result["n_test"] == 10
        assert result["n_train"] == 30

    def test_predict_proba_and_predict(self, tmp_path, monkeypatch):
        from application.services.ml.dropout_predictor import DropoutPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = DropoutPredictor()
        X = np.random.rand(30, 8)
        y = np.random.randint(0, 2, 30)
        p.train(X, y)
        proba = p.predict_proba(np.random.rand(8))
        assert 0 <= proba <= 1
        pred = p.predict(np.random.rand(8))
        assert pred in (0, 1)


class TestFrustrationPredictor:
    def test_train(self, tmp_path, monkeypatch):
        from application.services.ml.frustration_predictor import FrustrationPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = FrustrationPredictor()
        X = np.random.rand(50, 8)
        y = np.random.randint(0, 3, 50)
        result = p.train(X, y)
        assert "test" in result
        assert "feature_importances" in result
        assert result["n_samples"] == 50

    def test_train_stratify_fallback(self, tmp_path, monkeypatch):
        from application.services.ml.frustration_predictor import FrustrationPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = FrustrationPredictor()
        X = np.random.rand(10, 8)
        y = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 1])  # class 1 has only 1 sample, can't stratify
        result = p.train(X, y)
        assert result["n_samples"] == 10

    def test_train_with_override(self, tmp_path, monkeypatch):
        from application.services.ml.frustration_predictor import FrustrationPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = FrustrationPredictor()
        X = np.random.rand(21, 8)
        y = np.array([0]*7 + [1]*7 + [2]*7)
        X_test = np.random.rand(6, 8)
        y_test = np.array([0, 0, 1, 1, 2, 2])
        result = p.train(X, y, X_test_override=X_test, y_test_override=y_test)
        assert result["n_test"] == 6
        assert result["n_train"] == 21

    def test_predict_and_proba(self, tmp_path, monkeypatch):
        from application.services.ml.frustration_predictor import FrustrationPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = FrustrationPredictor()
        X = np.random.rand(30, 8)
        y = np.random.randint(0, 3, 30)
        p.train(X, y)
        pred = p.predict(np.random.rand(8))
        assert 0 <= pred <= 2
        proba = p.predict_proba(np.random.rand(8))
        assert len(proba) == 3
        assert abs(sum(proba) - 1.0) < 0.1


class TestEngagementPredictor:
    def test_train(self, tmp_path, monkeypatch):
        from application.services.ml.engagement_predictor import EngagementPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = EngagementPredictor()
        X = np.random.rand(50, 32)
        y = np.random.rand(50)
        result = p.train(X, y)
        assert "train" in result
        assert "test" in result
        assert "feature_importances" in result

    def test_train_with_override(self, tmp_path, monkeypatch):
        from application.services.ml.engagement_predictor import EngagementPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = EngagementPredictor()
        X = np.random.rand(30, 32)
        y = np.random.rand(30)
        X_test = np.random.rand(10, 32)
        y_test = np.random.rand(10)
        result = p.train(X, y, X_test_override=X_test, y_test_override=y_test)
        assert result["n_test"] == 10

    def test_predict(self, tmp_path, monkeypatch):
        from application.services.ml.engagement_predictor import EngagementPredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = EngagementPredictor()
        X = np.random.rand(30, 32)
        y = np.random.rand(30)
        p.train(X, y)
        pred = p.predict(np.random.rand(32))
        assert 0 <= pred <= 1


class TestPerformancePredictor:
    def test_train(self, tmp_path, monkeypatch):
        from application.services.ml.performance_predictor import PerformancePredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = PerformancePredictor()
        X = np.random.rand(50, 32)
        y = np.random.rand(50)
        result = p.train(X, y)
        assert "train" in result
        assert "test" in result
        assert "feature_importances" in result

    def test_train_with_override(self, tmp_path, monkeypatch):
        from application.services.ml.performance_predictor import PerformancePredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = PerformancePredictor()
        X = np.random.rand(30, 32)
        y = np.random.rand(30)
        X_test = np.random.rand(10, 32)
        y_test = np.random.rand(10)
        result = p.train(X, y, X_test_override=X_test, y_test_override=y_test)
        assert result["n_test"] == 10

    def test_predict(self, tmp_path, monkeypatch):
        from application.services.ml.performance_predictor import PerformancePredictor
        monkeypatch.setattr("application.services.ml.base_predictor.MODEL_DIR", str(tmp_path))
        p = PerformancePredictor()
        X = np.random.rand(30, 32)
        y = np.random.rand(30)
        p.train(X, y)
        pred = p.predict(np.random.rand(32))
        assert 0 <= pred <= 1
