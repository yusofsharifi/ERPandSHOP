import time
import threading
from typing import Any, Callable, Optional
from app.core.config import settings

# Try to import aioredis if available
try:
    import aioredis
    _has_aioredis = True
except Exception:
    _has_aioredis = False


class InMemoryCache:
    def __init__(self):
        self.store = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            v = self.store.get(key)
            if not v:
                return None
            value, expiry = v
            if expiry and time.time() > expiry:
                del self.store[key]
                return None
            return value

    def set(self, key: str, value: Any, ttl: int = 60):
        with self.lock:
            expiry = time.time() + ttl if ttl else None
            self.store[key] = (value, expiry)


_cache = InMemoryCache()
_redis = None


async def get_redis():
    global _redis
    if not _has_aioredis:
        return None
    if _redis is None:
        _redis = await aioredis.from_url(settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
    return _redis


async def get_cache_or_compute(key: str, compute_fn: Callable[[], Any], ttl: Optional[int] = None):
    # try redis first
    redis = await get_redis()
    ttl_use = ttl or settings.CACHE_TTL_SECONDS
    if redis:
        val = await redis.get(key)
        if val is not None:
            try:
                import json
                return json.loads(val)
            except Exception:
                return val
        # compute
        result = compute_fn()
        try:
            import json
            await redis.set(key, json.dumps(result), ex=ttl_use)
        except Exception:
            pass
        return result
    # fallback to in-memory
    val = _cache.get(key)
    if val is not None:
        return val
    result = compute_fn()
    _cache.set(key, result, ttl_use)
    return result


# Synchronous invalidate helpers used by background tasks

def invalidate_cache_prefix_sync(prefix: str):
    # try redis sync via redis-py if available
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL or f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}")
        # scan for keys
        cursor = '0'
        keys = []
        for key in r.scan_iter(match=prefix + '*'):
            keys.append(key)
        if keys:
            r.delete(*keys)
        return True
    except Exception:
        # fallback to in-memory
        with _cache.lock:
            to_delete = [k for k in _cache.store.keys() if k.startswith(prefix)]
            for k in to_delete:
                del _cache.store[k]
        return False


async def invalidate_cache_prefix_async(prefix: str):
    redis = await get_redis()
    if redis:
        try:
            cursor = b'0'
            async for key in redis.scan_iter(prefix + '*'):
                await redis.delete(key)
            return True
        except Exception:
            return False
    else:
        # fallback to sync invalidate
        invalidate_cache_prefix_sync(prefix)
        return False
