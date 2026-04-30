from typing import Dict, Any, List
from domain.ports.teacher_repository import TeacherRepository

class TeacherDashboardUseCase:
    """Use case for fetching teacher dashboard analytics and students"""
    
    def __init__(self, teacher_repository: TeacherRepository):
        self.teacher_repository = teacher_repository
        
    async def get_students(self, teacher_id: int) -> Dict[str, Any]:
        """Get all students for a teacher"""
        try:
            students = await self.teacher_repository.get_teacher_students(teacher_id)
            return {"success": True, "students": students}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_metrics(self, teacher_id: int) -> Dict[str, Any]:
        """Get metrics for a teacher"""
        try:
            metrics = await self.teacher_repository.get_teacher_metrics(teacher_id)
            return {"success": True, "metrics": metrics}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_student_detail(self, teacher_id: int, student_id: int) -> Dict[str, Any]:
        """Get student details for a teacher"""
        try:
            student = await self.teacher_repository.get_student_details(teacher_id, student_id)
            if not student:
                return {"success": False, "error": "Estudiante no encontrado o no pertenece a tus módulos"}
            return {"success": True, "student": student}
        except Exception as e:
            return {"success": False, "error": str(e)}
