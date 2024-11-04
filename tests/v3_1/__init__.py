from openapi_pydantic.v3.v3_1.schema import Schema, schema_validate


def test_empty_schema() -> None:
    schema = schema_validate({})
    assert schema == Schema()
