from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient, ReturnDocument
from config.settings import settings


class BehavioralRepository:
    _client: Optional[MongoClient] = None
    _db = None

    @classmethod
    def get_db(cls):
        if cls._db is None:
            cls._client = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=3000)
            cls._db = cls._client[settings.mongodb_db]
        return cls._db

    @classmethod
    def close(cls):
        if cls._client:
            cls._client.close()
            cls._db = None
            cls._client = None

    async def log_session_start(self, user_id: int, session_id: str):
        db = self.get_db()
        db.sessions.insert_one({
            "user_id": user_id,
            "session_id": session_id,
            "started_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc),
            "is_active": True,
            "events_count": 0,
        })

    async def log_session_activity(self, user_id: int, session_id: str):
        db = self.get_db()
        db.sessions.update_one(
            {"session_id": session_id, "user_id": user_id},
            {"$set": {"last_activity": datetime.now(timezone.utc)}, "$inc": {"events_count": 1}},
        )

    async def log_session_end(self, user_id: int, session_id: str):
        db = self.get_db()
        session = db.sessions.find_one_and_update(
            {"session_id": session_id, "user_id": user_id},
            {"$set": {"is_active": False, "ended_at": datetime.now(timezone.utc)}},
            return_document=ReturnDocument.AFTER,
        )
        if session:
            delta = (session.get("ended_at") - session.get("started_at")).total_seconds()
            db.session_metrics.insert_one({
                "user_id": user_id,
                "session_id": session_id,
                "duration_seconds": delta,
                "events_count": session.get("events_count", 0),
                "date": session.get("started_at"),
            })
            return delta
        return 0

    async def log_exercise_action(
        self, user_id: int, exercise_id: int, module_id: int,
        action: str, metadata: Optional[Dict] = None,
    ):
        db = self.get_db()
        db.behavioral_events.insert_one({
            "user_id": user_id,
            "exercise_id": exercise_id,
            "module_id": module_id,
            "action": action,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc),
        })

    async def log_frustration_signal(
        self, user_id: int, exercise_id: int,
        signal_type: str, details: Optional[str] = None,
    ):
        db = self.get_db()
        db.frustration_signals.insert_one({
            "user_id": user_id,
            "exercise_id": exercise_id,
            "signal_type": signal_type,
            "details": details or "",
            "timestamp": datetime.now(timezone.utc),
        })

    async def log_code_analysis(
        self, user_id: int, exercise_id: int, code: str,
        error: Optional[str], error_type: Optional[str],
    ):
        db = self.get_db()
        db.code_analysis.insert_one({
            "user_id": user_id,
            "exercise_id": exercise_id,
            "code_length": len(code),
            "has_error": error is not None,
            "error": error or "",
            "error_type": error_type or "",
            "timestamp": datetime.now(timezone.utc),
        })

    async def update_engagement_score(self, user_id: int, module_id: Optional[int] = None):
        db = self.get_db()
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)

        events_count = db.behavioral_events.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": seven_days_ago},
        })
        sessions_data = list(db.session_metrics.find(
            {"user_id": user_id, "date": {"$gte": seven_days_ago}},
        ).sort("date", -1))
        total_time = sum(s.get("duration_seconds", 0) for s in sessions_data)
        session_days = len(set(s["date"].strftime("%Y-%m-%d") for s in sessions_data if s.get("date")))

        frustration_count = db.frustration_signals.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": seven_days_ago},
        })

        base_score = min(1.0, events_count / 50)
        time_score = min(1.0, total_time / (3600 * 3))
        consistency_score = min(1.0, session_days / 7)
        frustration_penalty = min(0.5, frustration_count * 0.05)

        engagement = max(0.0, min(1.0, 0.3 * base_score + 0.3 * time_score + 0.3 * consistency_score - frustration_penalty))

        doc = {
            "user_id": user_id,
            "module_id": module_id,
            "engagement_score": round(engagement, 4),
            "events_count": events_count,
            "total_time_minutes": round(total_time / 60, 2),
            "session_days": session_days,
            "frustration_count": frustration_count,
            "calculated_at": now,
        }
        db.engagement_scores.update_one(
            {"user_id": user_id},
            {"$set": doc},
            upsert=True,
        )
        return doc

    async def get_student_behavioral_profile(self, user_id: int) -> Dict:
        db = self.get_db()
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        seven_days_ago = now - timedelta(days=7)

        events_30d = list(db.behavioral_events.find(
            {"user_id": user_id, "timestamp": {"$gte": thirty_days_ago}},
        ).sort("timestamp", -1))

        sessions_30d = list(db.session_metrics.find(
            {"user_id": user_id, "date": {"$gte": thirty_days_ago}},
        ).sort("date", -1))

        frustration_30d = list(db.frustration_signals.find(
            {"user_id": user_id, "timestamp": {"$gte": thirty_days_ago}},
        ).sort("timestamp", -1))

        code_analysis = list(db.code_analysis.find(
            {"user_id": user_id, "timestamp": {"$gte": thirty_days_ago}},
        ).sort("timestamp", -1))

        engagement = db.engagement_scores.find_one({"user_id": user_id})

        exercise_attempts = list(db.exercise_attempts.find(
            {"user_id": user_id, "timestamp": {"$gte": seven_days_ago}},
        ).sort("timestamp", -1))

        total_attempts_30d = len(exercise_attempts) if not thirty_days_ago else (await self._count_exercise_attempts_30d(user_id))
        passed_attempts = sum(1 for a in exercise_attempts if a.get("passed"))

        error_count = sum(1 for a in code_analysis if a.get("has_error"))
        total_code_ops = len(code_analysis) or 1

        signals_by_type = {}
        for f in frustration_30d:
            st = f.get("signal_type", "unknown")
            signals_by_type[st] = signals_by_type.get(st, 0) + 1

        total_time_30d = sum(s.get("duration_seconds", 0) for s in sessions_30d)
        session_days_30d = len(set(
            s["date"].strftime("%Y-%m-%d") for s in sessions_30d if s.get("date")
        ))

        return {
            "user_id": user_id,
            "total_sessions_30d": len(sessions_30d),
            "session_days_30d": session_days_30d,
            "total_time_minutes_30d": round(total_time_30d / 60, 2),
            "total_events_30d": len(events_30d),
            "total_exercise_attempts_30d": total_attempts_30d,
            "passed_exercises_30d": passed_attempts,
            "error_rate": round(error_count / total_code_ops, 4),
            "frustration_signals_30d": len(frustration_30d),
            "frustration_by_type": signals_by_type,
            "engagement_score": engagement.get("engagement_score", 0.5) if engagement else 0.5,
            "avg_session_minutes": round(total_time_30d / 60 / max(1, len(sessions_30d)), 2),
        }

    async def _count_exercise_attempts_30d(self, user_id: int) -> int:
        db = self.get_db()
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        return db.exercise_attempts.count_documents({
            "user_id": user_id,
            "timestamp": {"$gte": thirty_days_ago},
        })
