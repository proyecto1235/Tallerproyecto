import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock


_await = lambda c: asyncio.run(c)


# ===================================================================
# AICache
# ===================================================================

class TestAICache:

    def make(self):
        from infrastructure.adapters.output.redis.cache import AICache
        return AICache(redis_url="redis://test:6379/0")

    @pytest.fixture
    def mock_redis(self):
        with patch('infrastructure.adapters.output.redis.cache.aioredis.from_url', new_callable=AsyncMock) as m:
            redis_instance = AsyncMock()
            redis_instance.ping = AsyncMock(return_value=True)
            redis_instance.get = AsyncMock(return_value=None)
            redis_instance.setex = AsyncMock()
            redis_instance.scan = AsyncMock(return_value=(0, []))
            redis_instance.delete = AsyncMock()
            m.return_value = redis_instance
            yield redis_instance

    def test_get_cached_response_found(self, mock_redis):
        mock_redis.get.return_value = "cached_response"
        cache = self.make()
        result = _await(cache.get_cached_response("hello"))
        assert result == "cached_response"

    def test_get_cached_response_not_found(self, mock_redis):
        mock_redis.get.return_value = None
        cache = self.make()
        result = _await(cache.get_cached_response("hello"))
        assert result is None

    def test_get_cached_response_redis_unavailable(self):
        cache = self.make()
        cache._available = False
        result = _await(cache.get_cached_response("hello"))
        assert result is None

    def test_cache_response(self, mock_redis):
        cache = self.make()
        _await(cache.cache_response("hello", "world"))
        mock_redis.setex.assert_called_once()

    def test_cache_response_redis_unavailable(self):
        cache = self.make()
        cache._available = False
        _await(cache.cache_response("hello", "world"))

    def test_get_cached_embedding_found(self, mock_redis):
        import json
        mock_redis.get.return_value = json.dumps([0.1, 0.2, 0.3])
        cache = self.make()
        result = _await(cache.get_cached_embedding("text"))
        assert result == [0.1, 0.2, 0.3]

    def test_get_cached_embedding_not_found(self, mock_redis):
        mock_redis.get.return_value = None
        cache = self.make()
        result = _await(cache.get_cached_embedding("text"))
        assert result is None

    def test_cache_embedding(self, mock_redis):
        cache = self.make()
        _await(cache.cache_embedding("text", [0.1, 0.2]))
        mock_redis.setex.assert_called_once()

    def test_clear_with_keys(self, mock_redis):
        mock_redis.scan.return_value = (0, ["key1", "key2"])
        cache = self.make()
        _await(cache.clear("test:*"))
        mock_redis.delete.assert_called_once_with("key1", "key2")

    def test_clear_no_keys(self, mock_redis):
        mock_redis.scan.return_value = (0, [])
        cache = self.make()
        _await(cache.clear("test:*"))
        mock_redis.delete.assert_not_called()

    def test_clear_redis_unavailable(self):
        cache = self.make()
        cache._available = False
        _await(cache.clear("test:*"))

    def test_close(self, mock_redis):
        cache = self.make()
        cache._redis = mock_redis
        _await(cache.close())
        mock_redis.close.assert_awaited_once()
        assert cache._redis is None

    def test_close_no_redis(self):
        cache = self.make()
        cache._redis = None
        _await(cache.close())

    def test_get_redis_connects_on_first_call(self):
        with patch('infrastructure.adapters.output.redis.cache.aioredis.from_url', new_callable=AsyncMock) as m:
            redis_instance = AsyncMock()
            redis_instance.ping = AsyncMock(return_value=True)
            m.return_value = redis_instance
            cache = self.make()
            r = _await(cache._get_redis())
            assert r is not None
            assert cache._available is True

    def test_get_redis_fails_gracefully(self):
        with patch('infrastructure.adapters.output.redis.cache.aioredis.from_url', new_callable=AsyncMock) as m:
            m.side_effect = Exception("connection refused")
            cache = self.make()
            r = _await(cache._get_redis())
            assert r is None
            assert cache._available is False

    def test_get_redis_returns_none_if_unavailable(self):
        cache = self.make()
        cache._available = False
        r = _await(cache._get_redis())
        assert r is None


# ===================================================================
# RateLimiter
# ===================================================================

class TestRateLimiter:

    def make(self):
        from infrastructure.adapters.output.redis.rate_limiter import RateLimiter
        return RateLimiter(redis_url="redis://test:6379/0")

    @pytest.fixture
    def mock_redis(self):
        with patch('infrastructure.adapters.output.redis.rate_limiter.aioredis.from_url', new_callable=AsyncMock) as m:
            redis_instance = AsyncMock()
            redis_instance.incr = AsyncMock(return_value=1)
            redis_instance.expire = AsyncMock(return_value=True)
            m.return_value = redis_instance
            yield redis_instance

    def test_check_allows_within_limit(self, mock_redis):
        mock_redis.incr.return_value = 1
        limiter = self.make()
        _await(limiter.check("test_key", 10, 60))
        mock_redis.expire.assert_awaited_once()

    def test_check_blocks_exceeding_limit(self, mock_redis):
        from fastapi import HTTPException
        mock_redis.incr.return_value = 11
        limiter = self.make()
        with pytest.raises(HTTPException) as exc:
            _await(limiter.check("test_key", 10, 60))
        assert exc.value.status_code == 429

    def test_check_exactly_at_limit(self, mock_redis):
        mock_redis.incr.return_value = 10
        limiter = self.make()
        _await(limiter.check("test_key", 10, 60))

    def test_check_by_user(self, mock_redis):
        mock_redis.incr.return_value = 1
        limiter = self.make()
        _await(limiter.check_by_user(1, "/api/test", 10, 60))

    def test_check_by_ip_with_client(self, mock_redis):
        from fastapi import Request
        scope = {
            "type": "http",
            "client": ("192.168.1.1", 12345),
            "headers": [],
        }
        request = Request(scope)
        mock_redis.incr.return_value = 1
        limiter = self.make()
        _await(limiter.check_by_ip(request, "/api/test", 10, 60))

    def test_check_by_ip_with_forwarded(self, mock_redis):
        from fastapi import Request
        scope = {
            "type": "http",
            "client": ("192.168.1.1", 12345),
            "headers": [(b"x-forwarded-for", b"10.0.0.1, 192.168.1.1")],
        }
        request = Request(scope)
        mock_redis.incr.return_value = 1
        limiter = self.make()
        _await(limiter.check_by_ip(request, "/api/test", 10, 60))

    def test_check_by_ip_no_client(self, mock_redis):
        from fastapi import Request
        scope = {
            "type": "http",
            "client": None,
            "headers": [],
        }
        request = Request(scope)
        mock_redis.incr.return_value = 1
        limiter = self.make()
        _await(limiter.check_by_ip(request, "/api/test", 10, 60))

    def test_close(self, mock_redis):
        limiter = self.make()
        limiter._redis = mock_redis
        _await(limiter.close())
        mock_redis.close.assert_awaited_once()
        assert limiter._redis is None

    def test_close_no_redis(self):
        limiter = self.make()
        limiter._redis = None
        _await(limiter.close())

    def test_get_redis_creates_on_first_call(self):
        with patch('infrastructure.adapters.output.redis.rate_limiter.aioredis.from_url', new_callable=AsyncMock) as m:
            redis_instance = AsyncMock()
            m.return_value = redis_instance
            limiter = self.make()
            r = _await(limiter._get_redis())
            assert r is redis_instance
            assert limiter._redis is redis_instance
