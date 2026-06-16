from pydantic import BaseModel
from typing import Optional, Any


class DashboardResponse(BaseModel):
    success: bool = True
    total_students: int = 0
    total_modules: int = 0
    total_challenges: int = 0
    new_students_30d: int = 0
    avg_student_progress: float = 0.0
