from domain.ports.user_repository import UserRepository
from domain.ports.module_repository import ModuleRepository
from domain.ports.enrollment_repository import EnrollmentRepository
from domain.entities.enrollment import Enrollment
from infrastructure.adapters.output.mongo.event_repository_impl import EventRepository

class EnrollStudentUseCase:
    """Use case for enrolling a student in a module"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        module_repository: ModuleRepository,
        event_repository: EventRepository,
        enrollment_repository: EnrollmentRepository
    ):
        self.user_repository = user_repository
        self.module_repository = module_repository
        self.event_repository = event_repository
        self.enrollment_repository = enrollment_repository
    
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
            
            # Check for duplicated enrollment
            existing_enrollment = await self.enrollment_repository.get_by_student_and_module(student_id, module_id)
            if existing_enrollment:
                return {"success": False, "error": "Ya estás matriculado en este módulo"}
            
            # Create enrollment
            new_enrollment = Enrollment(
                id=None,
                student_id=student_id,
                module_id=module_id,
                status="active",
                enrolled_at=None,
                completed_at=None
            )
            created_enrollment = await self.enrollment_repository.create(new_enrollment)

            # Log enrollment (non-critical)
            try:
                await self.event_repository.log_event(
                    "enrollment_created",
                    student_id,
                    {
                        "module_id": module_id,
                        "module_title": module.title,
                        "status": "active"
                    }
                )
            except Exception as mongo_err:
                print(f"DEBUG: MongoDB log failed (non-critical): {mongo_err}")
            
            return {
                "success": True,
                "enrollment": created_enrollment.to_dict()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
