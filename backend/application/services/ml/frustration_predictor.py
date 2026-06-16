import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from .base_predictor import ClassifierPredictor


class FrustrationPredictor(ClassifierPredictor):
    def __init__(self):
        super().__init__("frustration")
        self._feature_names = [
            "session_days_mean", "total_sessions_mean", "total_time_minutes_mean",
            "exercise_attempts_mean", "passed_exercises_mean", "error_rate_mean",
            "forum_interactions_mean", "content_views_mean",
        ]
        self.class_names = ["baja", "media", "alta"]

    def train(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.3, X_test_override: np.ndarray = None, y_test_override: np.ndarray = None) -> dict:
        if X_test_override is not None and y_test_override is not None:
            X_train, X_test = X, X_test_override
            y_train, y_test = y, y_test_override
        else:
            classes, class_counts = np.unique(y, return_counts=True)
            if np.min(class_counts) >= 2:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=42, stratify=y
                )
            else:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=test_size, random_state=42
                )
        self._scaler.fit(X_train)
        X_train_scaled = self._scaler.transform(X_train)
        X_test_scaled = self._scaler.transform(X_test)

        self._model = RandomForestClassifier(
            n_estimators=200, max_depth=10, random_state=42,
            class_weight="balanced", n_jobs=-1,
        )
        self._model.fit(X_train_scaled, y_train)
        self._is_trained = True
        self.save()

        test_metrics = self.evaluate(X_test_scaled, y_test)

        return {
            "test": test_metrics,
            "feature_importances": self.get_feature_importances(),
            "n_samples": len(X),
            "n_train": len(X_train),
            "n_test": len(X_test),
        }

    def predict(self, X: np.ndarray) -> int:
        scaled = self._scaler.transform(X.reshape(1, -1))
        return int(self._model.predict(scaled)[0])

    def predict_proba(self, X: np.ndarray) -> list:
        scaled = self._scaler.transform(X.reshape(1, -1))
        return [round(float(p), 4) for p in self._model.predict_proba(scaled)[0]]
