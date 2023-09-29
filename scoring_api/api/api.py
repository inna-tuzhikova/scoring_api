#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from datetime import date
from typing import Any

from scoring_api.api.constants import ADMIN_LOGIN, GENDERS


class Missing:
    """Helper value to label not found dict entries"""
    pass


MISSING = Missing()


class Field:
    """Descriptor class for describing data field"""

    def __init__(
        self,
        target_type: type | tuple,
        required: bool,
        nullable: bool = False,
    ):
        self._required = required
        self._nullable = nullable
        self._value = None
        if not isinstance(target_type, tuple):
            target_type = target_type,
        else:
            assert len(target_type)
        self._target_types = target_type

    def __get__(self, instance, owner):
        return self._value

    def __set__(self, instance, value):
        if value == MISSING and self._required:
            raise ValueError('required field')
        if value is None and not self._nullable:
            raise ValueError('cannot be null')
        if value == MISSING:
            value = None
        elif value is not None:
            if not any(
                isinstance(value, target_type)
                for target_type in self._target_types
            ):
                raise ValueError(self._build_type_error_msg(value))
            self.validate(value)

        self._value = value

    def validate(self, value: Any) -> None:
        """Extra validation for field

        If the field should be validated in a more complicated way than type
        check add validation code here

        Args:
            value: value to be validated

        Raises:
            ValueError: raised if validation is failed
        """
        pass

    def _build_type_error_msg(self, value: Any) -> str:
        if len(self._target_types) == 1:
            return (
                f'expected {self._target_types[0].__name__}, '
                f'got {value.__class__.__name__} {value}'
            )
        else:
            types = ', '.join(
                target_type.__name__
                for target_type in self._target_types
            )
            return (
                f'expected to be one of types: [{types}], '
                f'got {value.__class__.__name__} {value}'
            )


class Schema:
    """Set of data fields"""

    def __init__(self, **kwargs):
        fields = []
        errors = []
        for key, value in self.__class__.__dict__.items():
            if isinstance(value, Field):
                fields.append((key, value))
        if not len(fields):
            raise ValueError('Set at least one field for schema')
        for key, field in fields:
            value = kwargs.get(key, MISSING)
            try:
                field.__set__(self, value)
            except ValueError as e:
                errors.append(f'Invalid `{key}` field: {e}')
        if errors:
            raise ValueError('\n'.join(errors))
        self.validate()

    def validate(self) -> None:
        """Extra validation for schema

        If the schema should be validated in a more complicated way than each
        field validation add validation code here

        Raises:
            ValueError: raised if validation is failed
        """
        pass


class CharField(Field):
    def __init__(self, required: bool, nullable: bool = False):
        super().__init__(
            required=required,
            nullable=nullable,
            target_type=str
        )


class ArgumentsField(Field):
    def __init__(self, required: bool, nullable: bool = False):
        super().__init__(
            required=required,
            nullable=nullable,
            target_type=dict
        )


class EmailField(CharField):
    def validate(self, value: Any) -> None:
        if '@' not in value:
            raise ValueError('email string should contain `@`')


class PhoneField(Field):
    _PHONE_LENGTH = 11
    _FIRST_DIGIT = '7'

    def __init__(self, required: bool, nullable: bool = False):
        super().__init__(
            required=required,
            nullable=nullable,
            target_type=(int, str)
        )

    def validate(self, value: Any) -> None:
        phone = str(value)
        if len(phone) != self._PHONE_LENGTH:
            raise ValueError('phone should have 11 digits')
        if phone[0] != self._FIRST_DIGIT:
            raise ValueError(f'phone should begin with {self._FIRST_DIGIT}')


class DateField(CharField):
    _DATE_RE = re.compile(r'(?P<day>\d{2})\.(?P<month>\d{2})\.(?P<year>\d{4})')

    def validate(self, value: str) -> None:
        self.string_to_date(value)

    @staticmethod
    def string_to_date(string: str) -> date:
        match = DateField._DATE_RE.match(string)
        if match is None:
            raise ValueError('date should be in fmt DD.MM.YYYY')
        try:
            result = date(
                int(match.group('year')),
                int(match.group('month')),
                int(match.group('day'))
            )
        except ValueError as e:
            raise ValueError(f'invalid date {string}: {e}')
        return result


class BirthDayField(DateField):
    _MAX_AGE_YEARS = 70

    def validate(self, value: Any) -> None:
        birthdate = self.string_to_date(value)
        today = date.today()
        age = today.year - birthdate.year - (
            (today.month, today.day) < (birthdate.month, birthdate.day)
        )
        if age > self._MAX_AGE_YEARS:
            raise ValueError(f'max age is {self._MAX_AGE_YEARS}, got {age}')


class GenderField(Field):
    def __init__(self, required: bool, nullable: bool = False):
        super().__init__(
            required=required,
            nullable=nullable,
            target_type=int
        )

    def validate(self, value: Any) -> None:
        if value not in GENDERS:
            genders = ', '.join(str(g) for g in GENDERS)
            raise ValueError(f'gender should be one of [{genders}]')


class ClientIDsField(Field):
    def __init__(self, required: bool, nullable: bool = False):
        super().__init__(
            required=required,
            nullable=nullable,
            target_type=list
        )

    def validate(self, value: Any) -> None:
        if not len(value):
            raise ValueError('client ids should not be empty')
        if not all(isinstance(item, (int, float)) for item in value):
            raise ValueError(f'all ids should be number, got {value}')


class ClientsInterestsRequest(Schema):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Schema):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate(self) -> None:
        valid = (
            None not in [self.phone, self.email]
            or None not in [self.first_name, self.last_name]
            or None not in [self.gender, self.birthday]
        )
        if not valid:
            raise ValueError(
                'specify at least one full pair: '
                'phone - email, first name - last name, gender - birthday'
            )


class MethodRequest(Schema):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN
