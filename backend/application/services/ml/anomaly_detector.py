import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import List, Dict, Any, Optional
from config.settings import settings

MODEL_DIR = settings.ml_model_dir

FEATURE_NAMES = [
    "session_days", "total_sessions", "total_time_minutes",
    "exercise_attempts", "passed_exercises", "error_rate",
    "forum_interactions", "content_views",
]


class AnomalyDetector:
    def __init__(self, contamination: float = 0.05):
        self._model: Optional[IsolationForest] = None
        self._scaler: Optional[StandardScaler] = None
        self._contamination = contamination
        self._is_trained = False
        self._feature_names = FEATURE_NAMES
        os.makedirs(MODEL_DIR, exist_ok=True)
        self._load()

    def _path(self, name: str) -> str:
        return os.path.join(MODEL_DIR, name)

    def _load(self) -> bool:
        try:
            if os.path.exists(self._path("anomaly_model.pkl")):
                self._model = joblib.load(self._path("anomaly_model.pkl"))
            if os.path.exists(self._path("anomaly_scaler.pkl")):
                self._scaler = joblib.load(self._path("anomaly_scaler.pkl"))
            if os.path.exists(self._path("anomaly_trained.pkl")):
                self._is_trained = joblib.load(self._path("anomaly_trained.pkl"))
            return self._is_trained
        except Exception:
            return False

    def _save(self):
        joblib.dump(self._model, self._path("anomaly_model.pkl"))
        joblib.dump(self._scaler, self._path("anomaly_scaler.pkl"))
        joblib.dump(self._is_trained, self._path("anomaly_trained.pkl"))

    def train(self, X: np.ndarray) -> dict:
        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        self._model = IsolationForest(
            n_estimators=200,
            contamination=self._contamination,
            random_state=42,
            n_jobs=-1,
        )
        self._model.fit(X_scaled)
        self._is_trained = True
        self._save()

        preds = self._model.predict(X_scaled)
        n_anomalies = int(np.sum(preds == -1))

        return {
            "n_samples": len(X),
            "n_anomalies": n_anomalies,
            "anomaly_rate": round(n_anomalies / len(X), 4),
            "contamination": self._contamination,
        }

    def extract_deltas(
        self, historical_data: List[Dict[str, Any]]
    ) -> Optional[np.ndarray]:
        if len(historical_data) < 2:
            return None

        sorted_data = sorted(historical_data, key=lambda x: x.get("week", 0))
        deltas = []
        for i in range(1, len(sorted_data)):
            prev = sorted_data[i - 1]
            curr = sorted_data[i]
            delta = []
            for feat in self._feature_names:
                delta.append(curr.get(feat, 0) - prev.get(feat, 0))
            deltas.append(delta)

        if len(deltas) < 2:
            return None

        return np.array(deltas).flatten()

    def predict(self, delta_features: np.ndarray) -> Dict[str, Any]:
        if not self._is_trained:
            return {"is_anomaly": False, "anomaly_score": 0.0, "risk": "unknown"}

        X = delta_features.reshape(1, -1)
        X_scaled = self._scaler.transform(X)
        pred = int(self._model.predict(X_scaled)[0])
        score = float(self._model.score_samples(X_scaled)[0])

        is_anomaly = pred == -1
        if is_anomaly and score < -0.4:
            risk = "high"
        elif is_anomaly:
            risk = "medium"
        else:
            risk = "low"

        return {
            "is_anomaly": bool(is_anomaly),
            "anomaly_score": round(score, 4),
            "risk": risk,
        }

    def batch_predict(
        self, delta_features_list: np.ndarray
    ) -> List[Dict[str, Any]]:
        if not self._is_trained:
            return [{"is_anomaly": False, "anomaly_score": 0.0, "risk": "unknown"} for _ in range(len(delta_features_list))]

        X_scaled = self._scaler.transform(delta_features_list)
        preds = self._model.predict(X_scaled)
        scores = self._model.score_samples(X_scaled)

        results = []
        for i in range(len(delta_features_list)):
            is_anomaly = preds[i] == -1
            if is_anomaly and scores[i] < -0.4:
                risk = "high"
            elif is_anomaly:
                risk = "medium"
            else:
                risk = "low"
            results.append({
                "is_anomaly": bool(is_anomaly),
                "anomaly_score": round(float(scores[i]), 4),
                "risk": risk,
            })
        return results
