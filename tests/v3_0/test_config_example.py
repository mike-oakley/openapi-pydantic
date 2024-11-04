from typing import Any

from openapi_pydantic.compat import PYDANTIC_V2
from openapi_pydantic.v3.v3_0 import (
    XML,
    Callback,
    Components,
    Contact,
    Discriminator,
    Encoding,
    Example,
    ExternalDocumentation,
    Header,
    Info,
    License,
    Link,
    MediaType,
    OAuthFlow,
    OAuthFlows,
    OpenAPI,
    Operation,
    Parameter,
    PathItem,
    Paths,
    Reference,
    RequestBody,
    Response,
    Responses,
    Schema,
    SecurityRequirement,
    SecurityScheme,
    Server,
    ServerVariable,
    Tag,
)


def test_config_example() -> None:
    all_types = [
        OpenAPI,
        Info,
        Contact,
        License,
        Server,
        ServerVariable,
        Components,
        Paths,
        PathItem,
        Operation,
        ExternalDocumentation,
        Parameter,
        RequestBody,
        MediaType,
        Encoding,
        Responses,
        Response,
        Callback,
        Example,
        Link,
        Header,
        Tag,
        Reference,
        Schema,
        Discriminator,
        XML,
        SecurityScheme,
        OAuthFlows,
        OAuthFlow,
        SecurityRequirement,
    ]
    for schema_type in all_types:
        _assert_config_examples(schema_type)


def _assert_config_examples(schema_type: Any) -> None:
    if PYDANTIC_V2:
        if not hasattr(schema_type, "model_config"):
            return
        extra = schema_type.model_config.get("json_schema_extra")
        if extra is not None:
            examples = extra["examples"]
            for example_dict in examples:
                obj = schema_type.model_validate(example_dict)
                assert obj.model_fields_set

    else:
        Config = getattr(schema_type, "Config", None)
        schema_extra = getattr(Config, "schema_extra", None)
        if schema_extra is not None:
            examples = schema_extra["examples"]
            for example_dict in examples:
                obj = schema_type(**example_dict)
                assert obj.__fields_set__
