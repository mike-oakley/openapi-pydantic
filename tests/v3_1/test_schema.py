import json
from typing import Any, Callable, Dict, List, Type, Union

import pytest
from pydantic import BaseModel, ValidationError

from openapi_pydantic.compat import PYDANTIC_V2
from openapi_pydantic.v3.v3_1 import Header, MediaType, OpenAPI, Parameter, Schema
from openapi_pydantic.v3.v3_1.schema import schema_validate


def test_boolean_schema() -> None:
    """Issue #35: boolean JSON schemas should be accepted."""
    schema: Schema = schema_validate(
        {
            "type": "array",
            "prefixItems": [{"type": "number"}, {"type": "string"}],
            "items": False,
            "minItems": 2,
            "maxItems": 2,
        }
    )
    assert schema.items is False
    assert schema.prefixItems is not None
    assert len(schema.prefixItems) == 2
    assert schema.minItems == 2
    assert schema.maxItems == 2


@pytest.mark.parametrize("boolean_schema", (True, False))
@pytest.mark.parametrize(
    "keyword",
    (
        "allOf",
        "anyOf",
        "oneOf",
        "not",
        "if",
        "then",
        "else",
        "dependentSchemas",
        "prefixItems",
        "items",
        "contains",
        "properties",
        "patternProperties",
        "additionalProperties",
        "propertyNames",
        "unevaluatedItems",
        "unevaluatedProperties",
        "contentSchema",
    ),
)
def test_boolean_schemas_round_trip(keyword: str, boolean_schema: bool) -> None:
    value: Union[bool, Dict[str, bool], List[bool]] = boolean_schema
    if keyword in ("properties", "patternProperties", "dependentSchemas"):
        value = {"value": boolean_schema}
    elif keyword in ("allOf", "anyOf", "oneOf", "prefixItems"):
        value = [boolean_schema]
    data: Dict[str, Any] = {keyword: value}
    schema: Schema = schema_validate(data)
    dump: Callable[..., str] = getattr(
        schema, "model_dump_json" if PYDANTIC_V2 else "json"
    )
    restored_data: Dict[str, Any] = json.loads(dump(by_alias=True, exclude_unset=True))
    assert restored_data == data
    actual: Any = restored_data[keyword]
    if isinstance(actual, dict):
        actual = actual["value"]
    elif isinstance(actual, list):
        actual = actual[0]
    assert actual is boolean_schema


@pytest.mark.parametrize("value", (0, 1, "true", "false"))
@pytest.mark.parametrize("keyword", ("items", "additionalProperties"))
def test_schema_values_reject_boolean_coercion(
    keyword: str, value: Union[int, str]
) -> None:
    data: Dict[str, Any] = {keyword: value}
    with pytest.raises(ValidationError):
        schema_validate(data)


@pytest.mark.parametrize("boolean_schema", (True, False))
@pytest.mark.parametrize(
    ("model_type", "attributes"),
    (
        (MediaType, {}),
        (Header, {}),
        (Parameter, {"name": "value", "in": "query"}),
    ),
)
def test_schema_entry_points_accept_booleans(
    model_type: Type[BaseModel], attributes: Dict[str, Any], boolean_schema: bool
) -> None:
    model: BaseModel = model_type(**{**attributes, "schema": boolean_schema})
    dump: Callable[..., str] = getattr(
        model, "model_dump_json" if PYDANTIC_V2 else "json"
    )
    data: Dict[str, Any] = json.loads(dump(by_alias=True, exclude_unset=True))
    assert data["schema"] is boolean_schema


@pytest.mark.parametrize("boolean_schema", (True, False))
def test_boolean_schemas_round_trip_complete_documents(boolean_schema: bool) -> None:
    header: Dict[str, Any] = {"schema": boolean_schema}
    media_type: Dict[str, Any] = {"schema": boolean_schema}
    parameter: Dict[str, Any] = {
        "name": "value",
        "in": "query",
        "schema": boolean_schema,
    }
    request_body: Dict[str, Any] = {
        "content": {
            "multipart/form-data": {
                **media_type,
                "encoding": {"value": {"headers": {"X-Value": header}}},
            }
        }
    }
    response: Dict[str, Any] = {
        "description": "OK",
        "headers": {"X-Value": header},
        "content": {"application/json": media_type},
    }
    operation: Dict[str, Any] = {
        "parameters": [parameter],
        "requestBody": request_body,
        "responses": {"200": response},
    }
    path_item: Dict[str, Any] = {"post": operation}
    callback: Dict[str, Any] = {"{$request.body#/url}": path_item}
    data: Dict[str, Any] = {
        "openapi": "3.1.2",
        "info": {"title": "Boolean schemas", "version": "1"},
        "paths": {
            "/values": {
                "parameters": [parameter],
                "post": {**operation, "callbacks": {"changed": callback}},
            }
        },
        "webhooks": {"changed": path_item},
        "components": {
            "schemas": {"Value": boolean_schema},
            "parameters": {"Value": parameter},
            "headers": {"Value": header},
            "requestBodies": {"Value": request_body},
            "responses": {"Value": response},
            "callbacks": {"changed": callback},
            "pathItems": {"Value": path_item},
        },
    }
    document: OpenAPI = OpenAPI(**data)
    assert document.components is not None
    assert document.components.schemas is not None
    assert document.components.schemas["Value"] is boolean_schema
    dump: Callable[..., str] = getattr(
        document, "model_dump_json" if PYDANTIC_V2 else "json"
    )
    serialized: str = dump(by_alias=True, exclude_unset=True)
    assert json.loads(serialized) == data
    load: Callable[..., OpenAPI] = getattr(
        OpenAPI, "model_validate_json" if PYDANTIC_V2 else "parse_raw"
    )
    restored: OpenAPI = load(serialized)
    assert restored.components is not None
    assert restored.components.schemas is not None
    assert restored.components.schemas["Value"] is boolean_schema
