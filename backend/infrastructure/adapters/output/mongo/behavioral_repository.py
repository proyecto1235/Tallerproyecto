from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient, ReturnDocument
from config.settings import settings
import asyncio


class BehavioralRepository:
    _client: Optional[MongoClient] = None
    _db = None
    _available: Optional[bool] = None

    @classmethod
    async def _try_connect(cls):
        if cls._available is not None:
            return cls._available
        loop = asyncio.get_event_loop()
        def _connect():
            try:
                c = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=2000, connectTimeoutMS=2000)
                c.admin.command('ping')
                return c
            except Exception:
                return None
        client = await loop.run_in_executor(None, _connect)
        if client:
            cls._client = client
            cls._db = client[settings.mongodb_db]
            cls._available = True
        else:
            cls._available = False
        return cls._available

    @classmethod
    async def get_db(cls):
        if cls._available is False:
            return None
        if cls._db is None:
            ok = await cls._try_connect()
            if not ok:
                return None
        return cls._db

    @classmethod
    def close(cls):
        if cls._client:
            cls._client.close()
            cls._db = None
            cls._client = None
        cls._available = None

    async def _exec(self, fn):
        db = await self.get_db()
        if db is None:
            return None
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(None, fn)
        except Exception:
            return None

    async def log_session_start(self, user_id: int, session_id: str):
        db = await self.get_db()
        if db is None: return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: db.sessions.insert_one({
            "user_id": user_id, "session_id": session_id,
            "started_at": datetime.now(timezone.utc),
            "last_activity": datetime.now(timezone.utc),
            "is_active": True, "events_count": 0,
        }))

    async def log_session_activity(self, user_id: int, session_id: str):
        db = await self.get_db()
        if db is None: return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: db.sessions.update_one(
            {"session_id": session_id, "user_id": user_id},
            {"$set": {"last_activity": datetime.now(timezone.utc)}, "$inc": {"events_count": 1}},
        ))

    async def log_session_end(self, user_id: int, session_id: str):
        db = await self.get_db()
        if db is None: return 0
        loop = asyncio.get_event_loop()
        try:
            session = await loop.run_in_executor(None, lambda: db.sessions.find_one_and_update(
                {"session_id": session_id, "user_id": user_id},
                {"$set": {"is_active": False, "ended_at": datetime.now(timezone.utc)}},
                return_document=ReturnDocument.AFTER,
            ))
            if session:
                delta = (session["ended_at"] - session["started_at"]).total_seconds()
                await loop.run_in_executor(None, lambda: db.session_metrics.insert_one({
                    "user_id": user_id, "session_id": session_id,
                    "duration_seconds": delta,
                    "events_count": session.get("events_count", 0),
                    "date": session["started_at"],
                }))
                return delta
        except Exception:
            pass
        return 0

    async def log_exercise_action(self, user_id: int, exercise_id: int, module_id: int,
                                   action: str, metadata: Optional[Dict] = None):
        db = await self.get_db()
        if db is None: return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: db.behavioral_events.insert_one({
            "user_id": user_id, "exercise_id": exercise_id,
            "module_id": module_id, "action": action,
            "metadata": metadata or {}, "timestamp": datetime.now(timezone.utc),
        }))

    async def log_frustration_signal(self, user_id: int, exercise_id: int,
                                      signal_type: str, details: Optional[str] = None):
        db = await self.get_db()
        if db is None: return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: db.frustration_signals.insert_one({
            "user_id": user_id, "exercise_id": exercise_id,
            "signal_type": signal_type, "details": details or "",
            "timestamp": datetime.now(timezone.utc),
        }))

    async def log_code_analysis(self, user_id: int, exercise_id: int, code: str,
                                 error: Optional[str], error_type: Optional[str]):
        db = await self.get_db()
        if db is None: return
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: db.code_analysis.insert_one({
            "user_id": user_id, "exercise_id": exercise_id,
            "code_length": len(code), "has_error": error is not None,
            "error": error or "", "error_type": error_type or "",
            "timestamp": datetime.now(timezone.utc),
        }))

    async def update_engagement_score(self, user_id: int, module_id: Optional[int] = None):
        db = await self.get_db()
        if db is None: return {"engagement_score": 0.5}
        loop = asyncio.get_event_loop()
        try:
            def _calc():
                now = datetime.now(timezone.utc)
                d7 = now - timedelta(days=7)
                events = db.behavioral_events.count_documents({"user_id": user_id, "timestamp": {"$gte": d7}})
                sessions = list(db.session_metrics.find({"user_id": user_id, "date": {"$gte": d7}}).sort("date", -1))
                total_time = sum(s.get("duration_seconds", 0) for s in sessions)
                session_days = len(set(s["date"].strftime("%Y-%m-%d") for s in sessions if s.get("date")))
                fr_count = db.frustration_signals.count_documents({"user_id": user_id, "timestamp": {"$gte": d7}})
                eng = max(0.0, min(1.0,
                    0.3 * min(1.0, events / 50) +
                    0.3 * min(1.0, total_time / 10800) +
                    0.3 * min(1.0, session_days / 7) -
                    min(0.5, fr_count * 0.05)))
                db.engagement_scores.update_one(
                    {"user_id": user_id},
                    {"$set": {"user_id": user_id, "module_id": module_id,
                              "engagement_score": round(eng, 4), "events_count": events,
                              "total_time_minutes": round(total_time / 60, 2),
                              "session_days": session_days, "frustration_count": fr_count,
                              "calculated_at": now}},
                    upsert=True,
                )
                return {"engagement_score": round(eng, 4)}
            return await loop.run_in_executor(None, _calc)
        except Exception:
            return {"engagement_score": 0.5}

    async def get_student_behavioral_profile(self, user_id: int) -> Dict:
        db = await self.get_db()
        if db is None: return {"engagement_score": 0.5}
        loop = asyncio.get_event_loop()
        try:
            def _get():
                now = datetime.now(timezone.utc)
                d30 = now - timedelta(days=30)
                d7 = now - timedelta(days=7)
                events = list(db.behavioral_events.find({"user_id": user_id, "timestamp": {"$gte": d30}}).sort("timestamp", -1))
                sessions = list(db.session_metrics.find({"user_id": user_id, "date": {"$gte": d30}}).sort("date", -1))
                frustration = list(db.frustration_signals.find({"user_id": user_id, "timestamp": {"$gte": d30}}).sort("timestamp", -1))
                code_analysis = list(db.code_analysis.find({"user_id": user_id, "timestamp": {"$gte": d30}}).sort("timestamp", -1))
                engagement = db.engagement_scores.find_one({"user_id": user_id})
                attempts = list(db.exercise_attempts.find({"user_id": user_id, "timestamp": {"$gte": d7}}).sort("timestamp", -1))
                total_attempts = len(attempts)
                passed = sum(1 for a in attempts if a.get("passed"))
                total_time = sum(s.get("duration_seconds", 0) for s in sessions)
                sess_days = len(set(s["date"].strftime("%Y-%m-%d") for s in sessions if s.get("date")))
                err_count = sum(1 for a in code_analysis if a.get("has_error"))
                sig_by_type = {}
                for f in frustration:
                    st = f.get("signal_type", "unknown")
                    sig_by_type[st] = sig_by_type.get(st, 0) + 1
                return {
                    "user_id": user_id, "total_sessions_30d": len(sessions),
                    "session_days_30d": sess_days,
                    "total_time_minutes_30d": round(total_time / 60, 2),
                    "total_events_30d": len(events),
                    "total_exercise_attempts_30d": total_attempts,
                    "passed_exercises_30d": passed,
                    "error_rate": round(err_count / max(1, len(code_analysis)), 4),
                    "frustration_signals_30d": len(frustration),
                    "frustration_by_type": sig_by_type,
                    "engagement_score": engagement.get("engagement_score", 0.5) if engagement else 0.5,
                    "avg_session_minutes": round(total_time / 60 / max(1, len(sessions)), 2),
                }
            return await loop.run_in_executor(None, _get)
        except Exception:
            return {"engagement_score": 0.5}

    async def _count_exercise_attempts_30d(self, user_id: int) -> int:
        db = await self.get_db()
        if db is None: return 0
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(None, lambda: db.exercise_attempts.count_documents({
                "user_id": user_id,
                "timestamp": {"$gte": datetime.now(timezone.utc) - timedelta(days=30)},
            }))
        except Exception:
            return 0
