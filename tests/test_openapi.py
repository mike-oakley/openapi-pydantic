import pytest

from openapi_pydantic.v3 import v3_0_3, v3_1_0


@pytest.mark.parametrize("version", ["3.0.3", "3.1.0"])
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

    if version == "3.0.3":
        assert v3_0_3.OpenAPI.parse_obj(data) == v3_0_3.OpenAPI(
            info=v3_0_3.Info(title="API with Callback", version=""),
            paths={
                "/create": v3_0_3.PathItem(
                    post=v3_0_3.Operation(
                        responses={"200": v3_0_3.Response(description="Success")},
                        callbacks={
                            "event": {
                                "callback": v3_0_3.PathItem(
                                    post=v3_0_3.Operation(
                                        responses={
                                            "200": v3_0_3.Response(
                                                description="Success"
                                            )
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
        assert v3_1_0.OpenAPI.parse_obj(data) == v3_1_0.OpenAPI(
            info=v3_1_0.Info(title="API with Callback", version=""),
            paths={
                "/create": v3_1_0.PathItem(
                    post=v3_1_0.Operation(
                        responses={"200": v3_1_0.Response(description="Success")},
                        callbacks={
                            "event": {
                                "callback": v3_1_0.PathItem(
                                    post=v3_1_0.Operation(
                                        responses={
                                            "200": v3_1_0.Response(
                                                description="Success"
                                            )
                                        }
                                    )
                                )
                            }
                        },
                    )
                )
            },
        )
