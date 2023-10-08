import pytest

from scoring_api.api import constants
from fixtures import auth_invalid_requests, method_invalid_requests


def test_empty_request(get_response):
    _, code = get_response({})
    assert code == constants.INVALID_REQUEST


@pytest.mark.parametrize('request_dict', auth_invalid_requests)
def test_bad_auth(request_dict, get_response):
    _, code = get_response(request_dict)
    assert code == constants.FORBIDDEN


@pytest.mark.parametrize('request_dict', method_invalid_requests)
def test_invalid_method_request(request_dict, get_response, set_valid_auth):
    set_valid_auth(request_dict)
    response, code = get_response(request_dict)
    assert code == constants.INVALID_REQUEST
    assert len(response) > 0
