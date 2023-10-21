import pytest

from scoring_api.api.api import Field, Schema


def test_schema_wo_fields():
    class TestSchema(Schema):
        pass

    with pytest.raises(ValueError):
        TestSchema()


def test_schema_with_valid_field():
    class TestSchema(Schema):
        x = Field(target_type=int, required=True, nullable=True)

    TestSchema(x=1)


def test_schema_with_valid_fields():
    class TestSchema(Schema):
        x = Field(target_type=int, required=True, nullable=True)
        y = Field(target_type=float, required=True, nullable=True)
        z = Field(target_type=str, required=True, nullable=True)

    TestSchema(x=1, y=2., z='z')


def test_schema_with_missing_fields():
    class TestSchema(Schema):
        x = Field(target_type=int, required=True, nullable=True)

    with pytest.raises(ValueError):
        TestSchema(y=1, z=2)


def test_schema_with_not_required_fields():
    class TestSchema(Schema):
        x = Field(target_type=int, required=False, nullable=True)
        y = Field(target_type=int, required=False, nullable=True)
        z = Field(target_type=int, required=False, nullable=True)

    TestSchema()


def test_schema_with_extra_kwargs():
    class TestSchema(Schema):
        x = Field(target_type=int, required=True, nullable=True)

    TestSchema(x=1, y=1, z=2)


def test_schema_with_not_nullable_fields():
    class TestSchema(Schema):
        x = Field(target_type=int, required=True, nullable=False)
        y = Field(target_type=int, required=True, nullable=False)

    with pytest.raises(ValueError):
        TestSchema(x=None, y=None)


def test_schema_with_nullable_fields():
    class TestSchema(Schema):
        x = Field(target_type=int, required=True, nullable=True)
        y = Field(target_type=int, required=True, nullable=True)

    TestSchema(x=None, y=None)


def test_schema_with_invalid_types():
    class TestSchema(Schema):
        x = Field(target_type=int, required=True, nullable=False)
        y = Field(target_type=int, required=True, nullable=False)

    with pytest.raises(ValueError):
        TestSchema(x='x', y=[])


def test_invalid_schema_with_validation():
    class TestSchema(Schema):
        x = Field(target_type=int, required=True, nullable=False)
        y = Field(target_type=int, required=True, nullable=False)

        def validate(self) -> None:
            if self.x == self.y:
                raise ValueError('x and y should not be duplicates')

    with pytest.raises(ValueError):
        TestSchema(x=1, y=1)


def test_valid_schema_with_validation():
    class TestSchema(Schema):
        x = Field(target_type=int, required=True, nullable=False)
        y = Field(target_type=int, required=True, nullable=False)

        def validate(self) -> None:
            if self.x > self.y:
                raise ValueError('x <= y required')

    TestSchema(x=10, y=20)
