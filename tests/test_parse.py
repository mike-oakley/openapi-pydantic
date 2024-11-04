from typing import Literal

import pytest

from openapi_pydantic import parse_obj
from openapi_pydantic.v3 import v3_0, v3_1


@pytest.mark.parametrize("version", ["3.0.4", "3.0.3", "3.0.2", "3.0.1", "3.0.0"])
def test_parse_obj_3_0(
    version: Literal["3.0.4", "3.0.3", "3.0.2", "3.0.1", "3.0.0"]
) -> None:
    result = parse_obj(
        {
            "openapi": version,
            "info": {"title": "foo", "version": "0.1.0"},
            "paths": {"/": {}},
        }
    )

    assert result == v3_0.OpenAPI(
        openapi=version,
        info=v3_0.Info(title="foo", version="0.1.0"),
        paths={"/": v3_0.PathItem()},
    )


@pytest.mark.parametrize("version", ["3.1.1", "3.1.0"])
def test_parse_obj_3_1(version: Literal["3.1.1", "3.1.0"]) -> None:
    result = parse_obj(
        {
            "openapi": version,
            "info": {"title": "foo", "version": "0.1.0"},
            "paths": {"/": {}},
        }
    )

    assert result == v3_1.OpenAPI(
        openapi=version,
        info=v3_1.Info(title="foo", version="0.1.0"),
        paths={"/": v3_1.PathItem()},
    )
