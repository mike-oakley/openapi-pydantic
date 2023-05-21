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
        module = v3_0_3
    else:
        module = v3_1_0

    open_api = module.OpenAPI.parse_obj(data)
    create_endpoint = open_api.paths["/create"]
    assert "200" in create_endpoint.post.responses
    assert "200" in create_endpoint.post.callbacks["event"]["callback"].post.responses
