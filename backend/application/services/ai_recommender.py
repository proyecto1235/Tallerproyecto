from typing import List, Dict, Any
from domain.ports.ai_service import AIService
from infrastructure.adapters.output.mongo.event_repository_impl import EventRepository

class RecommendationService:
    """Service for getting AI recommendations"""
    
    def __init__(self, ai_service: AIService, event_repo: EventRepository):
        self.ai_service = ai_service
        self.event_repo = event_repo
    
    async def get_personalized_recommendations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get personalized recommendations for a user"""
        # Get user's exercise history
        history = await self.event_repo.get_user_exercise_history(user_id)
        
        # Get ML recommendations
        recommendations = await self.ai_service.get_recommendations(user_id, history)
        
        # Log the recommendation request
        await self.event_repo.log_event(
            "recommendations_requested",
            user_id,
            {"count": len(recommendations)}
        )
        
        return recommendations
    
    async def detect_learning_style(self, user_id: int) -> Dict[str, Any]:
        """Detect student's learning style"""
        history = await self.event_repo.get_user_exercise_history(user_id)
        
        learning_path = await self.ai_service.detect_learning_path(user_id)
        
        await self.event_repo.log_event(
            "learning_path_detected",
            user_id,
            learning_path
        )
        
        return learning_path
