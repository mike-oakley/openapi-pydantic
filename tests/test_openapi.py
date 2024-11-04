from typing import Callable

import pytest

from openapi_pydantic.compat import PYDANTIC_V2
from openapi_pydantic.v3 import v3_0, v3_1


@pytest.mark.parametrize("version", ["3.0.4", "3.1.1"])
def test_parse_with_callback(version: str) -> None:
    data = {
        "openapi": version,
        "info": {"title": "API with Callback", "version": ""},
        "paths": {
            "/create": {
                "post": {
                    "responses": {"200": {"description": "Success"}},
                    "callbacks": {
                        "event": {
                            "callback": {
                                "post": {
                                    "responses": {"200": {"description": "Success"}}
                                }
                            }
                        }
                    },
                }
            }
        },
    }

    if version == "3.0.4":
        model_validate_3_0: Callable[[dict], v3_0.OpenAPI] = getattr(
            v3_0.OpenAPI, "model_validate" if PYDANTIC_V2 else "parse_obj"
        )
        assert model_validate_3_0(data) == v3_0.OpenAPI(
            info=v3_0.Info(title="API with Callback", version=""),
            paths={
                "/create": v3_0.PathItem(
                    post=v3_0.Operation(
                        responses={"200": v3_0.Response(description="Success")},
                        callbacks={
                            "event": {
                                "callback": v3_0.PathItem(
                                    post=v3_0.Operation(
                                        responses={
                                            "200": v3_0.Response(description="Success")
                                        }
                                    )
                                )
                            }
                        },
                    )
                )
            },
        )
    else:
        model_validate_3_1: Callable[[dict], v3_1.OpenAPI] = getattr(
            v3_1.OpenAPI, "model_validate" if PYDANTIC_V2 else "parse_obj"
        )
        assert model_validate_3_1(data) == v3_1.OpenAPI(
            info=v3_1.Info(title="API with Callback", version=""),
            paths={
                "/create": v3_1.PathItem(
                    post=v3_1.Operation(
                        responses={"200": v3_1.Response(description="Success")},
                        callbacks={
                            "event": {
                                "callback": v3_1.PathItem(
                                    post=v3_1.Operation(
                                        responses={
                                            "200": v3_1.Response(description="Success")
                                        }
                                    )
                                )
                            }
                        },
                    )
                )
            },
        )
