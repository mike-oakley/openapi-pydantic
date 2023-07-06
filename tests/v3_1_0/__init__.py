from openapi_pydantic.compat import PYDANTIC_V2
from openapi_pydantic.v3.v3_1_0.schema import Schema


def test_empty_schema() -> None:
    model_validate = Schema.model_validate if PYDANTIC_V2 else Schema.parse_obj
    schema = model_validate({})
    assert schema == Schema()
