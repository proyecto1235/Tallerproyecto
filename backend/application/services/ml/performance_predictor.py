import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from .base_predictor import RegressorPredictor


class PerformancePredictor(RegressorPredictor):
    def __init__(self):
        super().__init__("performance")
        self._feature_names = [
            "session_days_w1", "total_sessions_w1", "total_time_minutes_w1",
            "exercise_attempts_w1", "passed_exercises_w1", "error_rate_w1",
            "forum_interactions_w1", "content_views_w1",
            "session_days_w2", "total_sessions_w2", "total_time_minutes_w2",
            "exercise_attempts_w2", "passed_exercises_w2", "error_rate_w2",
            "forum_interactions_w2", "content_views_w2",
            "session_days_w3", "total_sessions_w3", "total_time_minutes_w3",
            "exercise_attempts_w3", "passed_exercises_w3", "error_rate_w3",
            "forum_interactions_w3", "content_views_w3",
            "session_days_w4", "total_sessions_w4", "total_time_minutes_w4",
            "exercise_attempts_w4", "passed_exercises_w4", "error_rate_w4",
            "forum_interactions_w4", "content_views_w4",
        ]

    def train(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.3, X_test_override: np.ndarray = None, y_test_override: np.ndarray = None) -> dict:
        if X_test_override is not None and y_test_override is not None:
            X_train, X_test = X, X_test_override
            y_train, y_test = y, y_test_override
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42
            )
        self._scaler.fit(X_train)
        X_train_scaled = self._scaler.transform(X_train)
        X_test_scaled = self._scaler.transform(X_test)

        self._model = RandomForestRegressor(
            n_estimators=200, max_depth=15, random_state=42, n_jobs=-1,
        )
        self._model.fit(X_train_scaled, y_train)
        self._is_trained = True
        self.save()

        train_pred = self._model.predict(X_train_scaled)
        train_metrics = {
            "mae": float(np.mean(np.abs(y_train - train_pred))),
            "rmse": float(np.sqrt(np.mean((y_train - train_pred) ** 2))),
            "r2": float(1 - np.sum((y_train - train_pred) ** 2) / np.sum((y_train - np.mean(y_train)) ** 2)),
        }

        test_metrics = self.evaluate(X_test_scaled, y_test)

        return {
            "train": {k: round(v, 4) for k, v in train_metrics.items()},
            "test": {k: round(v, 4) for k, v in test_metrics.items()},
            "feature_importances": self.get_feature_importances(),
            "n_samples": len(X),
            "n_train": len(X_train),
            "n_test": len(X_test),
        }

    def predict(self, X: np.ndarray) -> float:
        scaled = self._scaler.transform(X.reshape(1, -1))
        return float(np.clip(self._model.predict(scaled)[0], 0, 1))
