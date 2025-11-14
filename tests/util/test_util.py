import logging
from typing import Callable, Generic, Literal, TypeVar

import pytest
from pydantic import BaseModel, Field

from openapi_pydantic import (
    Info,
    MediaType,
    OpenAPI,
    Operation,
    PathItem,
    Reference,
    RequestBody,
    Response,
    Schema,
)
from openapi_pydantic.compat import PYDANTIC_V2
from openapi_pydantic.util import PydanticSchema, construct_open_api_with_schema_class


def test_construct_open_api_with_schema_class_1() -> None:
    open_api = construct_base_open_api_1()
    result_open_api_1 = construct_open_api_with_schema_class(open_api)
    result_open_api_2 = construct_open_api_with_schema_class(
        open_api, [PingRequest, PingResponse]
    )
    assert result_open_api_1.components == result_open_api_2.components
    assert result_open_api_1 == result_open_api_2

    dump_json = getattr(result_open_api_1, "model_dump_json" if PYDANTIC_V2 else "json")
    open_api_json = dump_json(by_alias=True, exclude_none=True, indent=2)
    logging.debug(open_api_json)


def test_construct_open_api_with_schema_class_2() -> None:
    open_api_1 = construct_base_open_api_1()
    open_api_2 = construct_base_open_api_2()
    result_open_api_1 = construct_open_api_with_schema_class(open_api_1)
    result_open_api_2 = construct_open_api_with_schema_class(
        open_api_2, [PingRequest, PingResponse]
    )
    assert result_open_api_1 == result_open_api_2


def test_construct_open_api_with_schema_class_3() -> None:
    open_api_3 = construct_base_open_api_3()

    result_with_alias_1 = construct_open_api_with_schema_class(open_api_3)
    assert result_with_alias_1.components is not None
    assert result_with_alias_1.components.schemas is not None
    schema_with_alias = result_with_alias_1.components.schemas["PongResponse"]
    assert schema_with_alias.properties is not None
    assert "pong_foo" in schema_with_alias.properties
    assert "pong_bar" in schema_with_alias.properties

    result_with_alias_2 = construct_open_api_with_schema_class(
        open_api_3, by_alias=True
    )
    assert result_with_alias_1 == result_with_alias_2

    result_without_alias = construct_open_api_with_schema_class(
        open_api_3, by_alias=False
    )
    assert result_without_alias.components is not None
    assert result_without_alias.components.schemas is not None
    schema_without_alias = result_without_alias.components.schemas["PongResponse"]
    assert schema_without_alias.properties is not None
    assert "resp_foo" in schema_without_alias.properties
    assert "resp_bar" in schema_without_alias.properties


@pytest.mark.skipif(PYDANTIC_V2, reason="generic type for Pydantic V1")
def test_construct_open_api_with_schema_class_4_generic_response_v1() -> None:
    DataT = TypeVar("DataT")
    from pydantic.v1.generics import GenericModel

    class GenericResponse(GenericModel, Generic[DataT]):
        msg: str = Field(description="message of the generic response")
        data: DataT = Field(description="data value of the generic response")

    open_api_4 = construct_base_open_api_4_generic_response(
        GenericResponse[PongResponse]
    )

    result = construct_open_api_with_schema_class(open_api_4)
    assert result.components is not None
    assert result.components.schemas is not None
    assert "GenericResponse_PongResponse_" in result.components.schemas


@pytest.mark.skipif(not PYDANTIC_V2, reason="generic type for Pydantic V2")
def test_construct_open_api_with_schema_class_4_generic_response_v2() -> None:
    DataT = TypeVar("DataT")

    class GenericResponse(BaseModel, Generic[DataT]):
        msg: str = Field(description="message of the generic response")
        data: DataT = Field(description="data value of the generic response")

    open_api_4 = construct_base_open_api_4_generic_response(
        GenericResponse[PongResponse]
    )

    result = construct_open_api_with_schema_class(open_api_4)
    assert result.components is not None
    assert result.components.schemas is not None
    assert "GenericResponse_PongResponse_" in result.components.schemas


