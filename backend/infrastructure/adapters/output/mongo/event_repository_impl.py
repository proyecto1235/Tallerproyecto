from typing import List, Dict, Any, Optional
from pymongo import MongoClient, errors
from datetime import datetime
from bson import ObjectId
from config.settings import settings
import asyncio

class EventRepository:
    """MongoDB implementation for event/metrics storage - degrades gracefully if MongoDB is unavailable.
    All MongoDB operations run in a thread executor to avoid blocking the event loop."""
    
    _client: Optional[MongoClient] = None
    _db = None
    _available: Optional[bool] = None  # None = not yet checked
    
    @classmethod
    async def _try_connect(cls):
        """Try connecting to MongoDB once, in a thread (non-blocking)"""
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
        """Get MongoDB database instance (returns None if unavailable)"""
        if cls._available is False:
            return None
        if cls._db is None:
            ok = await cls._try_connect()
            if not ok:
                return None
        return cls._db
    
    @classmethod
    def close(cls):
        """Close MongoDB connection"""
        if cls._client:
            cls._client.close()
            cls._db = None
            cls._client = None
        cls._available = None
    
    async def _run(self, fn, *args, **kwargs):
        """Run a synchronous MongoDB operation in a thread executor"""
        db = await self.get_db()
        if db is None:
            return None
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(None, lambda: fn(db, *args, **kwargs))
        except Exception:
            return None
    
    async def log_event(self, event_type: str, user_id: int, data: Dict[str, Any]) -> Optional[str]:
        return await self._run(
            lambda db: str(db.events.insert_one({
                "event_type": event_type, "user_id": user_id,
                "timestamp": datetime.utcnow(), "data": data,
            }).inserted_id)
        )
    
    async def log_exercise_attempt(self, user_id: int, exercise_id: int, passed: bool, score: float) -> Optional[str]:
        return await self._run(
            lambda db: str(db.exercise_attempts.insert_one({
                "event_type": "exercise_attempt", "user_id": user_id,
                "exercise_id": exercise_id, "passed": passed,
                "score": score, "timestamp": datetime.utcnow(),
            }).inserted_id)
        )
    
    async def get_user_events(self, user_id: int, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        return await self._run(
            lambda db: [
                {**e, "_id": str(e["_id"])} for e in
                db.events.find({"user_id": user_id, **( {"event_type": event_type} if event_type else {})})
                .sort("timestamp", -1)
            ] or []
        )
    
    async def get_user_exercise_history(self, user_id: int) -> List[Dict[str, Any]]:
        return await self._run(
            lambda db: [
                {**a, "_id": str(a["_id"])} for a in
                db.exercise_attempts.find({"user_id": user_id}).sort("timestamp", -1).limit(100)
            ] or []
        )
    
    async def save_progress_snapshot(self, user_id: int, progress_data: Dict[str, Any]) -> Optional[str]:
        return await self._run(
            lambda db: str(db.progress_snapshots.insert_one({
                "user_id": user_id, "timestamp": datetime.utcnow(), **progress_data,
            }).inserted_id)
        )
    
    async def log_chat_interaction(self, user_id: int, message: str, response: str, session_id: str) -> Optional[str]:
        return await self._run(
            lambda db: str(db.chat_interactions.insert_one({
                "user_id": user_id, "session_id": session_id,
                "message": message, "response": response,
                "timestamp": datetime.utcnow(),
            }).inserted_id)
        )
