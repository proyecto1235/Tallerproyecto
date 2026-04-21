from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List

class AIService(ABC):
    """Port for AI/ML service (Dialogflow + Scikit-learn recommendations)"""
    
    @abstractmethod
    async def get_recommendations(self, user_id: int, user_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get module recommendations using ML"""
        pass
    
    @abstractmethod
    async def chat_with_dialogflow(self, session_id: str, user_message: str) -> str:
        """Chat with Dialogflow agent"""
        pass
    
    @abstractmethod
    async def predict_student_performance(self, student_id: int, module_id: int) -> float:
        """Predict student performance using ML"""
        pass
    
    @abstractmethod
    async def detect_learning_path(self, student_id: int) -> Dict[str, Any]:
        """Detect optimal learning path for student"""
        pass
