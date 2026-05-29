from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json
import random


MODEL_DIR = "models"


class StudentPredictor:
    def __init__(self):
        self._dropout_model: Optional[RandomForestClassifier] = None
        self._frustration_model: Optional[RandomForestClassifier] = None
        self._engagement_model: Optional[RandomForestRegressor] = None
        self._performance_model: Optional[RandomForestRegressor] = None
        self._scaler: Optional[StandardScaler] = None
        self._feature_cols: List[str] = []
        self._load_or_init_models()

    def _model_path(self, name: str) -> str:
        return os.path.join(MODEL_DIR, f"{name}.pkl")

    def _load_or_init_models(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        try:
            if os.path.exists(self._model_path("dropout")):
                self._dropout_model = joblib.load(self._model_path("dropout"))
            if os.path.exists(self._model_path("frustration")):
                self._frustration_model = joblib.load(self._model_path("frustration"))
            if os.path.exists(self._model_path("engagement")):
                self._engagement_model = joblib.load(self._model_path("engagement"))
            if os.path.exists(self._model_path("performance")):
                self._performance_model = joblib.load(self._model_path("performance"))
            if os.path.exists(self._model_path("scaler")):
                self._scaler = joblib.load(self._model_path("scaler"))
            if os.path.exists(self._model_path("feature_cols")):
                with open(self._model_path("feature_cols"), "r") as f:
                    self._feature_cols = json.load(f)
        except Exception as e:
            print(f"[Predictor] Error loading models: {e}")

        needs_train = any(m is None for m in [
            self._dropout_model, self._frustration_model,
            self._engagement_model, self._performance_model,
            self._scaler,
        ])
        if needs_train:
            self._train_with_synthetic_data()

    @staticmethod
    def _extract_features(profile: Dict[str, Any]) -> np.ndarray:
        return np.array([[
            profile.get("session_days_30d", 0),
            profile.get("total_sessions_30d", 0),
            profile.get("total_time_minutes_30d", 0),
            profile.get("total_events_30d", 0),
            profile.get("total_exercise_attempts_30d", 0),
            profile.get("passed_exercises_30d", 0),
            profile.get("error_rate", 0),
            profile.get("frustration_signals_30d", 0),
            profile.get("engagement_score", 0.5),
            profile.get("avg_session_minutes", 0),
        ]])

    @property
    def feature_cols(self):
        return [
            "session_days_30d", "total_sessions_30d", "total_time_minutes_30d",
            "total_events_30d", "total_exercise_attempts_30d", "passed_exercises_30d",
            "error_rate", "frustration_signals_30d", "engagement_score", "avg_session_minutes",
        ]

    def _train_with_synthetic_data(self):
        random.seed(42)
        np.random.seed(42)
        n = 2000

        data = []
        for _ in range(n):
            session_days = random.randint(0, 30)
            total_sessions = random.randint(0, 60)
            total_time = round(random.uniform(0, 3000), 2)
            total_events = random.randint(0, 500)
            attempts = random.randint(0, 100)
            passed = random.randint(0, max(1, attempts))
            error_rate = round(random.uniform(0, 1), 4)
            frustration = random.randint(0, 30)
            engagement = round(random.uniform(0, 1), 4)
            avg_session = round(random.uniform(0, 120), 2)

            data.append([session_days, total_sessions, total_time, total_events,
                         attempts, passed, error_rate, frustration, engagement, avg_session])

        X = np.array(data)
        self._scaler = StandardScaler()
        X_scaled = self._scaler.fit_transform(X)

        def _risk_label(row):
            if row[4] < 3 and row[0] < 5 and row[6] > 0.5:
                return 1 if random.random() < 0.8 else 0
            if row[8] < 0.3 and row[7] > 5:
                return 1 if random.random() < 0.7 else 0
            return 1 if random.random() < 0.15 else 0

        def _frustration_label(row):
            if row[7] > 10 and row[6] > 0.4:
                return 2
            if row[7] > 5 or row[6] > 0.3:
                return 1
            return 0

        dropout_y = np.array([_risk_label(row) for row in data])
        frustration_y = np.array([_frustration_label(row) for row in data])
        engagement_y = np.array([row[8] for row in data])

        perf_scores = []
        for row in data:
            base = (row[5] / max(1, row[4])) * 0.5 + row[8] * 0.3 + (1 - row[6]) * 0.2
            perf_scores.append(min(1.0, base + random.uniform(-0.1, 0.1)))
        performance_y = np.array(perf_scores)

        self._dropout_model = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42, class_weight="balanced",
        )
        self._dropout_model.fit(X_scaled, dropout_y)

        self._frustration_model = RandomForestClassifier(
            n_estimators=100, max_depth=10, random_state=42, class_weight="balanced",
        )
        self._frustration_model.fit(X_scaled, frustration_y)

        self._engagement_model = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42,
        )
        self._engagement_model.fit(X_scaled, engagement_y)

        self._performance_model = RandomForestRegressor(
            n_estimators=100, max_depth=10, random_state=42,
        )
        self._performance_model.fit(X_scaled, performance_y)

        self._feature_cols = self.feature_cols
        self._save_models()

    def _save_models(self):
        os.makedirs(MODEL_DIR, exist_ok=True)
        joblib.dump(self._dropout_model, self._model_path("dropout"))
        joblib.dump(self._frustration_model, self._model_path("frustration"))
        joblib.dump(self._engagement_model, self._model_path("engagement"))
        joblib.dump(self._performance_model, self._model_path("performance"))
        joblib.dump(self._scaler, self._model_path("scaler"))
        with open(self._model_path("feature_cols"), "w") as f:
            json.dump(self._feature_cols, f)

    def train_on_real_data(self, behavioral_repo) -> Dict:
        try:
            db = behavioral_repo.get_db()
            user_ids = db.engagement_scores.distinct("user_id")
            if len(user_ids) < 10:
                return {"status": "skipped", "reason": f"Only {len(user_ids)} users with data"}

            X_list, dropout_y, frustration_y, engagement_y, perf_y = [], [], [], [], []
            for uid in user_ids:
                profile = behavioral_repo.get_student_behavioral_profile(uid)
                features = self._extract_features(profile)[0]

                db = behavioral_repo.get_db()
                attempts = list(db.exercise_attempts.find({"user_id": uid}))
                frustration = list(db.frustration_signals.find({"user_id": uid}))
                engagement_doc = db.engagement_scores.find_one({"user_id": uid})
                code_ops = list(db.code_analysis.find({"user_id": uid}))

                passed_ratio = sum(1 for a in attempts if a.get("passed")) / max(1, len(attempts))
                attempts_per_exercise = len(attempts) / max(1, len(set(a.get("exercise_id") for a in attempts)))
                error_rate = sum(1 for c in code_ops if c.get("has_error")) / max(1, len(code_ops))

                dropout_risk = 1 if (len(attempts) < 3 and error_rate > 0.5) else 0
                frustration_level = 0
                if len(frustration) > 10:
                    frustration_level = 2
                elif len(frustration) > 3:
                    frustration_level = 1
                engagement_score = engagement_doc.get("engagement_score", 0.5) if engagement_doc else 0.5
                perf_score = passed_ratio * 0.6 + engagement_score * 0.4

                X_list.append(features)
                dropout_y.append(dropout_risk)
                frustration_y.append(frustration_level)
                engagement_y.append(engagement_score)
                perf_y.append(perf_score)

            if len(X_list) < 10:
                return {"status": "skipped", "reason": "Not enough labeled data"}

            X = np.array(X_list)
            self._scaler = StandardScaler()
            X_scaled = self._scaler.fit_transform(X)

            self._dropout_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight="balanced")
            self._dropout_model.fit(X_scaled, dropout_y)

            self._frustration_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, class_weight="balanced")
            self._frustration_model.fit(X_scaled, frustration_y)

            self._engagement_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
            self._engagement_model.fit(X_scaled, engagement_y)

            self._performance_model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
            self._performance_model.fit(X_scaled, perf_y)

            self._feature_cols = self.feature_cols
            self._save_models()
            return {"status": "trained", "samples": len(X_list)}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    async def predict_metrics(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        features = self._extract_features(profile)
        features_scaled = self._scaler.transform(features)

        dropout_proba = float(self._dropout_model.predict_proba(features_scaled)[0][1]) if hasattr(self._dropout_model, "predict_proba") else float(self._dropout_model.predict(features_scaled)[0])
        frustration_class = int(self._frustration_model.predict(features_scaled)[0])
        engagement_pred = float(np.clip(self._engagement_model.predict(features_scaled)[0], 0, 1))
        performance_pred = float(np.clip(self._performance_model.predict(features_scaled)[0], 0, 1))

        dropout_proba = float(np.clip(dropout_proba, 0, 1))

        return {
            "dropout_risk": round(dropout_proba, 4),
            "dropout_risk_label": "high" if dropout_proba > 0.6 else ("medium" if dropout_proba > 0.3 else "low"),
            "frustration_level": frustration_class,
            "frustration_label": "high" if frustration_class == 2 else ("medium" if frustration_class == 1 else "low"),
            "engagement_score": round(engagement_pred, 4),
            "engagement_label": "high" if engagement_pred > 0.7 else ("medium" if engagement_pred > 0.4 else "low"),
            "performance_score": round(performance_pred, 4),
            "performance_label": "excellent" if performance_pred > 0.8 else ("good" if performance_pred > 0.6 else ("average" if performance_pred > 0.4 else "low")),
        }

    async def classify_students(self, profiles: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        at_risk = []
        excellent = []
        for p in profiles:
            metrics = await self.predict_metrics(p)
            uid = p.get("user_id", "unknown")
            if metrics["dropout_risk"] > 0.5 or metrics["performance_score"] < 0.3:
                at_risk.append({"user_id": uid, **metrics})
            if metrics["performance_score"] > 0.8:
                excellent.append({"user_id": uid, **metrics})
        return {"at_risk": at_risk, "excellent": excellent}

    async def get_insights(self, profile: Dict[str, Any]) -> List[str]:
        metrics = await self.predict_metrics(profile)
        insights = []
        if metrics["dropout_risk"] > 0.6:
            insights.append("Alto riesgo de abandono. El estudiante ha tenido poca actividad reciente.")
        elif metrics["dropout_risk"] > 0.3:
            insights.append("Riesgo moderado de abandono. Monitorear su progreso semanalmente.")

        if metrics["frustration_level"] >= 2:
            insights.append("Nivel alto de frustración detectado. Sugerir ejercicios más sencillos o pausa.")
        elif metrics["frustration_level"] == 1:
            insights.append("Signos de frustración. Revisar ejercicios recientes.")

        if metrics["engagement_score"] < 0.4:
            insights.append("Bajo engagement. Recomendar contenido más interactivo o gamificado.")
        elif metrics["engagement_score"] > 0.8:
            insights.append("Alto engagement. El estudiante está muy comprometido con la plataforma.")

        if metrics["performance_score"] < 0.3:
            insights.append("Rendimiento bajo. Considerar repaso de fundamentos.")
        elif metrics["performance_score"] > 0.8:
            insights.append("Rendimiento sobresaliente. Ofrecer retos avanzados.")

        return insights
