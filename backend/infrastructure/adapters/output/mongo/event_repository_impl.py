from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from config.settings import settings

class EventRepository:
    """MongoDB implementation for event/metrics storage"""
    
    _client: Optional[MongoClient] = None
    _db = None
    
    @classmethod
    def get_db(cls):
        """Get MongoDB database instance"""
        if cls._db is None:
            cls._client = MongoClient(settings.mongodb_url, serverSelectionTimeoutMS=3000)
            cls._db = cls._client[settings.mongodb_db]
        return cls._db
    
    @classmethod
    def close(cls):
        """Close MongoDB connection"""
        if cls._client:
            cls._client.close()
            cls._db = None
            cls._client = None
    
    async def log_event(self, event_type: str, user_id: int, data: Dict[str, Any]) -> str:
        """Log an event to MongoDB"""
        db = self.get_db()
        event = {
            "event_type": event_type,
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            "data": data,
        }
        result = db.events.insert_one(event)
        return str(result.inserted_id)
    
    async def log_exercise_attempt(self, user_id: int, exercise_id: int, passed: bool, score: float) -> str:
        """Log exercise attempt"""
        db = self.get_db()
        event = {
            "event_type": "exercise_attempt",
            "user_id": user_id,
            "exercise_id": exercise_id,
            "passed": passed,
            "score": score,
            "timestamp": datetime.utcnow(),
        }
        result = db.exercise_attempts.insert_one(event)
        return str(result.inserted_id)
    
    async def get_user_events(self, user_id: int, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get user events from MongoDB"""
        db = self.get_db()
        query = {"user_id": user_id}
        if event_type:
            query["event_type"] = event_type
        
        events = list(db.events.find(query).sort("timestamp", -1))
        for event in events:
            event["_id"] = str(event["_id"])
        return events
    
    async def get_user_exercise_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user exercise attempt history"""
        db = self.get_db()
        attempts = list(
            db.exercise_attempts.find({"user_id": user_id})
            .sort("timestamp", -1)
            .limit(100)
        )
        for attempt in attempts:
            attempt["_id"] = str(attempt["_id"])
        return attempts
    
    async def save_progress_snapshot(self, user_id: int, progress_data: Dict[str, Any]) -> str:
        """Save progress snapshot"""
        db = self.get_db()
        snapshot = {
            "user_id": user_id,
            "timestamp": datetime.utcnow(),
            **progress_data,
        }
        result = db.progress_snapshots.insert_one(snapshot)
        return str(result.inserted_id)
    
    async def log_chat_interaction(self, user_id: int, message: str, response: str, session_id: str) -> str:
        """Log Dialogflow chat interaction"""
        db = self.get_db()
        interaction = {
            "user_id": user_id,
            "session_id": session_id,
            "message": message,
            "response": response,
            "timestamp": datetime.utcnow(),
        }
        result = db.chat_interactions.insert_one(interaction)
        return str(result.inserted_id)
