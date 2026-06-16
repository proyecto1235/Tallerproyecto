import pytest
import numpy as np


class TestFrustrationPredictor:
    def test_train_and_evaluate(self, frustration_predictor, training_data):
        X, y = training_data["frustration"]
        if len(X) == 0 or len(np.unique(y)) < 2:
            pytest.skip("Not enough frustration samples")
        result = frustration_predictor.train(X, y)
        assert "test" in result
        assert result["test"]["accuracy"] > 0.0

    def test_class_distribution(self, frustration_predictor, training_data):
        X, y = training_data["frustration"]
        if len(X) == 0:
            pytest.skip("No data")
        classes, counts = np.unique(y, return_counts=True)
        print(f"[Frustration] Classes: {dict(zip(classes, counts))}")
        assert len(classes) >= 2

    def test_feature_importances(self, frustration_predictor, training_data):
        X, y = training_data["frustration"]
        if len(X) < 20:
            pytest.skip("Not enough data")
        frustration_predictor.train(X, y)
        importances = frustration_predictor.get_feature_importances()
        assert len(importances) > 0

    def test_predict_class_and_proba(self, frustration_predictor, training_data):
        X, y = training_data["frustration"]
        if len(X) == 0:
            pytest.skip("No data")
        frustration_predictor.train(X, y)
        cls = frustration_predictor.predict(X[0])
        assert cls in (0, 1, 2)
        proba = frustration_predictor.predict_proba(X[0])
        assert len(proba) >= 2
        assert abs(sum(proba) - 1.0) < 0.01

    def test_no_data_leakage(self, training_data):
        X, y = training_data["frustration"]
        if len(X) == 0:
            pytest.skip("No data")
        corrs = []
        for i in range(X.shape[1]):
            c = np.corrcoef(X[:, i], y)[0, 1]
            corrs.append(abs(c))
        max_corr = max(corrs)
        assert max_corr < 0.99, f"Possible data leakage: {max_corr}"
