from typing import Any

import redis


class KeyValueStore:
    def get(self, key: str) -> Any:
        raise NotImplementedError

    def set(self, key: str, value: Any) -> None:
        raise NotImplementedError

    def cache_get(self, key: str, timeout_sec: int | float = 5) -> Any:
        raise NotImplementedError

    def cache_set(self, key: str, value: Any, ttl: int | float) -> None:
        raise NotImplementedError

    def flush(self) -> None:
        raise NotImplementedError


class RedisStorage(KeyValueStore):
    def __init__(self, host: str = 'localhost', port: int = 6379):
        self._redis = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )

    def get(self, key) -> Any:
        return self._redis.get(key)

    def set(self, key: str, value: Any) -> None:
        self._redis.set(key, value)

    def cache_get(self, key, timeout_sec: int | float = 5) -> Any:
        return self._redis.get(key)

    def cache_set(self, key, value: Any, ttl: int | float) -> None:
        self._redis.setex(key, ttl, value)

    def flush(self) -> None:
        self._redis.flushdb()


def get_store() -> KeyValueStore:
    return RedisStorage()
