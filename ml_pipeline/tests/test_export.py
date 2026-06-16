import pytest
import numpy as np


class TestExport:
    def test_save_and_load_model(self, tmp_path, monkeypatch):
        from ml_pipeline.src.export import save_model, load_model, MODEL_DIR
        monkeypatch.setattr("ml_pipeline.src.export.MODEL_DIR", str(tmp_path))
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        X = np.array([[1.0], [2.0], [3.0]])
        y = np.array([0.0, 0.5, 1.0])
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(X, y)
        scaler = StandardScaler()
        scaler.fit(X)
        save_model(model, scaler, ["f1"], "test_model")
        loaded = load_model("test_model")
        assert loaded is not None
        preds = loaded.predict([[1.5]])
        assert len(preds) == 1

    def test_save_and_load_scaler(self, tmp_path, monkeypatch):
        from ml_pipeline.src.export import save_model, load_scaler, MODEL_DIR
        monkeypatch.setattr("ml_pipeline.src.export.MODEL_DIR", str(tmp_path))
        from sklearn.preprocessing import StandardScaler
        from sklearn.ensemble import RandomForestRegressor
        X = np.array([[1.0], [2.0], [3.0]])
        scaler = StandardScaler()
        scaler.fit(X)
        model = RandomForestRegressor(n_estimators=10)
        model.fit(X, [0, 0.5, 1])
        save_model(model, scaler, ["f1"], "test_scaler2")
        loaded = load_scaler("test_scaler2")
        assert loaded is not None
        result = loaded.transform([[2.0]])
        assert abs(float(result[0][0])) < 2.0

    def test_save_and_load_features(self, tmp_path, monkeypatch):
        from ml_pipeline.src.export import save_model, load_features, MODEL_DIR
        monkeypatch.setattr("ml_pipeline.src.export.MODEL_DIR", str(tmp_path))
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        model = RandomForestRegressor(n_estimators=10)
        scaler = StandardScaler()
        features = ["f1", "f2", "f3"]
        save_model(model, scaler, features, "test_feats")
        loaded = load_features("test_feats")
        assert loaded == features

    def test_model_exists(self, tmp_path, monkeypatch):
        from ml_pipeline.src.export import save_model, model_exists, MODEL_DIR
        monkeypatch.setattr("ml_pipeline.src.export.MODEL_DIR", str(tmp_path))
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.preprocessing import StandardScaler
        model = RandomForestRegressor(n_estimators=10)
        scaler = StandardScaler()
        save_model(model, scaler, ["f1"], "exists_test")
        assert model_exists("exists_test") is True
        assert model_exists("nonexistent") is False

    def test_load_nonexistent_returns_none(self, tmp_path, monkeypatch):
        from ml_pipeline.src.export import load_model, load_scaler, load_features, MODEL_DIR
        monkeypatch.setattr("ml_pipeline.src.export.MODEL_DIR", str(tmp_path))
        assert load_model("no_such_model") is None
        assert load_scaler("no_such_scaler") is None
        assert load_features("no_such_features") is None
