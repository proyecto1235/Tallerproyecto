from domain.ports.ai_service import AIService
from domain.ports.module_repository import ModuleRepository
from infrastructure.adapters.output.mongo.event_repository_impl import EventRepository

class GetRecommendationsUseCase:
    """Use case for getting module recommendations"""
    
    def __init__(
        self,
        ai_service: AIService,
        module_repository: ModuleRepository,
        event_repository: EventRepository
    ):
        self.ai_service = ai_service
        self.module_repository = module_repository
        self.event_repository = event_repository
    
    async def execute(self, user_id: int) -> dict:
        """Get recommendations for a user"""
        try:
            # Get user's exercise history
            history = await self.event_repository.get_user_exercise_history(user_id)
            
            # Get AI recommendations
            recommendations = await self.ai_service.get_recommendations(user_id, history)
            
            # Enrich with module details
            enriched_recommendations = []
            for rec in recommendations:
                module = await self.module_repository.get_by_id(rec.get("module_id"))
                if module:
                    enriched_recommendations.append({
                        **rec,
                        "module": module.to_dict()
                    })
            
            # Log the request
            await self.event_repository.log_event(
                "recommendations_retrieved",
                user_id,
                {"count": len(enriched_recommendations)}
            )
            
            return {
                "success": True,
                "recommendations": enriched_recommendations
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
