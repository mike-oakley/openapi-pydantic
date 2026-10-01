from openapi_pydantic.v3.v3_1.schema import schema_validate


def test_boolean_schema() -> None:
    """Issue #35: boolean JSON schemas should be accepted."""
    schema = schema_validate(
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
