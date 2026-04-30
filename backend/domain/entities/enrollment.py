from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Enrollment:
    id: Optional[int]
    student_id: int
    module_id: int
    status: str
    enrolled_at: Optional[datetime]
    completed_at: Optional[datetime]

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "module_id": self.module_id,
            "status": self.status,
            "enrolled_at": self.enrolled_at.isoformat() if self.enrolled_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }
