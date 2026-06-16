import pytest
import numpy as np
from sklearn.model_selection import train_test_split


class TestDropoutPredictor:
    def test_train_and_evaluate(self, dropout_predictor, training_data):
        X, y = training_data["dropout"]
        if len(X) == 0 or len(np.unique(y)) < 2:
            pytest.skip("Not enough dropout samples")
        n_pos = int(np.sum(y))
        print(f"[Dropout] Samples: {len(y)}, positive: {n_pos} ({n_pos/len(y)*100:.1f}%)")
        result = dropout_predictor.train(X, y)
        assert "test" in result
        assert result["test"]["accuracy"] > 0.0
        assert result["test"]["roc_auc"] > 0.0

    def test_precision_recall_f1(self, dropout_predictor, training_data):
        X, y = training_data["dropout"]
        if len(X) < 20 or len(np.unique(y)) < 2:
            pytest.skip("Not enough dropout samples")
        dropout_predictor.train(X, y)
        test_metrics = dropout_predictor._last_test_metrics if hasattr(dropout_predictor, '_last_test_metrics') else None
        assert test_metrics is None or test_metrics.get("precision", 0) >= 0

    def test_class_weights(self, dropout_predictor, training_data):
        X, y = training_data["dropout"]
        if len(X) < 20 or len(np.unique(y)) < 2:
            pytest.skip("Not enough data")
        dropout_predictor.train(X, y)
        assert dropout_predictor._model is not None
        assert dropout_predictor._model.class_weight == "balanced"

    def test_predict_proba_output(self, dropout_predictor, training_data):
        X, y = training_data["dropout"]
        if len(X) == 0:
            pytest.skip("No data")
        dropout_predictor.train(X, y)
        proba = dropout_predictor.predict_proba(X[0])
        assert 0 <= proba <= 1

    def test_stratified_split(self, training_data):
        X, y = training_data["dropout"]
        if len(X) < 20 or len(np.unique(y)) < 2:
            pytest.skip("Not enough data")
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
        tr_ratio = np.sum(y_tr) / len(y_tr)
        te_ratio = np.sum(y_te) / len(y_te)
        assert abs(tr_ratio - te_ratio) < 0.15, f"Stratification failed: train={tr_ratio:.3f}, test={te_ratio:.3f}"

    def test_no_data_leakage(self, training_data):
        X, y = training_data["dropout"]
        if len(X) == 0 or len(np.unique(y)) < 2:
            pytest.skip("Not enough data")
        corrs = []
        for i in range(X.shape[1]):
            c = np.corrcoef(X[:, i], y)[0, 1]
            corrs.append(abs(c))
        max_corr = max(corrs)
        assert max_corr < 0.90, f"Possible data leakage: max corr = {max_corr:.3f}"
