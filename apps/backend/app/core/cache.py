import os
import json
import functools
import time
import threading
import logging
from typing import Optional, Any
from fastapi import Request

logger = logging.getLogger(__name__)

# Redis connection (optional)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
_redis_available = False
redis_client = None
try:
    import redis  # type: ignore
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        # quick test to ensure connection doesn't raise on import time
        # (we'll handle runtime exceptions in methods)
        _redis_available = True
    except Exception as e:
        logger.warning("Redis not available at import time: %s", e)
        redis_client = None
        _redis_available = False
except Exception:
    logger.info("redis package not installed; using in-memory cache fallback")
    _redis_available = False


class InMemoryCache:
    def __init__(self):
        self._store = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            value, expires_at = entry
            if expires_at and time.time() > expires_at:
                del self._store[key]
                return None
            return value

    def setex(self, key: str, expire: int, value: str):
        with self._lock:
            expires_at = time.time() + expire if expire else None
            self._store[key] = (value, expires_at)

    def keys(self, pattern: str):
        # very simple pattern support: '*' matches prefix/suffix
        with self._lock:
            if pattern == "*":
                return list(self._store.keys())
            # fallback: return keys that contain the pattern fragment
            return [k for k in self._store.keys() if pattern.strip('*') in k]

    def delete(self, *keys):
        with self._lock:
            for k in keys:
                self._store.pop(k, None)


_inmem = InMemoryCache()


class CacheService:
    @staticmethod
    def _get_raw(key: str) -> Optional[str]:
        if _redis_available and redis_client:
            try:
                return redis_client.get(key)
            except Exception as e:
                logger.warning("Redis GET failed: %s", e)
                # fallthrough to in-memory
        return _inmem.get(key)

    @staticmethod
    def _set_raw(key: str, value: str, expire: int = 300):
        if _redis_available and redis_client:
            try:
                redis_client.setex(key, expire, value)
                return
            except Exception as e:
                logger.warning("Redis SET failed: %s", e)
        _inmem.setex(key, expire, value)

    @staticmethod
    def _delete_raw(key_pattern: str):
        if _redis_available and redis_client:
            try:
                keys = redis_client.keys(key_pattern)
                if keys:
                    redis_client.delete(*keys)
                return
            except Exception as e:
                logger.warning("Redis DELETE failed: %s", e)
        keys = _inmem.keys(key_pattern)
        if keys:
            _inmem.delete(*keys)

    @staticmethod
    def get(key: str) -> Optional[Any]:
        try:
            data = CacheService._get_raw(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.warning("Cache get error: %s", e)
            return None

    @staticmethod
    def set(key: str, value: Any, expire: int = 300):
        try:
            CacheService._set_raw(key, json.dumps(value), expire)
        except Exception as e:
            logger.warning("Cache set error: %s", e)

    @staticmethod
    def delete(key_pattern: str):
        try:
            CacheService._delete_raw(key_pattern)
        except Exception as e:
            logger.warning("Cache delete error: %s", e)


def cached(expire: int = 300):
    """
    Decorator to cache FastAPI endpoints.
    Uses request path + query params + Auth header (if present) as key.

    IMPORTANT: The endpoint function SHOULD include `request: Request` as an argument.
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract Request object from kwargs (FastAPI passes it by name usually)
            request = kwargs.get('request')

            # If not in kwargs, check args
            if not request:
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

            # If we found a request, check cache
            if request:
                auth_header = request.headers.get("Authorization", "public")
                cache_key = f"api_cache:{request.url.path}?{request.url.query}:{auth_header}"

                cached_data = CacheService.get(cache_key)

                if cached_data is not None:
                    return cached_data

                response = await func(*args, **kwargs)

                CacheService.set(cache_key, response, expire)
                return response

            # Fallback if no request object found (developer error, but safe fallback)
            logger.warning("@cached used on endpoint without 'request: Request' argument. Caching skipped.")
            return await func(*args, **kwargs)

        return wrapper
    return decorator
