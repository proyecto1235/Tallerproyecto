from typing import Optional, Dict, Any
from infrastructure.adapters.output.mongo.student_metrics_repository import StudentMetricsRepository


class MetricsService:
    def __init__(self):
        self._repo = StudentMetricsRepository()

    async def track_event(self, student_id: int, event_type: str, event_data: Optional[Dict[str, Any]] = None) -> bool:
        event_data = event_data or {}
        increments = {}

        if event_type == "session_start":
            increments["session_days"] = 1
            increments["total_sessions"] = 1

        elif event_type == "session_activity":
            increments["total_sessions"] = 1

        elif event_type == "exercise_view":
            increments["exercise_attempts"] = 1

        elif event_type == "exercise_submit":
            increments["exercise_attempts"] = 1
            if event_data.get("passed"):
                increments["passed_exercises"] = 1

        elif event_type == "exercise_attempt":
            increments["exercise_attempts"] = 1
            error_rate = event_data.get("error_rate")
            if error_rate is not None:
                await self._repo.set_fields(student_id, {"error_rate": error_rate})

        elif event_type == "forum_post":
            increments["forum_interactions"] = 1

        elif event_type == "forum_view":
            increments["forum_interactions"] = 1

        elif event_type == "content_view":
            increments["content_views"] = 1

        elif event_type == "session_end":
            duration = event_data.get("duration_minutes", 0)
            if duration > 0:
                await self._repo.increment_metrics(student_id, {"total_time_minutes": duration})

        elif event_type == "code_error":
            await self._repo.set_fields(student_id, {"error_rate": event_data.get("error_rate", 0.5)})

        if increments:
            return await self._repo.increment_metrics(student_id, increments)
        return True

    async def get_student_metrics(self, student_id: int) -> Optional[Dict[str, Any]]:
        metrics = await self._repo.get_metrics(student_id)
        return metrics.to_dict() if metrics else None

    async def get_all_students_metrics(self) -> list:
        return [m.to_dict() for m in await self._repo.get_all_metrics()]
