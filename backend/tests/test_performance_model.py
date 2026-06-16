import pytest
import numpy as np


class TestPerformancePredictor:
    def test_train_and_evaluate(self, performance_predictor, training_data):
        X, y = training_data["performance"]
        if len(X) == 0:
            pytest.skip("No training data available")
        result = performance_predictor.train(X, y)
        assert "train" in result
        assert "test" in result
        assert result["test"]["mae"] < 0.25, f"MAE too high: {result['test']['mae']}"
        assert result["test"]["rmse"] < 0.35, f"RMSE too high: {result['test']['rmse']}"
        assert result["test"]["r2"] > 0.50, f"R² too low: {result['test']['r2']}"

    def test_feature_importances(self, performance_predictor, training_data):
        X, y = training_data["performance"]
        if len(X) == 0:
            pytest.skip("No training data")
        performance_predictor.train(X, y)
        importances = performance_predictor.get_feature_importances()
        assert len(importances) > 0

    def test_predict_clamped(self, performance_predictor, training_data):
        X, y = training_data["performance"]
        if len(X) == 0:
            pytest.skip("No training data")
        performance_predictor.train(X, y)
        pred = performance_predictor.predict(X[0])
        assert 0 <= pred <= 1

    def test_no_data_leakage(self, training_data):
        X, y = training_data["performance"]
        if len(X) == 0 or len(y) == 0:
            pytest.skip("No training data")
        corrs = []
        for i in range(X.shape[1]):
            c = np.corrcoef(X[:, i], y)[0, 1]
            corrs.append(abs(c))
        max_corr = max(corrs)
        assert max_corr < 0.99, f"Possible data leakage: {max_corr}"
