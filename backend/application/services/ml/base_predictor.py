import os
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, mean_absolute_error, mean_squared_error, r2_score,
    confusion_matrix, classification_report,
)
import joblib
import json
from typing import Dict, List, Any, Optional, Tuple
from config.settings import settings

MODEL_DIR = settings.ml_model_dir


class BasePredictor:
    def __init__(self, name: str):
        self.name = name
        self._model = None
        self._scaler = StandardScaler()
        self._feature_names: List[str] = []
        self._is_trained = False
        os.makedirs(MODEL_DIR, exist_ok=True)

    def predict_batch(self, X: np.ndarray) -> np.ndarray:
        """Batch prediction: X is 2D (n_samples, n_features). Returns 1D (n_samples,).
        Falls back to per-sample prediction if batch fails (sklearn compat)."""
        try:
            scaled = self._scaler.transform(X)
            return self._model.predict(scaled)
        except Exception:
            return np.array([
                self.predict(x) for x in X
            ])

    def _path(self, suffix: str) -> str:
        return os.path.join(MODEL_DIR, f"{self.name}_{suffix}")

    def save(self):
        if self._model is not None:
            joblib.dump(self._model, self._path("model.pkl"))
        joblib.dump(self._scaler, self._path("scaler.pkl"))
        with open(self._path("features.json"), "w") as f:
            json.dump(self._feature_names, f)
        joblib.dump(self._is_trained, self._path("trained.pkl"))

    def load(self) -> bool:
        try:
            if os.path.exists(self._path("model.pkl")):
                self._model = joblib.load(self._path("model.pkl"))
            if os.path.exists(self._path("scaler.pkl")):
                self._scaler = joblib.load(self._path("scaler.pkl"))
            if os.path.exists(self._path("features.json")):
                with open(self._path("features.json")) as f:
                    self._feature_names = json.load(f)
            if os.path.exists(self._path("trained.pkl")):
                self._is_trained = joblib.load(self._path("trained.pkl"))
            return self._is_trained
        except Exception:
            return False

    def get_feature_importances(self) -> List[Dict[str, Any]]:
        if not hasattr(self._model, "feature_importances_"):
            return []
        importances = self._model.feature_importances_
        names = self._feature_names if len(self._feature_names) == len(importances) else [f"f{i}" for i in range(len(importances))]
        pairs = sorted(zip(names, importances), key=lambda x: -x[1])
        return [
            {"feature": p[0], "importance": round(float(p[1]), 4)}
            for p in pairs
        ]

    def get_top_features(self, n: int = 5) -> List[str]:
        return [p["feature"] for p in self.get_feature_importances()[:n]]


class RegressorPredictor(BasePredictor):
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        y_pred = self._model.predict(X_test)
        return {
            "mae": round(float(mean_absolute_error(y_test, y_pred)), 4),
            "rmse": round(float(np.sqrt(mean_squared_error(y_test, y_pred))), 4),
            "r2": round(float(r2_score(y_test, y_pred)), 4),
        }


class ClassifierPredictor(BasePredictor):
    def predict_batch(self, X: np.ndarray) -> np.ndarray:
        try:
            scaled = self._scaler.transform(X)
            return self._model.predict(scaled)
        except Exception:
            return np.array([self.predict(x) for x in X])

    def predict_proba_batch(self, X: np.ndarray) -> np.ndarray:
        try:
            scaled = self._scaler.transform(X)
            return self._model.predict_proba(scaled)
        except Exception:
            return np.array([self.predict_proba(x.reshape(1, -1))[0] for x in X])

    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        y_pred = self._model.predict(X_test)
        result = {
            "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "classification_report": classification_report(y_test, y_pred, output_dict=True, zero_division=0),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }
        if len(np.unique(y_test)) == 2:
            y_proba = self._model.predict_proba(X_test)[:, 1]
            result["precision"] = round(float(precision_score(y_test, y_pred, zero_division=0)), 4)
            result["recall"] = round(float(recall_score(y_test, y_pred, zero_division=0)), 4)
            result["f1"] = round(float(f1_score(y_test, y_pred, zero_division=0)), 4)
            try:
                result["roc_auc"] = round(float(roc_auc_score(y_test, y_proba)), 4)
            except Exception:
                result["roc_auc"] = 0.5
        return result
