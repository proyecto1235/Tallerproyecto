from typing import Optional
from datetime import datetime

class Challenge:
    def __init__(
        self,
        id: Optional[int],
        title: str,
        description: str,
        instructions: str,
        teacher_id: int,
        difficulty: int = 1,
        points: int = 100,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.title = title
        self.description = description
        self.instructions = instructions
        self.teacher_id = teacher_id
        self.difficulty = difficulty
        self.points = points
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "instructions": self.instructions,
            "teacher_id": self.teacher_id,
            "difficulty": self.difficulty,
            "points": self.points,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
