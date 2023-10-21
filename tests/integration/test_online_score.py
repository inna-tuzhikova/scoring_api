from typing import Callable

import pytest
from fixtures import online_score_invalid_requests, online_score_valid_requests

from scoring_api.api import constants


@pytest.mark.parametrize('arguments', online_score_invalid_requests)
def test_invalid_score_request(
    arguments: dict,
    get_response: Callable,
    set_valid_auth: Callable
):
    request = {
        'account': 'horns&hoofs',
        'login': 'h&f',
        'method': 'online_score',
        'arguments': arguments
    }
    set_valid_auth(request)
    response, code = get_response(request)
    assert code == constants.INVALID_REQUEST
    assert len(response) > 0


@pytest.mark.parametrize('arguments', online_score_valid_requests)
def test_ok_score_request(
    arguments: dict,
    get_response: Callable,
    set_valid_auth: Callable,
    context: dict
):
    request = {
        'account': 'horns&hoofs',
        'login': 'h&f',
        'method': 'online_score',
        'arguments': arguments
    }
    set_valid_auth(request)
    response, code = get_response(request)
    assert code == constants.OK
    score = response.get('score')
    assert isinstance(score, (int, float)) and score >= 0
    assert sorted(context['has']) == sorted(arguments.keys())


def test_ok_score_admin_request(
    get_response: Callable,
    set_valid_auth: Callable
):
    arguments = {'phone': '79175002040', 'email': 'stupnikov@otus.ru'}
    request = {
        'account': 'horns&hoofs',
        'login': 'admin',
        'method': 'online_score',
        'arguments': arguments
    }
    set_valid_auth(request)
    response, code = get_response(request)
    assert code == constants.OK
    score = response.get('score')
    assert score == 42
