from typing import Any, Union

from pydantic import BaseModel, Field

from .v3_0_3 import OpenAPI as OpenAPIv3_0
from .v3_1_0 import OpenAPI as OpenAPIv3_1


class _OpenAPI(BaseModel):
    __root__: Union[OpenAPIv3_1, OpenAPIv3_0] = Field(discriminator="openapi")


def parse_obj(data: Any) -> Union[OpenAPIv3_1, OpenAPIv3_0]:
    """Parse a raw object into an OpenAPI model with version inference."""
    return _OpenAPI.parse_obj(data).__root__
