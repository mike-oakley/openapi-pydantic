# mypy: ignore-errors

import sys
from typing import Any, Optional

import pytest
from openapi_spec_validator import validate
from pydantic import BaseModel

from openapi_pydantic import (
    DataType,
    Header,
    Info,
    MediaType,
    OpenAPI,
    Operation,
    PathItem,
    RequestBody,
    Response,
    Schema,
)
from openapi_pydantic.compat import PYDANTIC_V2
from openapi_pydantic.util import PydanticSchema, construct_open_api_with_schema_class

if sys.version_info < (3, 9):
    from typing_extensions import Annotated, Literal
else:
    from typing import Annotated, Literal


def test_basic_schema() -> None:
    class SampleModel(BaseModel):
        required: bool
        optional: Optional[bool] = None
        one_literal_choice: Literal["only_choice"]
        multiple_literal_choices: Literal["choice1", "choice2"]

    part_api = construct_sample_api(SampleModel)

    api = construct_open_api_with_schema_class(part_api)
    assert api.components is not None
    assert api.components.schemas is not None

    if PYDANTIC_V2:
        json_api: Any = api.model_dump(mode="json", by_alias=True, exclude_none=True)
    else:
        json_api: Any = api.dict(by_alias=True, exclude_none=True)
    validate(json_api)


@pytest.mark.skipif(
    not PYDANTIC_V2,
    reason="Field-level JSON examples not supported in Pydantic V1",
)
def test_field_json_schema_example() -> None:
    from pydantic import WithJsonSchema

    Thing = Annotated[str, WithJsonSchema({"examples": ["thing1"]})]

    class SampleModel(BaseModel):
        a: Thing

    part_api = construct_sample_api(SampleModel)

    api = construct_open_api_with_schema_class(part_api)
    assert api.components is not None
    assert api.components.schemas is not None

    json_api: Any = api.model_dump(mode="json", by_alias=True, exclude_none=True)
    props = json_api["components"]["schemas"]["SampleRequest"]["properties"]
    assert props["a"]["examples"] == ["thing1"]

    validate(json_api)


def construct_sample_api(SampleModel) -> OpenAPI:
    class SampleRequest(SampleModel):
        model_config = {"json_schema_mode": "validation"}

    class SampleResponse(SampleModel):
        model_config = {"json_schema_mode": "serialization"}

    return OpenAPI(
        info=Info(
            title="Sample API",
            version="v0.0.1",
        ),
        paths={
            "/callme": PathItem(
                post=Operation(
                    requestBody=RequestBody(
                        content={
                            "application/json": MediaType(
                                schema=PydanticSchema(schema_class=SampleRequest)
                            )
                        }
                    ),
                    responses={
                        "200": Response(
                            description="resp",
                            headers={
                                "WWW-Authenticate": Header(
                                    description="Indicate how to authenticate",
                                    schema=Schema(type=DataType.STRING),
                                )
                            },
                            content={
                                "application/json": MediaType(
                                    schema=PydanticSchema(schema_class=SampleResponse)
                                )
                            },
                        )
                    },
                )
            )
        },
    )
