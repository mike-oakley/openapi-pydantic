from openapi_pydantic import (
    Header,
    MediaType,
    Parameter,
    ParameterLocation,
    PathItem,
    Reference,
    Schema,
    SecurityScheme,
)
from openapi_pydantic.compat import PYDANTIC_V2


def test_header_alias() -> None:
    header_1 = Header(param_in="header")
    model_validate = Header.model_validate if PYDANTIC_V2 else Header.parse_obj
    header_2 = model_validate({"param_in": "header"})
    header_3 = model_validate({"in": "header"})
    header_4 = model_validate({"in": ParameterLocation.HEADER})
    assert header_1 == header_2 == header_3 == header_4


def test_media_type_alias() -> None:
    media_type_1 = MediaType(media_type_schema=Schema())
    media_type_2 = MediaType(schema=Schema())
    model_validate = MediaType.model_validate if PYDANTIC_V2 else MediaType.parse_obj
    media_type_3 = model_validate({"media_type_schema": Schema()})
    media_type_4 = model_validate({"schema": Schema()})
    assert media_type_1 == media_type_2 == media_type_3 == media_type_4


def test_parameter_alias() -> None:
    parameter_1 = Parameter(name="test", param_in="path", param_schema=Schema())
    parameter_2 = Parameter(name="test", param_in="path", schema=Schema())
    model_validate = Parameter.model_validate if PYDANTIC_V2 else Parameter.parse_obj
    parameter_3 = model_validate(
        {"name": "test", "param_in": "path", "param_schema": Schema()}
    )
    parameter_4 = model_validate({"name": "test", "in": "path", "schema": Schema()})
    assert parameter_1 == parameter_2 == parameter_3 == parameter_4


def test_path_item_alias() -> None:
    path_item_1 = PathItem(ref="#/dummy")
    model_validate = PathItem.model_validate if PYDANTIC_V2 else PathItem.parse_obj
    path_item_2 = model_validate({"ref": "#/dummy"})
    path_item_3 = model_validate({"$ref": "#/dummy"})
    assert path_item_1 == path_item_2 == path_item_3


def test_reference_alias() -> None:
    reference_1 = Reference(ref="#/dummy")
    model_validate = Reference.model_validate if PYDANTIC_V2 else Reference.parse_obj
    reference_2 = model_validate({"ref": "#/dummy"})
    reference_3 = model_validate({"$ref": "#/dummy"})
    assert reference_1 == reference_2 == reference_3


def test_security_scheme() -> None:
    security_scheme_1 = SecurityScheme(type="apiKey", security_scheme_in="header")
    model_validate = (
        SecurityScheme.model_validate if PYDANTIC_V2 else SecurityScheme.parse_obj
    )
    security_scheme_2 = model_validate(
        {"type": "apiKey", "security_scheme_in": "header"}
    )
    security_scheme_3 = model_validate({"type": "apiKey", "in": "header"})
    assert security_scheme_1 == security_scheme_2 == security_scheme_3


def test_schema() -> None:
    schema_1 = Schema(schema_not=Schema(), schema_format="email")
    model_validate = Schema.model_validate if PYDANTIC_V2 else Schema.parse_obj
    schema_2 = model_validate({"schema_not": Schema(), "schema_format": "email"})
    schema_3 = model_validate({"not": Schema(), "format": "email"})
    assert schema_1 == schema_2 == schema_3
