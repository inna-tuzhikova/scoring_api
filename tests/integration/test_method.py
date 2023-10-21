from typing import Callable

import pytest
from fixtures import auth_invalid_requests, method_invalid_requests

from scoring_api.api import constants


def test_empty_request(get_response):
    _, code = get_response({})
    assert code == constants.INVALID_REQUEST


@pytest.mark.parametrize('request_dict', auth_invalid_requests)
def test_bad_auth(request_dict: dict, get_response: Callable):
    _, code = get_response(request_dict)
    assert code == constants.FORBIDDEN


@pytest.mark.parametrize('request_dict', method_invalid_requests)
def test_invalid_method_request(
    request_dict: dict,
    get_response: Callable,
    set_valid_auth: Callable
):
    set_valid_auth(request_dict)
    response, code = get_response(request_dict)
    assert code == constants.INVALID_REQUEST
    assert len(response) > 0
