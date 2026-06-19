import json
import hashlib
import logging
from typing import Optional, Any
import redis.asyncio as aioredis

logger = logging.getLogger(__name__)

class AICache:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None
        self._available: Optional[bool] = None
        self._warned: bool = False

    async def _get_redis(self) -> Optional[aioredis.Redis]:
        if self._available is False:
            if not self._warned:
                logger.warning(
                    "[AICache] Redis no disponible. El caché de respuestas de IA y embeddings "
                    "está desactivado. Las respuestas del tutor se generarán sin caché "
                    "(mayor latencia). Revisa REDIS_URL en .env."
                )
                self._warned = True
            return None
        if self._redis is None:
            try:
                self._redis = await aioredis.from_url(
                    self.redis_url, decode_responses=True,
                    socket_connect_timeout=2, socket_timeout=2,
                )
                await self._redis.ping()
                self._available = True
            except Exception as e:
                logger.warning(f"[AICache] Redis no disponible: {e}")
                self._available = False
                self._redis = None
                return None
        return self._redis

    async def _make_key(self, prefix: str, data: Any) -> str:
        raw = json.dumps(data, sort_keys=True) if not isinstance(data, str) else data
        h = hashlib.sha256(raw.encode()).hexdigest()[:32]
        return f"{prefix}:{h}"

    async def get_cached_response(self, prompt: str, model: str = "default") -> Optional[str]:
        r = await self._get_redis()
        if r is None: return None
        key = await self._make_key("ai_response", f"{model}:{prompt}")
        return await r.get(key)

    async def cache_response(self, prompt: str, response: str, model: str = "default", ttl: int = 3600):
        r = await self._get_redis()
        if r is None: return
        key = await self._make_key("ai_response", f"{model}:{prompt}")
        await r.setex(key, ttl, response)

    async def get_cached_embedding(self, text: str) -> Optional[list[float]]:
        r = await self._get_redis()
        if r is None: return None
        key = await self._make_key("embed", text)
        val = await r.get(key)
        if val:
            return json.loads(val)
        return None

    async def cache_embedding(self, text: str, embedding: list[float], ttl: int = 86400):
        r = await self._get_redis()
        if r is None: return
        key = await self._make_key("embed", text)
        await r.setex(key, ttl, json.dumps(embedding))

    async def clear(self, pattern: str = "ai_response:*"):
        r = await self._get_redis()
        if r is None: return
        cursor = 0
        while True:
            cursor, keys = await r.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await r.delete(*keys)
            if cursor == 0:
                break

    async def get(self, key: str) -> Optional[str]:
        r = await self._get_redis()
        if r is None: return None
        return await r.get(key)

    async def set(self, key: str, value: str, ttl: int = 60):
        r = await self._get_redis()
        if r is None: return
        await r.setex(key, ttl, value)

    async def close(self):
        if self._redis:
            await self._redis.close()
            self._redis = None
