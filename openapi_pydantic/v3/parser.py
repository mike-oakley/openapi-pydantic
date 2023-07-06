from typing import Any, Union

from pydantic import BaseModel, Field

from openapi_pydantic.compat import PYDANTIC_V2

from .v3_0_3 import OpenAPI as OpenAPIv3_0
from .v3_1_0 import OpenAPI as OpenAPIv3_1

OpenAPIv3 = Union[OpenAPIv3_1, OpenAPIv3_0]

if PYDANTIC_V2:
    from pydantic import RootModel

    class _OpenAPIV2(RootModel):
        root: OpenAPIv3 = Field(discriminator="openapi")

else:

    class _OpenAPIV1(BaseModel):
        __root__: OpenAPIv3 = Field(discriminator="openapi")


def parse_obj(data: Any) -> OpenAPIv3:
    """Parse a raw object into an OpenAPI model with version inference."""
    if PYDANTIC_V2:
        return _OpenAPIV2.model_validate(data).root
    else:
        return _OpenAPIV1.parse_obj(data).__root__
