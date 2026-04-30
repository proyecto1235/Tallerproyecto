from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class TeacherRepository(ABC):
    @abstractmethod
    async def get_teacher_students(self, teacher_id: int) -> List[Dict[str, Any]]:
        """Get all students enrolled in the teacher's modules"""
        pass

    @abstractmethod
    async def get_teacher_metrics(self, teacher_id: int) -> Dict[str, Any]:
        """Get analytics/metrics for the teacher's dashboard"""
        pass
        
    @abstractmethod
    async def get_student_details(self, teacher_id: int, student_id: int) -> Optional[Dict[str, Any]]:
        """Get specific student details for a teacher"""
        pass