def construct_base_open_api_1() -> OpenAPI:
    model_validate: Callable[[dict], OpenAPI] = getattr(
        OpenAPI, "model_validate" if PYDANTIC_V2 else "parse_obj"
    )
    return model_validate(
        {
            "info": {"title": "My own API", "version": "v0.0.1"},
            "paths": {
                "/ping": {
                    "post": {
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": PydanticSchema(schema_class=PingRequest)
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "pong",
                                "content": {
                                    "application/json": {
                                        "schema": PydanticSchema(
                                            schema_class=PingResponse
                                        )
                                    }
                                },
                            }
                        },
                    }
                }
            },
        }
    )


def construct_base_open_api_2() -> OpenAPI:
    return OpenAPI(
        info=Info(
            title="My own API",
            version="v0.0.1",
        ),
        paths={
            "/ping": PathItem(
                post=Operation(
                    requestBody=RequestBody(
                        content={
                            "application/json": MediaType(
                                media_type_schema=Reference(
                                    **{"$ref": "#/components/schemas/PingRequest"}
                                )
                            )
                        }
                    ),
                    responses={
                        "200": Response(
                            description="pong",
                            content={
                                "application/json": MediaType(
                                    media_type_schema=Reference(
                                        **{"$ref": "#/components/schemas/PingResponse"}
                                    )
                                )
                            },
                        )
                    },
                )
            )
        },
    )


def construct_base_open_api_3() -> OpenAPI:
    return OpenAPI(
        info=Info(
            title="My own API",
            version="v0.0.1",
        ),
        paths={
            "/ping": PathItem(
                post=Operation(
                    requestBody=RequestBody(
                        content={
                            "application/json": MediaType(
                                media_type_schema=PydanticSchema(
                                    schema_class=PingRequest
                                )
                            )
                        }
                    ),
                    responses={
                        "200": Response(
                            description="pong",
                            content={
                                "application/json": MediaType(
                                    media_type_schema=PydanticSchema(
                                        schema_class=PongResponse
                                    )
                                )
                            },
                        )
                    },
                )
            )
        },
    )


def construct_base_open_api_4_generic_response(response_schema: type) -> OpenAPI:
    return OpenAPI(
        info=Info(
            title="My own API",
            version="v0.0.1",
        ),
        paths={
            "/ping": PathItem(
                post=Operation(
                    requestBody=RequestBody(
                        content={
                            "application/json": MediaType(
                                media_type_schema=PydanticSchema(
                                    schema_class=PingRequest
                                )
                            )
                        }
                    ),
                    responses={
                        "200": Response(
                            description="pong",
                            content={
                                "application/json": MediaType(
                                    media_type_schema=PydanticSchema(
                                        schema_class=response_schema
                                    )
                                )
                            },
                        )
                    },
                )
            )
        },
    )


@pytest.mark.parametrize(
    "config_name", ("json_schema_mode", "json_schema_mode_override")
)
@pytest.mark.skipif(not PYDANTIC_V2, reason="computed fields require Pydantic V2")
def test_construct_open_api_with_schema_class_json_schema_mode(
    config_name: Literal["json_schema_mode", "json_schema_mode_override"],
) -> None:
    from typing import Optional

    from pydantic import BaseModel, ConfigDict, computed_field

    class SampleBase(BaseModel):
        req: bool
        opt: Optional[bool] = None

        @computed_field  # type: ignore[prop-decorator]
        @property
        def comp(self) -> bool:
            return True

    class SampleValidation(SampleBase):
        # json_schema_mode is a custom property, so mypy cannot verify its presence
        model_config = ConfigDict(**{config_name: "validation"})  # type: ignore[misc]

    class SampleSerialization(SampleBase):
        model_config = ConfigDict(**{config_name: "serialization"})  # type: ignore[misc]

    api_obj = OpenAPI(
        info=Info(title="Sample API", version="v0.0.1"),
        paths={
            "/mode": PathItem(
                post=Operation(
                    requestBody=RequestBody(
                        content={
                            "application/json": MediaType(
                                schema=PydanticSchema(schema_class=SampleValidation)
                            )
                        }
                    ),
                    responses={
                        "200": Response(
                            description="resp",
                            content={
                                "application/json": MediaType(
                                    schema=PydanticSchema(
                                        schema_class=SampleSerialization
                                    )
                                )
                            },
                        )
                    },
                )
            )
        },
    )

    result = construct_open_api_with_schema_class(api_obj)
    assert result.components is not None
    assert result.components.schemas is not None

    validation_schema = result.components.schemas["SampleValidation"]
    serialization_schema = result.components.schemas["SampleSerialization"]
    assert isinstance(validation_schema, Schema)
    assert isinstance(serialization_schema, Schema)

    assert validation_schema.properties is not None
    assert serialization_schema.properties is not None

    # validation mode: computed field excluded
    assert "comp" not in validation_schema.properties
    assert validation_schema.required is not None
    assert set(validation_schema.required) == {"req"}

    # serialization mode: computed field included and required
    assert "comp" in serialization_schema.properties
    assert serialization_schema.required is not None
    assert set(serialization_schema.required) == {"req", "comp"}


