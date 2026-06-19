import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from pymongo import MongoClient
from config.settings import settings
from domain.analytics.student_metrics import StudentMetrics
import asyncio

logger = logging.getLogger(__name__)

class StudentMetricsRepository:
    _client: Optional[MongoClient] = None
    _db = None
    _available: Optional[bool] = None
    _warned: bool = False

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
            cls._warned = False
        return cls._available

    @classmethod
    async def get_db(cls):
        if cls._available is False:
            if not cls._warned:
                logger.warning(
                    "[StudentMetricsRepository] MongoDB no disponible. "
                    "Métricas de estudiante no se persisten ni consultan. "
                    "Revisa MONGODB_URL en .env."
                )
                cls._warned = True
            return None
        if cls._db is None:
            ok = await cls._try_connect()
            if not ok:
                if not cls._warned:
                    logger.warning(
                        "[StudentMetricsRepository] MongoDB no disponible. "
                        "Métricas de estudiante no disponibles."
                    )
                    cls._warned = True
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

    async def upsert_metrics(self, student_id: int, updates: Dict[str, Any]) -> bool:
        db = await self.get_db()
        if db is None:
            return False
        loop = asyncio.get_event_loop()
        try:
            def _upsert():
                updates["last_updated"] = datetime.now(timezone.utc)
                db.student_metrics.update_one(
                    {"student_id": student_id},
                    {"$set": updates, "$inc": {}},
                    upsert=True,
                )
                return True
            return await loop.run_in_executor(None, _upsert)
        except Exception:
            return False

    async def increment_metrics(self, student_id: int, increments: Dict[str, Any]) -> bool:
        db = await self.get_db()
        if db is None:
            return False
        loop = asyncio.get_event_loop()
        try:
            def _inc():
                db.student_metrics.update_one(
                    {"student_id": student_id},
                    {
                        "$inc": increments,
                        "$set": {"last_updated": datetime.now(timezone.utc)},
                        "$setOnInsert": {"student_id": student_id},
                    },
                    upsert=True,
                )
                return True
            return await loop.run_in_executor(None, _inc)
        except Exception:
            return False

    async def set_fields(self, student_id: int, fields: Dict[str, Any]) -> bool:
        db = await self.get_db()
        if db is None:
            return False
        loop = asyncio.get_event_loop()
        try:
            def _set():
                fields["last_updated"] = datetime.now(timezone.utc)
                db.student_metrics.update_one(
                    {"student_id": student_id},
                    {"$set": fields},
                    upsert=True,
                )
                return True
            return await loop.run_in_executor(None, _set)
        except Exception:
            return False

    async def get_metrics(self, student_id: int) -> Optional[StudentMetrics]:
        db = await self.get_db()
        if db is None:
            return None
        loop = asyncio.get_event_loop()
        try:
            def _get():
                doc = db.student_metrics.find_one({"student_id": student_id})
                return StudentMetrics.from_dict(doc) if doc else None
            return await loop.run_in_executor(None, _get)
        except Exception:
            return None

    async def get_all_metrics(self) -> List[StudentMetrics]:
        db = await self.get_db()
        if db is None:
            return []
        loop = asyncio.get_event_loop()
        try:
            def _get_all():
                docs = list(db.student_metrics.find())
                return [StudentMetrics.from_dict(d) for d in docs]
            return await loop.run_in_executor(None, _get_all)
        except Exception:
            return []

    async def get_metrics_batch(self, student_ids: List[int]) -> List[StudentMetrics]:
        db = await self.get_db()
        if db is None:
            return []
        loop = asyncio.get_event_loop()
        try:
            def _batch():
                docs = list(db.student_metrics.find({"student_id": {"$in": student_ids}}))
                return [StudentMetrics.from_dict(d) for d in docs]
            return await loop.run_in_executor(None, _batch)
        except Exception:
            return []
