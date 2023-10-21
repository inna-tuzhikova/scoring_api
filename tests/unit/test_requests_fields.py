from typing import Any

import pytest

from scoring_api.api.api import (
    ArgumentsField,
    BirthDayField,
    CharField,
    ClientIDsField,
    DateField,
    EmailField,
    GenderField,
    PhoneField,
)


@pytest.mark.parametrize('value', ['111', 'dfd', '', '___', 'field'])
def test_valid_char_field(value: str):
    f = CharField(required=True)
    f.__set__(None, value)


@pytest.mark.parametrize('value', [1, [], 1.1, True, {}])
def test_invalid_char_field(value: Any):
    f = CharField(required=True)
    with pytest.raises(ValueError):
        f.__set__(None, value)


@pytest.mark.parametrize('value', [{}, {1: 2}, dict(), dict(a=1, b=2), {1: 1}])
def test_valid_arguments_field(value: Any):
    f = ArgumentsField(required=True)
    f.__set__(None, value)


@pytest.mark.parametrize('value', [[], 7, '1.1', True, tuple()])
def test_invalid_arguments_field(value: Any):
    f = ArgumentsField(required=True)
    with pytest.raises(ValueError):
        f.__set__(None, value)


@pytest.mark.parametrize('value', [
    'user@example.com',
    'hello@world.com',
    'user@example',
])
def test_valid_email_field(value: str):
    f = EmailField(required=True)
    f.__set__(None, value)


@pytest.mark.parametrize('value', [
    'userexample.com',
    '123',
    ''
])
def test_invalid_email_field(value: str):
    f = EmailField(required=True)
    with pytest.raises(ValueError):
        f.__set__(None, value)


@pytest.mark.parametrize('value', [
    '71234567890',
    '75656565656',
    70987654321,
    71111111111,
])
def test_valid_phone_field(value: str | int):
    f = PhoneField(required=True)
    f.__set__(None, value)


@pytest.mark.parametrize('value', [
    '7123456789',
    7987654321,
    '01234567890',
    99876543210,
    6,
    '7aaa',
    'xxx'
])
def test_invalid_phone_field(value: str | int):
    f = PhoneField(required=True)
    with pytest.raises(ValueError):
        f.__set__(None, value)


@pytest.mark.parametrize('value', [
    '12.12.2023',
    '01.01.2020',
    '07.07.1980',
    '17.07.1990',
    '15.05.1990',
])
def test_valid_date_field(value: str):
    f = DateField(required=True)
    f.__set__(None, value)


@pytest.mark.parametrize('value', [
    'XXX',
    'XX.XX.XXXX',
    '12.12.12',
    '40.40.2000',
    '31.02.2022',
])
def test_invalid_date_field(value: str):
    f = DateField(required=True)
    with pytest.raises(ValueError):
        f.__set__(None, value)


@pytest.mark.parametrize('value', [
    '12.12.2023',
    '01.01.2020',
    '07.07.1980',
    '17.07.1990',
    '15.05.1990',
])
def test_valid_birthday_field(value: str):
    f = BirthDayField(required=True)
    f.__set__(None, value)


@pytest.mark.parametrize('value', [
    'XXX',
    'XX.XX.XXXX',
    '40.40.2000',
    '31.02.2022',
    '11.02.1900',
])
def test_invalid_birthday_field(value):
    f = BirthDayField(required=True)
    with pytest.raises(ValueError):
        f.__set__(None, value)


@pytest.mark.parametrize('value', [0, 1, 2])
def test_valid_gender_field(value: int):
    f = GenderField(required=True)
    f.__set__(None, value)


@pytest.mark.parametrize('value', [3, 100, 'male', 'female', 'unknown', 'Q'])
def test_invalid_gender_field(value: Any):
    f = GenderField(required=True)
    with pytest.raises(ValueError):
        f.__set__(None, value)


@pytest.mark.parametrize('value', [
    [1, 2, 3],
    [1],
    [-10]
])
def test_valid_client_ids_field(value: list):
    f = ClientIDsField(required=True)
    f.__set__(None, value)


@pytest.mark.parametrize('value', [
    [],
    [None, None],
    ['client_1', 'client_2'],
    dict(),
    dict(a=1, b=2)
])
def test_invalid_client_ids_field(value: Any):
    f = ClientIDsField(required=True)
    with pytest.raises(ValueError):
        f.__set__(None, value)
