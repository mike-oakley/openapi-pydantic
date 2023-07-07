import logging
from typing import Callable

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


class PingRequest(BaseModel):
    """Ping Request"""

    req_foo: str = Field(description="foo value of the request")
    req_bar: str = Field(description="bar value of the request")


class PingResponse(BaseModel):
    """Ping response"""

    resp_foo: str = Field(description="foo value of the response")
    resp_bar: str = Field(description="bar value of the response")


class PongResponse(BaseModel):
    """Pong response"""

    resp_foo: str = Field(alias="pong_foo", description="foo value of the response")
    resp_bar: str = Field(alias="pong_bar", description="bar value of the response")
