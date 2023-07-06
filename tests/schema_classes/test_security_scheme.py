from openapi_pydantic import SecurityScheme
from openapi_pydantic.compat import PYDANTIC_V2


def test_oidc_parsing() -> None:
    security_scheme_1 = SecurityScheme(
        type="openIdConnect", openIdConnectUrl="https://example.com/openIdConnect"
    )
    assert isinstance(security_scheme_1.openIdConnectUrl, str)
    if PYDANTIC_V2:
        assert security_scheme_1.model_dump_json(by_alias=True, exclude_none=True) == (
            '{"type":"openIdConnect","openIdConnectUrl":"https://example.com/openIdConnect"}'
        )
    else:
        assert security_scheme_1.json(by_alias=True, exclude_none=True) == (
            '{"type": "openIdConnect", "openIdConnectUrl": "https://example.com/openIdConnect"}'
        )

    security_scheme_2 = SecurityScheme(
        type="openIdConnect", openIdConnectUrl="/openIdConnect"
    )
    assert isinstance(security_scheme_2.openIdConnectUrl, str)
    if PYDANTIC_V2:
        assert security_scheme_2.model_dump_json(by_alias=True, exclude_none=True) == (
            '{"type":"openIdConnect","openIdConnectUrl":"/openIdConnect"}'
        )
    else:
        assert security_scheme_2.json(by_alias=True, exclude_none=True) == (
            '{"type": "openIdConnect", "openIdConnectUrl": "/openIdConnect"}'
        )

    security_scheme_3 = SecurityScheme(
        type="openIdConnect", openIdConnectUrl="openIdConnect"
    )
    assert isinstance(security_scheme_3.openIdConnectUrl, str)
    if PYDANTIC_V2:
        assert security_scheme_3.model_dump_json(by_alias=True, exclude_none=True) == (
            '{"type":"openIdConnect","openIdConnectUrl":"openIdConnect"}'
        )
    else:
        assert security_scheme_3.json(by_alias=True, exclude_none=True) == (
            '{"type": "openIdConnect", "openIdConnectUrl": "openIdConnect"}'
        )
