import json
import hashlib
from typing import Optional, Any
import redis.asyncio as aioredis

class AICache:
    def __init__(self, redis_url: str = "redis://redis:6379/0"):
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def _make_key(self, prefix: str, data: Any) -> str:
        raw = json.dumps(data, sort_keys=True) if not isinstance(data, str) else data
        h = hashlib.sha256(raw.encode()).hexdigest()[:32]
        return f"{prefix}:{h}"

    async def get_cached_response(self, prompt: str, model: str = "default") -> Optional[str]:
        r = await self._get_redis()
        key = await self._make_key("ai_response", f"{model}:{prompt}")
        return await r.get(key)

    async def cache_response(self, prompt: str, response: str, model: str = "default", ttl: int = 3600):
        r = await self._get_redis()
        key = await self._make_key("ai_response", f"{model}:{prompt}")
        await r.setex(key, ttl, response)

    async def get_cached_embedding(self, text: str) -> Optional[list[float]]:
        r = await self._get_redis()
        key = await self._make_key("embed", text)
        val = await r.get(key)
        if val:
            return json.loads(val)
        return None

    async def cache_embedding(self, text: str, embedding: list[float], ttl: int = 86400):
        r = await self._get_redis()
        key = await self._make_key("embed", text)
        await r.setex(key, ttl, json.dumps(embedding))

    async def clear(self, pattern: str = "ai_response:*"):
        r = await self._get_redis()
        cursor = 0
        while True:
            cursor, keys = await r.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await r.delete(*keys)
            if cursor == 0:
                break

    async def close(self):
        if self._redis:
            await self._redis.close()
            self._redis = None
