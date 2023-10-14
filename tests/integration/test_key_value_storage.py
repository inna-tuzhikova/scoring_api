import pytest
import redis

from scoring_api.api import constants


def test_online_score_with_non_existing_key(
    store,
    set_valid_auth,
    get_response
):
    request = {
        'account': 'horns&hoofs',
        'login': 'h&f',
        'method': 'online_score',
        'arguments': {
            'gender': 1,
            'birthday': '01.01.2000',
            'first_name': 'a',
            'last_name': 'b'
        }
    }
    set_valid_auth(request)

    response, code = get_response(request)
    assert code == constants.OK
    assert len(response) > 0
    assert response['score'] == 2


def test_online_score_with_existing_key(set_valid_auth, get_response):
    request = {
        'account': 'horns&hoofs',
        'login': 'h&f',
        'method': 'online_score',
        'arguments': {
            'gender': 1,
            'birthday': '01.01.2000',
            'last_name': 'b'
        }
    }
    set_valid_auth(request)

    response, code = get_response(request)
    assert code == constants.OK
    assert len(response) > 0
    assert response['score'] == 1.5

    response, code = get_response(request)
    assert code == constants.OK
    assert len(response) > 0
    assert response['score'] == 1.5


def test_online_score_with_lost_connection(
    monkeypatch,
    get_response,
    store,
    set_valid_auth
):
    def redis_get_with_connection_error(*args, **kwargs):
        raise redis.exceptions.ConnectionError

    monkeypatch.setattr(redis.Redis, 'get', redis_get_with_connection_error)

    request = {
        'account': 'horns&hoofs',
        'login': 'h&f',
        'method': 'online_score',
        'arguments': {
            'gender': 1,
            'birthday': '01.01.2000',
            'last_name': 'b'
        }
    }
    set_valid_auth(request)

    response, code = get_response(request)
    assert code == constants.OK
    assert len(response) > 0
    assert response['score'] == 1.5


def test_client_interests_with_non_existing_key(set_valid_auth, get_response):
    request = {
        'account': 'horns&hoofs',
        'login': 'h&f',
        'method': 'clients_interests',
        'arguments': {
            'client_ids': [1, 2]
        }
    }
    set_valid_auth(request)

    response, code = get_response(request)
    assert code == constants.OK
    assert len(response) == 2
    assert response[1] == []
    assert response[2] == []

    response, code = get_response(request)
    assert code == constants.OK
    assert len(response) == 2
    assert response[1] == []
    assert response[2] == []


def test_client_interests_with_existing_key(
    set_valid_auth,
    get_response_with_store_preset
):
    request = {
        'account': 'horns&hoofs',
        'login': 'h&f',
        'method': 'clients_interests',
        'arguments': {
            'client_ids': [1, 2]
        }
    }
    set_valid_auth(request)

    response, code = get_response_with_store_preset(request)
    assert code == constants.OK
    assert len(response) == 2
    assert response[1] == ['a', 'b']
    assert response[2] == ['c', 'd']


def test_clients_interests_with_lost_connection(
    monkeypatch,
    set_valid_auth,
    get_response
):
    def redis_get_with_connection_error(*args, **kwargs):
        raise redis.exceptions.ConnectionError

    monkeypatch.setattr(redis.Redis, 'get', redis_get_with_connection_error)

    request = {
        'account': 'horns&hoofs',
        'login': 'h&f',
        'method': 'clients_interests',
        'arguments': {
            'client_ids': [0, 1, 2]
        }
    }
    set_valid_auth(request)

    with pytest.raises(redis.ConnectionError):
        get_response(request)
