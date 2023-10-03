from typing import Any

import pytest

from scoring_api.api.api import MISSING, Field


def test_not_typed_field():
    with pytest.raises(ValueError):
        Field(
            target_type=tuple(),
            required=True,
            nullable=True
        )


def test_missing_required_field():
    f = Field(target_type=int, required=True, nullable=True)
    with pytest.raises(ValueError):
        f.__set__(None, MISSING)


def test_missing_not_required_field():
    f = Field(target_type=int, required=False, nullable=True)
    f.__set__(None, MISSING)


def test_assign_null_to_not_nullable():
    f = Field(target_type=int, required=True, nullable=False)
    with pytest.raises(ValueError):
        f.__set__(None, None)


def test_assign_null_to_nullable():
    f = Field(target_type=int, required=True, nullable=True)
    f.__set__(None, None)


@pytest.mark.parametrize('field_type,invalid_value', [
    (int, 1.1),
    (str, 1),
    (float, 'float'),
    (dict, 42),
    (list, dict()),
])
def test_assign_invalid_type(field_type: type, invalid_value: Any):
    f = Field(target_type=field_type, required=True)
    with pytest.raises(ValueError):
        f.__set__(None, invalid_value)


@pytest.mark.parametrize('field_type,valid_value', [
    (int, 1),
    (str, 'str'),
    (float, 12.1),
    (dict, {}),
    (list, [1, 2, 3]),
])
def test_assign_valid_type(field_type: type, valid_value: Any):
    f = Field(target_type=field_type, required=True)
    f.__set__(None, valid_value)


@pytest.mark.parametrize('field_types,invalid_value', [
    ((int, str), 1.4),
    ((str, dict), tuple()),
    ((set, dict), []),
    ((list, tuple), True),
    ((int, float), 'Wrong'),
])
def test_assign_invalid_type_to_multi_typed_field(
    field_types: type,
    invalid_value: Any
):
    f = Field(target_type=field_types, required=True)
    with pytest.raises(ValueError):
        f.__set__(None, invalid_value)


@pytest.mark.parametrize('field_types,valid_value', [
    ((int, str), '4'),
    ((str, dict), 'string'),
    ((set, dict), {}),
    ((list, tuple), tuple()),
    ((int, float), 5),
])
def test_assign_valid_type_to_multi_typed_field(
    field_types: type,
    valid_value: Any
):
    f = Field(target_type=field_types, required=True)
    f.__set__(None, valid_value)


@pytest.mark.parametrize('even_int', [2, 4, 100, 500, -90])
def test_valid_assign_to_field_with_validation(even_int: int):
    class EvenInt(Field):
        def __init__(self):
            super().__init__(target_type=int, required=True, nullable=False)

        def validate(self, value: Any) -> None:
            if value % 2:
                raise ValueError('should be even')

    f = EvenInt()
    f.__set__(None, even_int)


@pytest.mark.parametrize('bad_string', [
    'aaa',
    '1aaa',
    ' ',
    '___',
    '',
])
def test_invalid_assign_to_field_with_validation(bad_string: str):
    class CapitalizedString(Field):
        def __init__(self):
            super().__init__(target_type=str, required=True, nullable=False)

        def validate(self, value: Any) -> None:
            if not len(value) or not value[0].isupper():
                raise ValueError('should be non empty capitalized string')

    f = CapitalizedString()
    with pytest.raises(ValueError):
        f.__set__(None, bad_string)
