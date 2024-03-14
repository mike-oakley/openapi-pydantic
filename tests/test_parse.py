import sys
if sys.version_info.minor >= 8:
    from typing import Literal
else:
    # Provide python <= 3.7 compatibility
    from typing_extensions import Literal


import pytest

from openapi_pydantic import parse_obj
from openapi_pydantic.v3 import v3_0_3, v3_1_0


@pytest.mark.parametrize("version", ["3.0.3", "3.0.2", "3.0.1", "3.0.0"])
def test_parse_obj_3_0_3(version: Literal["3.0.3", "3.0.2", "3.0.1", "3.0.0"]) -> None:
    result = parse_obj(
        {
            "openapi": version,
            "info": {"title": "foo", "version": "0.1.0"},
            "paths": {"/": {}},
        }
    )

    assert result == v3_0_3.OpenAPI(
        openapi=version,
        info=v3_0_3.Info(title="foo", version="0.1.0"),
        paths={"/": v3_0_3.PathItem()},
    )


def test_parse_obj_3_1_0() -> None:
    result = parse_obj(
        {
            "openapi": "3.1.0",
            "info": {"title": "foo", "version": "0.1.0"},
            "paths": {"/": {}},
        }
    )

    assert result == v3_1_0.OpenAPI(
        openapi="3.1.0",
        info=v3_1_0.Info(title="foo", version="0.1.0"),
        paths={"/": v3_1_0.PathItem()},
    )
