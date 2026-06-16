import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from .base_predictor import ClassifierPredictor


class DropoutPredictor(ClassifierPredictor):
    def __init__(self):
        super().__init__("dropout")
        self._feature_names = [
            "session_days_mean", "total_sessions_mean", "total_time_minutes_mean",
            "exercise_attempts_mean", "passed_exercises_mean", "error_rate_mean",
            "forum_interactions_mean", "content_views_mean",
        ]

    def train(self, X: np.ndarray, y: np.ndarray, test_size: float = 0.3, X_test_override: np.ndarray = None, y_test_override: np.ndarray = None) -> dict:
        if X_test_override is not None and y_test_override is not None:
            X_train, X_test = X, X_test_override
            y_train, y_test = y, y_test_override
        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
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

        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(self._model, X_train_scaled, y_train, cv=skf, scoring="roc_auc")

        test_metrics = self.evaluate(X_test_scaled, y_test)

        return {
            "test": test_metrics,
            "cv_roc_auc_mean": round(float(np.mean(cv_scores)), 4),
            "cv_roc_auc_std": round(float(np.std(cv_scores)), 4),
            "feature_importances": self.get_feature_importances(),
            "n_samples": len(X),
            "n_train": len(X_train),
            "n_test": len(X_test),
            "class_distribution": {
                "no_dropout": int(np.sum(y_train == 0)),
                "dropout": int(np.sum(y_train == 1)),
            },
        }

    def predict_proba(self, X: np.ndarray) -> float:
        scaled = self._scaler.transform(X.reshape(1, -1))
        return float(self._model.predict_proba(scaled)[0][1])

    def predict(self, X: np.ndarray) -> int:
        scaled = self._scaler.transform(X.reshape(1, -1))
        return int(self._model.predict(scaled)[0])
