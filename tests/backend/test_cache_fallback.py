import pytest

from fastapi import Request

from app.core import cache


def setup_function():
    # ensure clean in-memory store before each test
    cache._inmem._store.clear()


def test_inmemory_set_get_delete(monkeypatch):
    monkeypatch.setattr(cache, "_redis_available", False)
    cache._inmem._store.clear()

    cache.CacheService.set("test:key", {"a": 1}, expire=2)
    assert cache.CacheService.get("test:key") == {"a": 1}

    cache.CacheService.delete("test:key")
    assert cache.CacheService.get("test:key") is None


def test_redis_failure_fallback(monkeypatch):
    class DummyRedis:
        def get(self, key):
            raise Exception("redis get fail")

        def setex(self, key, expire, value):
            raise Exception("redis set fail")

        def keys(self, pattern):
            raise Exception("redis keys fail")

        def delete(self, *keys):
            raise Exception("redis delete fail")

    # Simulate redis present but failing on operations
    monkeypatch.setattr(cache, "_redis_available", True)
    monkeypatch.setattr(cache, "redis_client", DummyRedis())
    cache._inmem._store.clear()

    cache.CacheService.set("failing:key", {"b": 2}, expire=2)
    assert cache.CacheService.get("failing:key") == {"b": 2}

    cache.CacheService.delete("failing:key")
    assert cache.CacheService.get("failing:key") is None
