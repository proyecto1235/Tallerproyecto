import time
from typing import Optional
import redis.asyncio as aioredis
from fastapi import HTTPException, Request

class RateLimiter:
    def __init__(self, redis_url: str = "redis://redis:6379/0"):
        self.redis_url = redis_url
        self._redis: Optional[aioredis.Redis] = None

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None:
            self._redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def check(self, key: str, max_requests: int, window_seconds: int = 60):
        r = await self._get_redis()
        now = int(time.time())
        window_key = f"ratelimit:{key}:{now // window_seconds}"

        count = await r.incr(window_key)
        if count == 1:
            await r.expire(window_key, window_seconds + 1)

        if count > max_requests:
            raise HTTPException(status_code=429, detail=f"Demasiadas solicitudes. Límite: {max_requests} por {window_seconds}s")

    async def check_by_user(self, user_id: int, endpoint: str, max_requests: int, window_seconds: int = 60):
        await self.check(f"user:{user_id}:{endpoint}", max_requests, window_seconds)

    async def check_by_ip(self, request: Request, endpoint: str, max_requests: int, window_seconds: int = 60):
        ip = request.client.host if request.client else "unknown"
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        await self.check(f"ip:{ip}:{endpoint}", max_requests, window_seconds)

    async def close(self):
        if self._redis:
            await self._redis.close()
            self._redis = None
