import json
import logging
from decimal import Decimal
from typing import Any, Callable, Dict, Type, Union

import pytest
from pydantic import BaseModel, ValidationError

from openapi_pydantic import Reference, schema_validate
from openapi_pydantic.compat import (
    DEFS_KEY,
    PYDANTIC_V2,
    ConfigDict,
    Extra,
    models_json_schema,
    v1_schema,
)
from openapi_pydantic.v3 import v3_0, v3_1


def test_schema() -> None:
    schema = schema_validate(
        {
            "title": "reference list",
            "description": "schema for list of reference type",
            "allOf": [{"$ref": "#/definitions/TestType"}],
        }
    )
    logging.debug(f"schema.allOf={schema.allOf}")
    assert schema.allOf
    assert isinstance(schema.allOf, list)
    assert isinstance(schema.allOf[0], Reference)
    assert schema.allOf[0].ref == "#/definitions/TestType"


def test_additional_properties_is_bool() -> None:
    class TestModel(BaseModel):
        test_field: str

        if PYDANTIC_V2:
            model_config = ConfigDict(
                extra="forbid",
            )

        else:

            class Config:
                extra = Extra.forbid

    if PYDANTIC_V2:
        _key_map, schema_definition = models_json_schema([(TestModel, "validation")])
    else:
        schema_definition = v1_schema([TestModel])

    assert schema_definition == {
        DEFS_KEY: {
            "TestModel": {
                "title": "TestModel",
                "type": "object",
                "properties": {"test_field": {"title": "Test Field", "type": "string"}},
                "required": ["test_field"],
                "additionalProperties": False,
            }
        }
    }

    # allow "additionalProperties" to have boolean value
    result = schema_validate(schema_definition[DEFS_KEY]["TestModel"])
    assert result.additionalProperties is False


@pytest.mark.parametrize("schema_type", (v3_0.Schema, v3_1.Schema))
@pytest.mark.parametrize("field", ("minimum", "maximum", "multipleOf"))
@pytest.mark.parametrize("value", (2**53 + 1, 2**64 + 1, 1.0, 1.5))
def test_numeric_constraints_preserve_type_and_precision(
    schema_type: Type[Union[v3_0.Schema, v3_1.Schema]],
    field: str,
    value: Union[int, float],
) -> None:
    data: Dict[str, Any] = {field: value}
    schema: Union[v3_0.Schema, v3_1.Schema] = schema_type(**data)
    assert getattr(schema, field) == value
    assert type(getattr(schema, field)) is type(value)

    dump: Callable[..., Dict[str, Any]] = getattr(
        schema, "model_dump" if PYDANTIC_V2 else "dict"
    )
    restored_data: Dict[str, Any] = json.loads(json.dumps(dump(exclude_unset=True)))
    restored: Union[v3_0.Schema, v3_1.Schema] = schema_type(**restored_data)
    assert getattr(restored, field) == value
    assert type(getattr(restored, field)) is type(value)


@pytest.mark.parametrize("schema_type", (v3_0.Schema, v3_1.Schema))
@pytest.mark.parametrize("value", (0, -1, 0.0, -1.5, Decimal("0"), Decimal("-0.01")))
def test_multiple_of_rejects_nonpositive_values(
    schema_type: Type[Union[v3_0.Schema, v3_1.Schema]],
    value: Union[int, float, Decimal],
) -> None:
    with pytest.raises(ValidationError):
        schema_type(multipleOf=value)


@pytest.mark.parametrize("schema_type", (v3_0.Schema, v3_1.Schema))
@pytest.mark.parametrize("field", ("minimum", "maximum", "multipleOf"))
@pytest.mark.parametrize("value", (True, False, "1.5"))
def test_numeric_constraints_reject_non_number_values(
    schema_type: Type[Union[v3_0.Schema, v3_1.Schema]],
    field: str,
    value: Union[bool, str],
) -> None:
    data: Dict[str, Any] = {field: value}
    with pytest.raises(ValidationError):
        schema_type(**data)


@pytest.mark.parametrize("field", ("exclusiveMinimum", "exclusiveMaximum"))
@pytest.mark.parametrize("value", (2**53 + 1, 2**64 + 1, 1.0, 1.5))
def test_openapi_3_1_exclusive_bounds_preserve_precision(
    field: str, value: Union[int, float]
) -> None:
    data: Dict[str, Any] = {field: value}
    schema: v3_1.Schema = v3_1.Schema(**data)
    assert getattr(schema, field) == value
    assert type(getattr(schema, field)) is type(value)


@pytest.mark.parametrize("field", ("exclusiveMinimum", "exclusiveMaximum"))
@pytest.mark.parametrize("value", (True, False))
def test_openapi_3_0_exclusive_bounds_remain_boolean(field: str, value: bool) -> None:
    data: Dict[str, Any] = {field: value}
    schema: v3_0.Schema = v3_0.Schema(**data)
    assert getattr(schema, field) is value
