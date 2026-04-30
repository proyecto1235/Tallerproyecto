from typing import Optional, Dict, Any
from datetime import datetime

class Achievement:
    def __init__(
        self,
        id: Optional[int],
        name: str,
        description: str,
        icon: Optional[str] = None,
        points: int = 0,
        criteria: Optional[Dict[str, Any]] = None,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.points = points
        self.criteria = criteria or {}

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "points": self.points,
            "criteria": self.criteria,
        }

class UserAchievement:
    def __init__(
        self,
        id: Optional[int],
        user_id: int,
        achievement_id: int,
        earned_at: Optional[datetime] = None,
    ):
        self.id = id
        self.user_id = user_id
        self.achievement_id = achievement_id
        self.earned_at = earned_at or datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "achievement_id": self.achievement_id,
            "earned_at": self.earned_at.isoformat(),
        }
