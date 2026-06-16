from typing import Optional
from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class WeeklyStudentMetrics:
    student_id: int
    week_number: int
    year: int
    avg_session_days: float = 0.0
    avg_total_sessions: float = 0.0
    avg_total_time_minutes: float = 0.0
    avg_exercise_attempts: float = 0.0
    avg_passed_exercises: float = 0.0
    avg_error_rate: float = 0.0
    avg_forum_interactions: float = 0.0
    avg_content_views: float = 0.0
    engagement_score: float = 0.0
    performance_score: float = 0.0
    frustration_score: float = 0.0
    dropout_risk: float = 0.0
    cluster_id: int = -1
    cluster_name: str = "unknown"
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "week_number": self.week_number,
            "year": self.year,
            "avg_session_days": round(self.avg_session_days, 4),
            "avg_total_sessions": round(self.avg_total_sessions, 4),
            "avg_total_time_minutes": round(self.avg_total_time_minutes, 4),
            "avg_exercise_attempts": round(self.avg_exercise_attempts, 4),
            "avg_passed_exercises": round(self.avg_passed_exercises, 4),
            "avg_error_rate": round(self.avg_error_rate, 4),
            "avg_forum_interactions": round(self.avg_forum_interactions, 4),
            "avg_content_views": round(self.avg_content_views, 4),
            "engagement_score": round(self.engagement_score, 4),
            "performance_score": round(self.performance_score, 4),
            "frustration_score": round(self.frustration_score, 4),
            "dropout_risk": round(self.dropout_risk, 4),
            "cluster_id": self.cluster_id,
            "cluster_name": self.cluster_name,
            "created_at": (self.created_at or datetime.now(timezone.utc)).isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "WeeklyStudentMetrics":
        return cls(
            student_id=data.get("student_id", 0),
            week_number=data.get("week_number", 0),
            year=data.get("year", 0),
            avg_session_days=float(data.get("avg_session_days", 0)),
            avg_total_sessions=float(data.get("avg_total_sessions", 0)),
            avg_total_time_minutes=float(data.get("avg_total_time_minutes", 0)),
            avg_exercise_attempts=float(data.get("avg_exercise_attempts", 0)),
            avg_passed_exercises=float(data.get("avg_passed_exercises", 0)),
            avg_error_rate=float(data.get("avg_error_rate", 0)),
            avg_forum_interactions=float(data.get("avg_forum_interactions", 0)),
            avg_content_views=float(data.get("avg_content_views", 0)),
            engagement_score=float(data.get("engagement_score", 0)),
            performance_score=float(data.get("performance_score", 0)),
            frustration_score=float(data.get("frustration_score", 0)),
            dropout_risk=float(data.get("dropout_risk", 0)),
            cluster_id=data.get("cluster_id", -1),
            cluster_name=data.get("cluster_name", "unknown"),
            created_at=data.get("created_at"),
        )
