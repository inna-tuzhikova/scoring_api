import logging
from typing import Any

from redis.backoff import ExponentialBackoff
from redis.client import Redis
from redis.exceptions import ConnectionError
from redis.retry import Retry

logger = logging.getLogger(__name__)


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
    def __init__(self, host: str = 'redis', port: int = 6379):
        self._redis = Redis(
            host=host,
            port=port,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry=Retry(ExponentialBackoff(), 3),
            retry_on_error=[ConnectionError]
        )

    def get(self, key) -> Any:
        try:
            return self._redis.get(key)
        except ConnectionError as e:
            logger.exception('Unable to get due to connection error')
            raise e

    def set(self, key: str, value: Any) -> None:
        try:
            self._redis.set(key, value)
        except ConnectionError as e:
            logger.exception('Unable to set key due to connection error')
            raise e

    def cache_get(self, key, timeout_sec: int | float = 5) -> Any:
        try:
            result = self._redis.get(key)
        except ConnectionError:
            logger.exception('Unable to get cache due to connection error')
            result = None
        return result

    def cache_set(self, key, value: Any, ttl: int | float) -> None:
        try:
            self._redis.setex(key, ttl, value)
        except ConnectionError:
            logger.exception('Unable to set cache due to connection error')

    def flush(self) -> None:
        self._redis.flushdb()


def get_store() -> KeyValueStore:
    return RedisStorage()
