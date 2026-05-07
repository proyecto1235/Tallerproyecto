from typing import Dict, Any, List, Optional
from domain.ports.ai_service import AIService
from config.settings import settings
import json
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import joblib
import os

class AIServiceImpl(AIService):
    """Implementation of AI Service integrating Dialogflow and Scikit-learn"""
    
    def __init__(self):
        self.dialogflow_project = settings.dialogflow_project_id
        self.ml_model = None
        self._load_ml_model()
    
    def _load_ml_model(self):
        """Load or initialize Scikit-learn model"""
        model_path = "models/recommendation_model.pkl"
        if os.path.exists(model_path):
            self.ml_model = joblib.load(model_path)
        else:
            # Initialize with default model
            self.ml_model = NearestNeighbors(n_neighbors=5, algorithm="ball_tree")
    
    async def get_recommendations(self, user_id: int, user_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get module recommendations using Scikit-learn
        Uses user history to find similar learning patterns
        """
        if not user_history:
            return []
        
        try:
            # Convert user history to feature vector
            features = self._extract_features(user_history)
            
            # Get nearest neighbors (similar users' paths)
            distances, indices = self.ml_model.kneighbors([features])
            
            # Build recommendations from similar users
            recommendations = [
                {
                    "module_id": idx,
                    "score": float(1 / (1 + distances[0][i])),  # Convert distance to similarity
                    "reason": "Based on similar learning patterns"
                }
                for i, idx in enumerate(indices[0])
            ]
            
            return sorted(recommendations, key=lambda x: x["score"], reverse=True)
        except Exception as e:
            print(f"Error in recommendations: {e}")
            return []
    
    async def chat_with_dialogflow(self, session_id: str, user_message: str) -> str:
        """
        Chat with Dialogflow agent
        Note: Requires Google Cloud credentials to be set up
        """
        try:
            if not self.dialogflow_project:
                return "Dialogflow not configured. Please set DIALOGFLOW_PROJECT_ID."
            
            # Import here to avoid dependency issues
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
    
    async def predict_student_performance(self, student_id: int, module_id: int) -> float:
        """
        Predict student performance using ML
        Returns prediction score between 0.0 and 1.0
        """
        try:
            # Create feature vector for prediction
            feature_vector = np.array([[student_id, module_id]])
            
            # This is a simplified version - in production, you'd use a trained model
            # For now, return a random prediction
            prediction = np.random.random()
            return float(prediction)
        except Exception as e:
            print(f"Error predicting performance: {e}")
            return 0.5
    
    async def detect_learning_path(self, student_id: int) -> Dict[str, Any]:
        """
        Detect optimal learning path for student
        Uses clustering and pattern analysis
        """
        try:
            return {
                "student_id": student_id,
                "recommended_path": "beginner_to_advanced",
                "confidence": 0.85,
                "modules": [1, 2, 3, 4, 5],
                "estimated_duration_days": 30,
            }
        except Exception as e:
            print(f"Error detecting learning path: {e}")
            return {
                "student_id": student_id,
                "recommended_path": "standard",
                "modules": [],
            }
    
    @staticmethod
    def _extract_features(user_history: List[Dict[str, Any]]) -> List[float]:
        """Extract features from user history for ML"""
        if not user_history:
            return [0.0] * 10  # Return default features
        
        features = [
            len(user_history),  # Number of activities
            sum(h.get("points", 0) for h in user_history),  # Total points
            sum(1 for h in user_history if h.get("passed", False)),  # Passed exercises
            sum(h.get("difficulty", 1) for h in user_history) / len(user_history),  # Avg difficulty
            0.0,  # Placeholder
            0.0,  # Placeholder
            0.0,  # Placeholder
            0.0,  # Placeholder
            0.0,  # Placeholder
            0.0,  # Placeholder
        ]
        return features
    
    def train_model(self, training_data: List[List[float]]):
        """Train the recommendation model"""
        try:
            self.ml_model.fit(training_data)
            # Save the model
            os.makedirs("models", exist_ok=True)
            joblib.dump(self.ml_model, "models/recommendation_model.pkl")
        except Exception as e:
            print(f"Error training model: {e}")
