import pytest
import redis

from scoring_api.api.store import KeyValueStore


@pytest.mark.parametrize('key,value', [
    ('uid:0', '666'),
    ('uid:1', '777'),
])
def test_cache_get_existing_key(
    key: str,
    value: str,
    store_with_presets: KeyValueStore
):
    result = store_with_presets.cache_get(key)
    assert result == value


@pytest.mark.parametrize('non_existing_key', [
    'non_existing_key_1',
    'non_existing_key_2'
])
def test_cache_get_non_existing_key(
    non_existing_key: str,
    store: KeyValueStore
):
    result = store.cache_get(non_existing_key)
    assert result is None


def test_cache_set_non_existing_key(store: KeyValueStore):
    result = store.cache_get('key')
    assert result is None
    store.cache_set('key', '123', 1)
    result = store.cache_get('key')
    assert result == '123'


def test_cache_set_existing_key(store_with_presets: KeyValueStore):
    result = store_with_presets.cache_get('uid:0')
    assert result == '666'
    store_with_presets.cache_set('uid:0', '6666', 1)
    result = store_with_presets.cache_get('uid:0')
    assert result == '6666'


def test_cache_lost_connection(store_with_presets: KeyValueStore, monkeypatch):
    def redis_get_with_connection_error(*args, **kwargs):
        raise redis.exceptions.ConnectionError

    monkeypatch.setattr(redis.Redis, 'get', redis_get_with_connection_error)

    result = store_with_presets.cache_get('uid:0')
    assert result is None


def test_cache_get_retries_on_connection_lost(
    monkeypatch,
    store_with_presets: KeyValueStore
):
    retries = [3]
    original_send = redis.Connection.send_command

    def send_command(*args, **kwargs):
        if retries[0] > 0:
            retries[0] -= 1
            raise redis.exceptions.ConnectionError(
                'Some error while sending command'
            )
        else:
            return original_send(*args, **kwargs)

    monkeypatch.setattr(redis.Connection, 'send_command', send_command)
    result = store_with_presets.cache_get('uid:0')
    assert result == '666'


@pytest.mark.parametrize('key,value', [
    ('uid:0', '666'),
    ('uid:1', '777'),
])
def test_get_existing_key(
    key: str,
    value: str,
    store_with_presets: KeyValueStore
):
    result = store_with_presets.get(key)
    assert result == value


@pytest.mark.parametrize('non_existing_key', [
    'non_existing_key_1',
    'non_existing_key_2'
])
def test_get_non_existing_key(non_existing_key: str, store: KeyValueStore):
    result = store.get(non_existing_key)
    assert result is None


def test_set_non_existing_key(store: KeyValueStore):
    result = store.get('key')
    assert result is None
    store.set('key', '123')
    result = store.get('key')
    assert result == '123'


def test_set_existing_key(store_with_presets: KeyValueStore):
    result = store_with_presets.get('uid:0')
    assert result == '666'
    store_with_presets.set('uid:0', '6666')
    result = store_with_presets.get('uid:0')
    assert result == '6666'


def test_get_lost_connection(store_with_presets: KeyValueStore, monkeypatch):
    def redis_get_with_connection_error(*args, **kwargs):
        raise redis.exceptions.ConnectionError

    monkeypatch.setattr(redis.Redis, 'get', redis_get_with_connection_error)

    with pytest.raises(redis.exceptions.ConnectionError):
        store_with_presets.get('uid:0')


def test_get_retries_on_connection_lost(
    monkeypatch,
    store_with_presets: KeyValueStore
):
    retries = [3]
    original_send = redis.Connection.send_command

    def send_command(*args, **kwargs):
        if retries[0] > 0:
            retries[0] -= 1
            raise redis.exceptions.ConnectionError(
                'Some error while sending command'
            )
        else:
            return original_send(*args, **kwargs)

    monkeypatch.setattr(redis.Connection, 'send_command', send_command)
    result = store_with_presets.get('uid:0')
    assert result == '666'
