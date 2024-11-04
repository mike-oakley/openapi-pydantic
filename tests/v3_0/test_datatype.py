import pytest
from pydantic import ValidationError

from openapi_pydantic.v3.v3_0 import Schema


@pytest.mark.parametrize(
    "datatype",
    (
        "string",
        "number",
        "integer",
        "boolean",
        "array",
        "object",
    ),
)
def test_good_types_parse_and_equate(datatype: str) -> None:
    assert Schema(type=datatype).type == datatype


def test_bad_types_raise_validation_errors() -> None:
    with pytest.raises(ValidationError):
        Schema(type="invalid")

    with pytest.raises(ValidationError):
        Schema(anyOf=[{"type": "invalid"}])

    with pytest.raises(ValidationError):
        Schema(
            properties={
                "a": Schema(type="invalid"),
            },
        )
