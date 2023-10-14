import hashlib
import json
from datetime import datetime
from typing import Callable, Generator

import pytest

from scoring_api.api import constants
from scoring_api.api.handler import method_handler
from scoring_api.api.store import KeyValueStore, get_store


@pytest.fixture
def context() -> dict:
    return dict()


@pytest.fixture
def headers() -> dict:
    return dict()


@pytest.fixture(scope='function')
def store() -> Generator[KeyValueStore, None, None]:
    key_value_store = get_store()
    yield key_value_store
    key_value_store.flush()


@pytest.fixture(scope='session')
def set_valid_auth() -> Callable[[dict], None]:
    def auth(request: dict) -> None:
        if request.get('login') == constants.ADMIN_LOGIN:
            request['token'] = hashlib.sha512((
                datetime.now().strftime('%Y%m%d%H')
                + constants.ADMIN_SALT
            ).encode('utf-8')).hexdigest()
        else:
            msg = (
                request.get('account', '')
                + request.get('login', '')
                + constants.SALT
            )
            request['token'] = hashlib.sha512(msg.encode('utf-8')).hexdigest()
    return auth


@pytest.fixture(scope='function')
def get_response(
    headers: dict,
    context: dict,
    store: KeyValueStore
) -> Callable[[dict], tuple[dict | str, int]]:
    def response(request: dict) -> tuple[dict | str, int]:
        return method_handler(
            request=dict(
                body=request,
                headers=headers
            ),
            ctx=context,
            store=store
        )
    return response


@pytest.fixture(scope='function')
def store_with_presets() -> Generator[KeyValueStore, None, None]:
    key_value_store = get_store()
    key_value_store.set('i:0', json.dumps(['a']))
    key_value_store.set('i:1', json.dumps(['a', 'b']))
    key_value_store.set('i:2', json.dumps(['c', 'd']))

    key_value_store.set('uid:0', '666')
    key_value_store.set('uid:1', '777')
    yield key_value_store
    key_value_store.flush()


@pytest.fixture(scope='function')
def get_response_with_store_preset(
    headers: dict,
    context: dict,
    store_with_presets: KeyValueStore
) -> Callable[[dict], tuple[dict | str, int]]:
    def response(request: dict) -> tuple[dict | str, int]:
        return method_handler(
            request=dict(
                body=request,
                headers=headers
            ),
            ctx=context,
            store=store_with_presets
        )
    return response
