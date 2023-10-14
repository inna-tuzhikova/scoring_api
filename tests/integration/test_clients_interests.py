import pytest
from fixtures import (
    clients_interests_invalid_requests,
    clients_interests_valid_requests,
)

from scoring_api.api import constants


@pytest.mark.parametrize('arguments', clients_interests_invalid_requests)
def test_invalid_interests_request(
    arguments,
    get_response_with_interests_preset,
    set_valid_auth
):
    request = {
        'account': 'horns&hoofs',
        'login': 'h&f',
        'method': 'clients_interests',
        'arguments': arguments
    }
    set_valid_auth(request)
    response, code = get_response_with_interests_preset(request)
    assert code == constants.INVALID_REQUEST
    assert len(response) > 0


@pytest.mark.parametrize('arguments', clients_interests_valid_requests)
def test_ok_interests_request(
    arguments,
    get_response_with_interests_preset,
    set_valid_auth,
    context
):
    request = {
        'account': 'horns&hoofs',
        'login': 'h&f',
        'method': 'clients_interests',
        'arguments': arguments
    }
    set_valid_auth(request)
    response, code = get_response_with_interests_preset(request)
    assert code == constants.OK, code
    assert len(arguments['client_ids']) == len(response)
    assert all(
        v
        and isinstance(v, list)
        and all(isinstance(i, (bytes, str)) for i in v)
        for v in response.values()
    )
    assert context.get('nclients') == len(arguments['client_ids'])
