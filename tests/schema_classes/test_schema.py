import logging

from pydantic import BaseModel

from openapi_pydantic import Reference, schema_validate
from openapi_pydantic.compat import (
    DEFS_KEY,
    PYDANTIC_V2,
    ConfigDict,
    Extra,
    models_json_schema,
    v1_schema,
)


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
