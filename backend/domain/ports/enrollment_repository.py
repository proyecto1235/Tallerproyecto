from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.enrollment import Enrollment

class EnrollmentRepository(ABC):
    @abstractmethod
    async def create(self, enrollment: Enrollment) -> Enrollment:
        pass
    
    @abstractmethod
    async def get_by_id(self, enrollment_id: int) -> Optional[Enrollment]:
        pass
    
    @abstractmethod
    async def get_by_student_and_module(self, student_id: int, module_id: int) -> Optional[Enrollment]:
        pass
    
    @abstractmethod
    async def get_by_student(self, student_id: int) -> List[Enrollment]:
        pass
    
    @abstractmethod
    async def get_by_module(self, module_id: int) -> List[Enrollment]:
        pass
        
    @abstractmethod
    async def update(self, enrollment: Enrollment) -> Enrollment:
        pass

    @abstractmethod
    async def delete(self, enrollment_id: int) -> bool:
        pass
