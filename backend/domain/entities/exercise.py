from typing import Optional, Dict, Any
from datetime import datetime

class Exercise:
    def __init__(
        self,
        id: Optional[int],
        module_id: int,
        title: str,
        description: str,
        instructions: str,
        theory_content: Optional[str] = None,
        difficulty: int = 1,
        points: int = 100,
        order: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.module_id = module_id
        self.title = title
        self.description = description
        self.instructions = instructions
        self.theory_content = theory_content
        self.difficulty = difficulty
        self.points = points
        self.order = order
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "module_id": self.module_id,
            "title": self.title,
            "description": self.description,
            "instructions": self.instructions,
            "theory_content": self.theory_content,
            "difficulty": self.difficulty,
            "points": self.points,
            "order": self.order,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
