from typing import Optional
from datetime import datetime

class Progress:
    """Value object representing user progress in a module"""
    
    def __init__(
        self,
        user_id: int,
        module_id: int,
        percentage: float = 0.0,
        completed_exercises: int = 0,
        total_exercises: int = 0,
        points_earned: int = 0,
        last_activity: Optional[datetime] = None,
        is_completed: bool = False,
    ):
        if not 0 <= percentage <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        
        self.user_id = user_id
        self.module_id = module_id
        self.percentage = percentage
        self.completed_exercises = completed_exercises
        self.total_exercises = total_exercises
        self.points_earned = points_earned
        self.last_activity = last_activity or datetime.now()
        self.is_completed = is_completed

    def update_progress(self, completed: int, total: int, points: int):
        """Update progress values"""
        self.completed_exercises = completed
        self.total_exercises = total
        self.points_earned = points
        self.percentage = (completed / total * 100) if total > 0 else 0
        self.last_activity = datetime.now()
        self.is_completed = completed == total

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "module_id": self.module_id,
            "percentage": self.percentage,
            "completed_exercises": self.completed_exercises,
            "total_exercises": self.total_exercises,
            "points_earned": self.points_earned,
            "last_activity": self.last_activity.isoformat(),
            "is_completed": self.is_completed,
        }
