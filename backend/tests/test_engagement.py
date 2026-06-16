import pytest
import numpy as np


class TestEngagementPredictor:
    def test_train_and_evaluate(self, engagement_predictor, training_data):
        X, y = training_data["engagement"]
        if len(X) == 0:
            pytest.skip("No training data available")
        result = engagement_predictor.train(X, y)
        assert "train" in result
        assert "test" in result
        assert result["test"]["mae"] < 0.25, f"MAE too high: {result['test']['mae']}"
        assert result["test"]["rmse"] < 0.35, f"RMSE too high: {result['test']['rmse']}"
        assert result["test"]["r2"] > 0.50, f"R² too low: {result['test']['r2']}"

    def test_feature_importances(self, engagement_predictor, training_data):
        X, y = training_data["engagement"]
        if len(X) == 0:
            pytest.skip("No training data")
        engagement_predictor.train(X, y)
        importances = engagement_predictor.get_feature_importances()
        assert len(importances) > 0
        assert importances[0]["importance"] > 0
        top = engagement_predictor.get_top_features(3)
        assert len(top) == 3

    def test_predict_shape(self, engagement_predictor, training_data):
        X, y = training_data["engagement"]
        if len(X) == 0:
            pytest.skip("No training data")
        engagement_predictor.train(X, y)
        pred = engagement_predictor.predict(X[0])
        assert 0 <= pred <= 1

    def test_no_data_leakage(self, training_data):
        X, y = training_data["engagement"]
        if len(X) == 0 or len(y) == 0:
            pytest.skip("No training data")
        corrs = []
        for i in range(X.shape[1]):
            c = np.corrcoef(X[:, i], y)[0, 1]
            corrs.append(abs(c))
        max_corr = max(corrs)
        assert max_corr < 0.99, f"Possible data leakage: feature-target correlation = {max_corr}"
