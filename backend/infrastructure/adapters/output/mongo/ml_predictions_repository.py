from typing import Optional, List
from datetime import datetime, timezone
from pymongo import MongoClient
from config.settings import settings
from domain.analytics.ml_predictions import MLPrediction
import asyncio


class MLPredictionsRepository:
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

    async def save_predictions(self, prediction: MLPrediction) -> bool:
        db = await self.get_db()
        if db is None:
            return False
        loop = asyncio.get_event_loop()
        try:
            def _save():
                prediction.created_at = datetime.now(timezone.utc)
                db.ml_predictions.update_one(
                    {
                        "student_id": prediction.student_id,
                        "week_number": prediction.week_number,
                    },
                    {"$set": prediction.to_dict()},
                    upsert=True,
                )
                return True
            return await loop.run_in_executor(None, _save)
        except Exception:
            return False

    async def get_latest(self, student_id: int) -> Optional[MLPrediction]:
        db = await self.get_db()
        if db is None:
            return None
        loop = asyncio.get_event_loop()
        try:
            def _get():
                doc = db.ml_predictions.find_one(
                    {"student_id": student_id},
                    sort=[("week_number", -1)],
                )
                return MLPrediction.from_dict(doc) if doc else None
            return await loop.run_in_executor(None, _get)
        except Exception:
            return None

    async def get_history(self, student_id: int, limit: int = 16) -> List[MLPrediction]:
        db = await self.get_db()
        if db is None:
            return []
        loop = asyncio.get_event_loop()
        try:
            def _get():
                docs = list(db.ml_predictions.find(
                    {"student_id": student_id}
                ).sort("week_number", -1).limit(limit))
                return [MLPrediction.from_dict(d) for d in docs]
            return await loop.run_in_executor(None, _get)
        except Exception:
            return []

    async def get_all_latest(self) -> List[MLPrediction]:
        db = await self.get_db()
        if db is None:
            return []
        loop = asyncio.get_event_loop()
        try:
            def _get():
                pipeline = [
                    {"$sort": {"week_number": -1}},
                    {"$group": {
                        "_id": "$student_id",
                        "doc": {"$first": "$$ROOT"},
                    }},
                    {"$replaceWith": "$doc"},
                ]
                docs = list(db.ml_predictions.aggregate(pipeline))
                return [MLPrediction.from_dict(d) for d in docs]
            return await loop.run_in_executor(None, _get)
        except Exception:
            return []
