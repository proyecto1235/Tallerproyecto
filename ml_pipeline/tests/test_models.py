import pytest
import numpy as np


class TestModelTraining:
    def test_engagement_train(self, dataset):
        from ml_pipeline.src.windows import build_sliding_windows
        from ml_pipeline.src.models import train_engagement

        windows = build_sliding_windows(dataset)
        X_train, y_train = windows["engagement"]["train"]
        if len(X_train) == 0:
            pytest.skip("No training data")

        model, scaler = train_engagement(X_train, y_train)
        X_scaled = scaler.transform(X_train)
        preds = model.predict(X_scaled)
        assert len(preds) == len(y_train)
        assert all(0 <= p <= 1 for p in preds)
        assert hasattr(model, "feature_importances_")

    def test_performance_train(self, dataset):
        from ml_pipeline.src.windows import build_sliding_windows
        from ml_pipeline.src.models import train_performance

        windows = build_sliding_windows(dataset)
        X_train, y_train = windows["performance"]["train"]
        if len(X_train) == 0:
            pytest.skip("No training data")

        model, scaler = train_performance(X_train, y_train)
        X_scaled = scaler.transform(X_train)
        preds = model.predict(X_scaled)
        assert all(0 <= p <= 1 for p in preds)

    def test_dropout_train(self, dataset):
        from ml_pipeline.src.windows import build_sliding_windows
        from ml_pipeline.src.models import train_dropout

        windows = build_sliding_windows(dataset)
        X_train, y_train = windows["dropout"]["train"]
        if len(X_train) == 0 or len(np.unique(y_train)) < 2:
            pytest.skip("Not enough dropout samples")

        model, scaler = train_dropout(X_train, y_train)
        assert model.class_weight == "balanced"

    def test_frustration_train(self, dataset):
        from ml_pipeline.src.windows import build_sliding_windows
        from ml_pipeline.src.models import train_frustration

        windows = build_sliding_windows(dataset)
        X_train, y_train = windows["frustration"]["train"]
        if len(X_train) == 0:
            pytest.skip("No training data")

        model, scaler = train_frustration(X_train, y_train)
        X_scaled = scaler.transform(X_train)
        preds = model.predict(X_scaled)
        assert len(preds) == len(y_train)
        assert all(p in (0, 1, 2) for p in preds)
