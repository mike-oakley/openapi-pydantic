import pytest

from openapi_pydantic import (
    Info,
    MediaType,
    OpenAPI,
    Operation,
    PathItem,
    RequestBody,
    Response,
    Schema,
)
from openapi_pydantic.compat import PYDANTIC_V2, JsonSchemaMode
from openapi_pydantic.util import PydanticSchema, construct_open_api_with_schema_class


@pytest.mark.skipif(not PYDANTIC_V2, reason="computed fields require Pydantic V2")
def test_optional_and_computed_fields():
    api = construct_sample_api()

    result = construct_open_api_with_schema_class(api)
    assert result.components is not None
    assert result.components.schemas is not None

    req_schema = result.components.schemas["SampleRequest"]
    assert isinstance(req_schema, Schema)
    assert req_schema.properties is not None
    assert req_schema.required is not None

    resp_schema = result.components.schemas["SampleResponse"]
    assert isinstance(resp_schema, Schema)
    assert resp_schema.properties is not None
    assert resp_schema.required is not None

    # When validating:
    # - required fields are still required
    # - optional fields are still optional
    # - computed fields don't exist
    assert "req" in req_schema.properties
    assert "opt" in req_schema.properties
    assert "comp" not in req_schema.properties
    assert set(req_schema.required) == {"req"}

    # When serializing:
    # - required fields are still required
    # - optional fields become required
    # - computed fields are required
    assert "req" in resp_schema.properties
    assert "opt" in resp_schema.properties
    assert "comp" in resp_schema.properties
    assert set(resp_schema.required) == {"req", "comp", "opt"}


def construct_sample_api() -> OpenAPI:
    from pydantic import BaseModel, ConfigDict, computed_field

    class ConfigDictExt(ConfigDict, total=False):
        json_schema_mode: JsonSchemaMode

    class SampleModel(BaseModel):
        req: bool
        opt: bool | None = None

        @computed_field
        @property
        def comp(self) -> bool:
            return True

    class SampleRequest(SampleModel):
        model_config = ConfigDictExt(json_schema_mode="validation")

    class SampleResponse(SampleModel):
        model_config = ConfigDictExt(json_schema_mode="serialization")

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