@pytest.mark.skipif(not PYDANTIC_V2, reason="requires Pydantic V2 for union_format")
def test_construct_open_api_with_schema_class_union_format_any_of() -> None:
    from typing import Optional

    class ModelAnyOf(BaseModel):
        maybe: Optional[int] = None

    api_obj = OpenAPI(
        info=Info(title="Union API", version="v0.0.1"),
        paths={
            "/union": PathItem(
                post=Operation(
                    requestBody=RequestBody(
                        content={
                            "application/json": MediaType(
                                schema=PydanticSchema(schema_class=ModelAnyOf)
                            )
                        }
                    ),
                    responses={"200": Response(description="ok")},
                )
            )
        },
    )
    result = construct_open_api_with_schema_class(api_obj, union_format="any_of")
    assert result.components is not None
    assert result.components.schemas is not None
    schema_obj = result.components.schemas["ModelAnyOf"]
    assert isinstance(schema_obj, Schema)
    props = schema_obj.properties
    assert props is not None
    maybe_schema = props["maybe"]
    assert isinstance(maybe_schema, Schema)
    assert maybe_schema.anyOf is not None
    types = {s.type for s in maybe_schema.anyOf if isinstance(s, Schema)}
    assert types == {"integer", "null"}


@pytest.mark.skipif(not PYDANTIC_V2, reason="requires Pydantic V2 for union_format")
def test_construct_open_api_with_schema_class_union_format_primitive_array() -> None:
    from typing import Optional

    class ModelPrimitiveArray(BaseModel):
        maybe: Optional[int] = None

    api_obj = OpenAPI(
        info=Info(title="Union API", version="v0.0.1"),
        paths={
            "/union": PathItem(
                post=Operation(
                    requestBody=RequestBody(
                        content={
                            "application/json": MediaType(
                                schema=PydanticSchema(schema_class=ModelPrimitiveArray)
                            )
                        }
                    ),
                    responses={"200": Response(description="ok")},
                )
            )
        },
    )
    result = construct_open_api_with_schema_class(
        api_obj, union_format="primitive_type_array"
    )
    assert result.components is not None
    assert result.components.schemas is not None
    schema_obj = result.components.schemas["ModelPrimitiveArray"]
    assert isinstance(schema_obj, Schema)
    props = schema_obj.properties
    assert props is not None
    maybe_schema = props["maybe"]
    # primitive_type_array should render type as array of primitive types when possible
    assert isinstance(maybe_schema, Schema)
    assert maybe_schema.anyOf is None
    assert isinstance(maybe_schema.type, list)
    assert set(maybe_schema.type) == {"integer", "null"}


class PingRequest(BaseModel):
    """Ping Request."""

    req_foo: str = Field(description="foo value of the request")
    req_bar: str = Field(description="bar value of the request")


class PingResponse(BaseModel):
    """Ping response."""

    resp_foo: str = Field(description="foo value of the response")
    resp_bar: str = Field(description="bar value of the response")


class PongResponse(BaseModel):
    """Pong response."""

    resp_foo: str = Field(alias="pong_foo", description="foo value of the response")
    resp_bar: str = Field(alias="pong_bar", description="bar value of the response")
