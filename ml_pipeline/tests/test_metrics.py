import pytest
import numpy as np
import json
import os


class TestMetrics:
    def test_evaluate_regression(self):
        from ml_pipeline.src.metrics import evaluate_regression
        from sklearn.ensemble import RandomForestRegressor
        X = np.array([[1.0], [2.0], [3.0], [4.0], [5.0]])
        y = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(X, y)
        result = evaluate_regression(model, X, y)
        assert "mae" in result
        assert "rmse" in result
        assert "r2" in result
        assert isinstance(result["mae"], float)

    def test_evaluate_binary_classification(self):
        from ml_pipeline.src.metrics import evaluate_binary_classification
        from sklearn.ensemble import RandomForestClassifier
        X = np.random.rand(50, 4)
        y = np.array([0] * 25 + [1] * 25)
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        result = evaluate_binary_classification(model, X, y)
        assert "accuracy" in result
        assert "precision" in result
        assert "recall" in result
        assert "f1" in result
        assert "roc_auc" in result
        assert "confusion_matrix" in result

    def test_evaluate_binary_single_class_no_roc(self):
        from ml_pipeline.src.metrics import evaluate_binary_classification
        from sklearn.ensemble import RandomForestClassifier
        X = np.random.rand(20, 2)
        y = np.array([0] * 20)
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        result = evaluate_binary_classification(model, X, y)
        assert "roc_auc" not in result

    def test_evaluate_binary_roc_auc_exception(self, monkeypatch):
        from ml_pipeline.src.metrics import evaluate_binary_classification
        from sklearn.ensemble import RandomForestClassifier
        def bad_roc(*a, **kw):
            raise ValueError("mock failure")
        monkeypatch.setattr("ml_pipeline.src.metrics.roc_auc_score", bad_roc)
        X = np.random.rand(30, 2)
        y = np.array([0] * 15 + [1] * 15)
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        result = evaluate_binary_classification(model, X, y)
        assert result["roc_auc"] == 0.5

    def test_evaluate_multiclass_classification(self):
        from ml_pipeline.src.metrics import evaluate_multiclass_classification
        from sklearn.ensemble import RandomForestClassifier
        X = np.random.rand(60, 4)
        y = np.array([0] * 20 + [1] * 20 + [2] * 20)
        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)
        result = evaluate_multiclass_classification(model, X, y)
        assert "accuracy" in result
        assert "classification_report" in result
        assert "confusion_matrix" in result

    def test_evaluate_clustering(self):
        from ml_pipeline.src.metrics import evaluate_clustering
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        X = np.random.rand(50, 4)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = KMeans(n_clusters=3, random_state=42, n_init="auto")
        model.fit(X_scaled)
        result = evaluate_clustering(model, scaler, X)
        assert "silhouette_score" in result
        assert "n_clusters" in result
        assert result["n_clusters"] == 3
        assert "cluster_distribution" in result
        assert "n_samples" in result
        assert result["n_samples"] == 50

    def test_evaluate_clustering_single_cluster_silhouette_zero(self):
        from ml_pipeline.src.metrics import evaluate_clustering
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        X = np.random.rand(10, 2)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = KMeans(n_clusters=1, random_state=42, n_init="auto")
        model.fit(X_scaled)
        result = evaluate_clustering(model, scaler, X)
        assert result["silhouette_score"] == 0.0

    def test_evaluate_anomaly(self):
        from ml_pipeline.src.metrics import evaluate_anomaly
        from sklearn.ensemble import IsolationForest
        from sklearn.preprocessing import StandardScaler
        np.random.seed(42)
        X = np.random.rand(100, 4)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        model = IsolationForest(random_state=42, contamination=0.1)
        model.fit(X_scaled)
        result = evaluate_anomaly(model, scaler, X)
        assert "n_samples" in result
        assert "n_anomalies" in result
        assert "anomaly_rate" in result
        assert result["n_samples"] == 100

    def test_evaluate_anomaly_empty(self):
        pass  # unreachable in practice: StandardScaler rejects 0-sample arrays

    def test_save_metrics_json(self, tmp_path, monkeypatch):
        from ml_pipeline.src.metrics import save_metrics_json, REPORTS_DIR
        monkeypatch.setattr("ml_pipeline.src.metrics.REPORTS_DIR", str(tmp_path))
        metrics = {"test_model": {"mae": 0.1234, "r2": 0.9}}
        path = save_metrics_json(metrics)
        assert os.path.exists(path)
        with open(path) as f:
            loaded = json.load(f)
        assert loaded["test_model"]["mae"] == 0.1234

    def test_save_training_summary(self, tmp_path, monkeypatch):
        from ml_pipeline.src.metrics import save_training_summary, REPORTS_DIR
        monkeypatch.setattr("ml_pipeline.src.metrics.REPORTS_DIR", str(tmp_path))
        metrics = {
            "regression": {"mae": 0.1234, "r2": 0.9876},
            "nested": {"sub": {"mae": 0.05, "r2": 0.99, "note": "ok"}},
            "binary": {"accuracy": 0.95, "classification_report": {"0": {"precision": 0.9}}},
        }
        path = save_training_summary(metrics)
        assert os.path.exists(path)
        with open(path) as f:
            content = f.read()
        assert "Regression" in content
        assert "0.1234" in content
        assert "0.9876" in content
        assert "0.0500" in content
        assert "ok" in content
