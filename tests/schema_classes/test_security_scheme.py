from openapi_pydantic import SecurityScheme
from openapi_pydantic.compat import PYDANTIC_V2


def test_oidc_parsing() -> None:
    security_scheme_1 = SecurityScheme(
        type="openIdConnect", openIdConnectUrl="https://example.com/openIdConnect"
    )
    assert isinstance(security_scheme_1.openIdConnectUrl, str)
    dump1 = getattr(security_scheme_1, "model_dump_json" if PYDANTIC_V2 else "json")
    if PYDANTIC_V2:
        assert dump1(by_alias=True, exclude_none=True) == (
            '{"type":"openIdConnect","openIdConnectUrl":"https://example.com/openIdConnect"}'
        )
    else:
        assert dump1(by_alias=True, exclude_none=True) == (
            '{"type": "openIdConnect", "openIdConnectUrl": "https://example.com/openIdConnect"}'
        )

    security_scheme_2 = SecurityScheme(
        type="openIdConnect", openIdConnectUrl="/openIdConnect"
    )
    assert isinstance(security_scheme_2.openIdConnectUrl, str)
    dump2 = getattr(security_scheme_2, "model_dump_json" if PYDANTIC_V2 else "json")
    if PYDANTIC_V2:
        assert dump2(by_alias=True, exclude_none=True) == (
            '{"type":"openIdConnect","openIdConnectUrl":"/openIdConnect"}'
        )
    else:
        assert dump2(by_alias=True, exclude_none=True) == (
            '{"type": "openIdConnect", "openIdConnectUrl": "/openIdConnect"}'
        )

    security_scheme_3 = SecurityScheme(
        type="openIdConnect", openIdConnectUrl="openIdConnect"
    )
    assert isinstance(security_scheme_3.openIdConnectUrl, str)
    dump3 = getattr(security_scheme_3, "model_dump_json" if PYDANTIC_V2 else "json")
    if PYDANTIC_V2:
        assert dump3(by_alias=True, exclude_none=True) == (
            '{"type":"openIdConnect","openIdConnectUrl":"openIdConnect"}'
        )
    else:
        assert dump3(by_alias=True, exclude_none=True) == (
            '{"type": "openIdConnect", "openIdConnectUrl": "openIdConnect"}'
        )
