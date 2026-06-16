import pytest
import numpy as np


class TestNoDataLeakage:
    """Verify that no target variable appears as a feature in any model."""

    def test_engagement_features_dont_contain_engagement(self, training_data):
        X, y = training_data["engagement"]
        if len(X) == 0:
            pytest.skip("No training data")
        for i in range(X.shape[1]):
            col_data = X[:, i]
            corr = np.corrcoef(col_data, y)[0, 1]
            if abs(corr) > 0.95:
                pytest.fail(f"Feature {i} has correlation {corr:.3f} with target engagement_score")

    def test_performance_features_dont_contain_performance(self, training_data):
        X, y = training_data["performance"]
        if len(X) == 0:
            pytest.skip("No training data")
        for i in range(X.shape[1]):
            col_data = X[:, i]
            corr = np.corrcoef(col_data, y)[0, 1]
            if abs(corr) > 0.95:
                pytest.fail(f"Feature {i} has correlation {corr:.3f} with target performance_score")

    def test_dropout_features_dont_contain_dropout(self, training_data):
        X, y = training_data["dropout"]
        if len(X) == 0:
            pytest.skip("No training data")
        for i in range(X.shape[1]):
            col_data = X[:, i]
            corr = np.corrcoef(col_data, y)[0, 1]
            if abs(corr) > 0.90:
                pytest.fail(f"Feature {i} has correlation {corr:.3f} with target dropout")

    def test_frustration_features_dont_contain_frustration(self, training_data):
        X, y = training_data["frustration"]
        if len(X) == 0:
            pytest.skip("No training data")
        for i in range(X.shape[1]):
            col_data = X[:, i]
            corr = np.corrcoef(col_data, y)[0, 1]
            if abs(corr) > 0.95:
                pytest.fail(f"Feature {i} has correlation {corr:.3f} with target frustration")
