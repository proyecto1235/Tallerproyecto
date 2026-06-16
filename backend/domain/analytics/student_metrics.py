from typing import Optional
from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class StudentMetrics:
    student_id: int
    session_days: int = 0
    total_sessions: int = 0
    total_time_minutes: float = 0.0
    exercise_attempts: int = 0
    passed_exercises: int = 0
    error_rate: float = 0.0
    forum_interactions: int = 0
    content_views: int = 0
    last_updated: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "session_days": self.session_days,
            "total_sessions": self.total_sessions,
            "total_time_minutes": self.total_time_minutes,
            "exercise_attempts": self.exercise_attempts,
            "passed_exercises": self.passed_exercises,
            "error_rate": round(self.error_rate, 4),
            "forum_interactions": self.forum_interactions,
            "content_views": self.content_views,
            "last_updated": (self.last_updated or datetime.now(timezone.utc)).isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StudentMetrics":
        return cls(
            student_id=data.get("student_id", 0),
            session_days=data.get("session_days", 0),
            total_sessions=data.get("total_sessions", 0),
            total_time_minutes=float(data.get("total_time_minutes", 0)),
            exercise_attempts=data.get("exercise_attempts", 0),
            passed_exercises=data.get("passed_exercises", 0),
            error_rate=float(data.get("error_rate", 0)),
            forum_interactions=data.get("forum_interactions", 0),
            content_views=data.get("content_views", 0),
            last_updated=data.get("last_updated"),
        )
