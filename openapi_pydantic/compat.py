"""Compatibility layer to make this package usable with Pydantic 1 or 2"""

from pydantic.version import VERSION as PYDANTIC_VERSION

PYDANTIC_MAJOR_VERSION = int(PYDANTIC_VERSION.split(".", 1)[0])

if int(PYDANTIC_MAJOR_VERSION) >= 2:
    PYDANTIC_V2 = True
else:
    PYDANTIC_V2 = False

if PYDANTIC_V2:
    from typing import Literal

    from pydantic import ConfigDict
    from pydantic.json_schema import JsonSchemaMode, models_json_schema  # type: ignore

    # Pydantic 2 renders JSON schemas using the keyword "$defs"
    DEFS_KEY = "$defs"

    # Add V1 stubs to this module, but hide them from typing
    globals().update(
        {
            "Extra": None,
            "v1_schema": None,
        }
    )

else:
    from pydantic import Extra
    from pydantic.schema import schema as v1_schema

    # Pydantic 1 renders JSON schemas using the keyword "definitions"
    DEFS_KEY = "definitions"

    # Add V2 stubs to this module, but hide them from typing
    globals().update(
        {
            "ConfigDict": None,
            "Literal": None,
            "models_json_schema": None,
            "JsonSchemaMode": None,
        }
    )

__all__ = [
    "Literal",
    "ConfigDict",
    "JsonSchemaMode",
    "models_json_schema",
    "Extra",
    "v1_schema",
]
