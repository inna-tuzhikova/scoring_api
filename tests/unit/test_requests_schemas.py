import pytest

from scoring_api.api.api import (
    ClientsInterestsRequest,
    MethodRequest,
    OnlineScoreRequest,
)


@pytest.mark.parametrize('request_dict', [
    dict(account='', login='a', token='', arguments={}, method='1'),
    dict(login='b', token='1', arguments={1: 2}, method='2'),
    dict(account='b', login='c', token=None, arguments=None, method='3'),
    dict(account=None, login=None, token=None, arguments={3: 4}, method=''),
    dict(login=None, token='token', arguments=None, method=''),
])
def test_valid_method_request(request_dict):
    MethodRequest(**request_dict)


@pytest.mark.parametrize('request_dict', [
    dict(account='1', token=[], arguments={}),
    dict(account='2', token='', arguments=None, method=78),
    dict(account='3', login='7', arguments='', method=None),
    dict(account=None, login='None', token='', method=''),
    dict(login=67, method=''),
])
def test_invalid_method_request(request_dict):
    with pytest.raises(ValueError):
        MethodRequest(**request_dict)


@pytest.mark.parametrize('request_dict', [
    dict(client_ids=[1, 2, 3], date='12.12.2022'),
    dict(client_ids=[1], date='15.05.2000'),
    dict(client_ids=[2, 3], date=None),
    dict(client_ids=[4, 5]),
])
def test_valid_clients_interests_request(request_dict):
    ClientsInterestsRequest(**request_dict)


@pytest.mark.parametrize('request_dict', [
    dict(client_ids=[], date='XXX'),
    dict(client_ids='[]', date='12.12.12'),
    dict(client_ids=None, date=None),
    dict(date=''),
    dict(client_ids=[1, 2], date=[1, 2]),
])
def test_invalid_clients_interests_request(request_dict):
    with pytest.raises(ValueError):
        ClientsInterestsRequest(**request_dict)


@pytest.mark.parametrize('request_dict', [
    dict(
        first_name='a', last_name='b',
    ),
    dict(
        email='user@example.com', phone=71234567890,
    ),
    dict(
        birthday='12.12.2000', gender=2
    ),
    dict(
        first_name='1', last_name='2',
        email='user@example.com', phone='70987654321',
        birthday='12.12.1990', gender=2
    ),
    dict(
        email='user@example.com', phone='70987654321',
        birthday='12.12.1990', gender=2
    ),

])
def test_valid_online_score_request(request_dict):
    OnlineScoreRequest(**request_dict)


@pytest.mark.parametrize('request_dict', [
    dict(
        first_name='a',
        email='user@example.com',
        birthday='12.12.2005'
    ),
    dict(
        last_name='a',
        phone=71234567890,
        gender=1
    ),
    dict(),
    dict(
        first_name=None, last_name=None,
        email=None, phone=None,
        birthday=None, gender=None
    ),
    dict(
        first_name=12, last_name=[],
    ),
    dict(
        email='user@example.com', phone={}
    ),
    dict(
        birthday='12.12.2000', gender='1'
    ),
])
def test_invalid_online_score_request(request_dict):
    with pytest.raises(ValueError):
        OnlineScoreRequest(**request_dict)
