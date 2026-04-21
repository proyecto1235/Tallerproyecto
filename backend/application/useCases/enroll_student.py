from domain.ports.user_repository import UserRepository
from domain.ports.module_repository import ModuleRepository
from infrastructure.adapters.output.mongo.event_repository_impl import EventRepository

class EnrollStudentUseCase:
    """Use case for enrolling a student in a module"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        module_repository: ModuleRepository,
        event_repository: EventRepository
    ):
        self.user_repository = user_repository
        self.module_repository = module_repository
        self.event_repository = event_repository
    
    async def execute(self, student_id: int, module_id: int) -> dict:
        """Enroll student in module"""
        try:
            # Validate student exists
            student = await self.user_repository.get_by_id(student_id)
            if not student:
                return {"success": False, "error": "Estudiante no encontrado"}
            
            # Validate module exists and is published
            module = await self.module_repository.get_by_id(module_id)
            if not module:
                return {"success": False, "error": "Módulo no encontrado"}
            
            if not module.is_published:
                return {"success": False, "error": "Módulo no está publicado"}
            
            # Log enrollment
            await self.event_repository.log_event(
                "enrollment_created",
                student_id,
                {
                    "module_id": module_id,
                    "module_title": module.title,
                    "status": "active"
                }
            )
            
            return {
                "success": True,
                "enrollment": {
                    "student_id": student_id,
                    "module_id": module_id,
                    "status": "active",
                    "message": f"Inscrito en {module.title}"
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
