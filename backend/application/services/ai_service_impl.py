import logging
from typing import Dict, Any, List, Optional
from domain.ports.ai_service import AIService
from config.settings import settings
import json
import os

logger = logging.getLogger(__name__)

class AIServiceImpl(AIService):
    """Implementation of AI Service integrating Dialogflow and Scikit-learn"""

    def __init__(self):
        self.dialogflow_project = settings.dialogflow_project_id
        self.ml_model = None
        self._load_ml_model()

    def _load_ml_model(self):
        """Load or initialize Scikit-learn model"""
        import joblib
        from sklearn.neighbors import NearestNeighbors
        model_path = os.path.join(settings.ml_model_dir, "recommendation_model.pkl")
        if os.path.exists(model_path):
            self.ml_model = joblib.load(model_path)
        else:
            self.ml_model = NearestNeighbors(n_neighbors=5, algorithm="ball_tree")

    async def get_recommendations(self, user_id: int, user_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get module recommendations using Scikit-learn
        Uses user history to find similar learning patterns
        """
        if not user_history:
            return []

        try:
            features = self._extract_features(user_history)
            distances, indices = self.ml_model.kneighbors([features])
            recommendations = [
                {
                    "module_id": idx,
                    "score": float(1 / (1 + distances[0][i])),
                    "reason": "Based on similar learning patterns",
                }
                for i, idx in enumerate(indices[0])
            ]
            return sorted(recommendations, key=lambda x: x["score"], reverse=True)
        except Exception as e:
            logger.warning(f"[AIServiceImpl] Error en get_recommendations: {e}")
            return []

    async def chat_with_dialogflow(self, session_id: str, user_message: str) -> str:
        """
        Chat with Dialogflow agent
        Note: Requires Google Cloud credentials to be set up
        """
        try:
            if not self.dialogflow_project:
                return "Dialogflow not configured."
            from google.cloud import dialogflow
            client = dialogflow.SessionsClient()
            session_path = client.session_path(self.dialogflow_project, session_id)
            text_input = dialogflow.TextInput(text=user_message, language_code="es")
            query_input = dialogflow.QueryInput(text=text_input)
            response = client.detect_intent(
                request={"session": session_path, "query_input": query_input}
            )
            return response.query_result.fulfillment_text or "No response from Dialogflow"
        except ImportError:
            return "Dialogflow library not installed"
        except Exception as e:
            return f"Error: {str(e)}"

    async def predict_student_performance(self, student_id: int, module_id: int) -> Optional[float]:
        """
        Predict student performance using real data from behavioral repository
        Returns prediction score between 0.0 and 1.0, or None if unavailable
        """
        try:
            from application.services.ml.orchestrator import MLOrchestrator
            orchestrator = MLOrchestrator()
            result = orchestrator.predict_student(student_id)
            perf = result.get("performance")
            if perf is not None:
                return float(perf)
        except Exception as e:
            logger.warning(f"[AIServiceImpl] ML predict_student falló: {e}")
        try:
            from infrastructure.adapters.output.postgres.connection import PostgresConnection
            with PostgresConnection.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COALESCE(AVG(ea.score), 0) / 100.0
                    FROM exercise_attempts ea
                    JOIN exercises e ON e.id = ea.exercise_id
                    WHERE ea.student_id = %s AND e.module_id = %s
                """, (student_id, module_id))
                row = cursor.fetchone()
                if row and row[0] is not None:
                    return float(row[0])
        except Exception as e:
            logger.warning(f"[AIServiceImpl] Fallback query predict_student falló: {e}")
        logger.warning(f"[AIServiceImpl] No se pudo predecir rendimiento para student={student_id}, module={module_id}")
        return None

    async def detect_learning_path(self, student_id: int) -> Dict[str, Any]:
        """
        Detect optimal learning path for student based on real progress data
        """
        try:
            from infrastructure.adapters.output.postgres.connection import PostgresConnection
            with PostgresConnection.get_cursor() as cursor:
                cursor.execute("""
                    SELECT m.id, m.title, m.difficulty, m."order",
                           COALESCE(p.percentage, 0) as progress,
                           CASE WHEN e.status = 'completed' THEN TRUE ELSE FALSE END as completed
                    FROM modules m
                    LEFT JOIN enrollments e ON e.module_id = m.id AND e.student_id = %s
                    LEFT JOIN progress p ON p.module_id = m.id AND p.student_id = %s
                    WHERE m.is_published = TRUE AND m.status = 'approved'
                    ORDER BY m."order" ASC
                """, (student_id, student_id))
                rows = cursor.fetchall()

            if not rows:
                return {"student_id": student_id, "modules": [], "recommended_path": "unknown"}

            modules_list = []
            next_modules = []
            for r in rows:
                mod = {"id": r[0], "title": r[1], "difficulty": r[2], "order": r[3], "progress": float(r[4]), "completed": r[5]}
                modules_list.append(mod)
                if float(r[4]) < 100.0 and not r[5]:
                    next_modules.append(mod)

            return {
                "student_id": student_id,
                "recommended_path": "custom",
                "confidence": 0.9,
                "modules": [m["id"] for m in modules_list],
                "next_modules": [m["id"] for m in next_modules[:3]],
                "completed_count": sum(1 for m in modules_list if m["completed"]),
                "total_modules": len(modules_list),
                "estimated_duration_days": max(1, (len(modules_list) - sum(1 for m in modules_list if m["completed"])) * 7),
            }
        except Exception as e:
            logger.warning(f"[AIServiceImpl] detect_learning_path falló: {e}")
            return {"student_id": student_id, "modules": [], "recommended_path": "unknown"}

    @staticmethod
    def _extract_features(user_history: List[Dict[str, Any]]) -> List[float]:
        """Extract features from user history for ML model input"""
        if not user_history:
            return [0.0] * 10
        features = [
            len(user_history),
            sum(h.get("points", 0) for h in user_history),
            sum(1 for h in user_history if h.get("passed", False)),
            sum(h.get("difficulty", 1) for h in user_history) / len(user_history),
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        ]
        return features

    def train_model(self, training_data: List[List[float]]):
        """Train the recommendation model"""
        try:
            self.ml_model.fit(training_data)
            model_dir = settings.ml_model_dir
            os.makedirs(model_dir, exist_ok=True)
            import joblib
            joblib.dump(self.ml_model, os.path.join(model_dir, "recommendation_model.pkl"))
        except Exception as e:
            logger.warning(f"[AIServiceImpl] Error entrenando modelo: {e}")
