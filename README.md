<p align="center">
  <img src="https://raw.githubusercontent.com/mike-oakley/openapi-pydantic/main/docs/_static/logo.png" alt="openapi-pydantic logo" width="120" height="120">
</p>

<h1 align="center">openapi-pydantic</h1>

<p align="center">
  <a href="https://pypi.org/project/openapi-pydantic/"><img src="https://img.shields.io/pypi/v/openapi-pydantic" alt="PyPI"></a>
  <a href="https://github.com/mike-oakley/openapi-pydantic/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/openapi-pydantic" alt="License"></a>
</p>

<p align="center">
  <b>Modern, type-safe OpenAPI schemas in Python using Pydantic 1.8+ and 2.x</b>
</p>

---

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Examples](#usage-examples)
- [Using Pydantic Classes as Schema](#using-pydantic-classes-as-schema)
- [Notes](#notes)
- [Credits](#credits)
- [License](#license)

---

## ✨ Features

- Supports both Pydantic 1.8+ and 2.x
- Supports the [OpenAPI 3.1 specification](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.1.1.md#schema) (with [3.0]((https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.4.md#schema)) also available)
- Easy construction of OpenAPI schemas using Python objects or dicts
- Seamless integration with Pydantic models for request/response schemas
- Utility functions for schema conversion and validation

---

## 📦 Installation

```bash
pip install openapi-pydantic
```

---

## 🚀 Quick Start

```python
from openapi_pydantic import OpenAPI, Info, PathItem, Operation, Response

open_api = OpenAPI(
    info=Info(
        title="My own API",
        version="v0.0.1",
    ),
    paths={
        "/ping": PathItem(
            get=Operation(
                responses={
                    "200": Response(
                        description="pong"
                    )
                }
            )
        )
    },
)
# For Pydantic 1.x, use `json` instead of `model_dump_json`
print(open_api.model_dump_json(by_alias=True, exclude_none=True, indent=2))
```

<details>
<summary>Output</summary>

```json
{
  "openapi": "3.1.1",
  "info": {
    "title": "My own API",
    "version": "v0.0.1"
  },
  "servers": [
    {
      "url": "/"
    }
  ],
  "paths": {
    "/ping": {
      "get": {
        "responses": {
          "200": {
            "description": "pong"
          }
        },
        "deprecated": false
      }
    }
  }
}
```
</details>

---

## 📝 Usage Examples

Pydantic allows you to use object, dict, or mixed data for input. The following examples all produce the same OpenAPI result as above:

```python
from openapi_pydantic import parse_obj, OpenAPI, PathItem, Response

# Construct OpenAPI from dict, inferring the correct schema version
open_api = parse_obj({
    "openapi": "3.1.1",
    "info": {"title": "My own API", "version": "v0.0.1"},
    "paths": {
        "/ping": {
            "get": {"responses": {"200": {"description": "pong"}}}
        }
    },
})

# Construct OpenAPI v3.1 schema from dict
# For Pydantic 1.x, use `parse_obj` instead of `model_validate`
open_api = OpenAPI.model_validate({
    "info": {"title": "My own API", "version": "v0.0.1"},
    "paths": {
        "/ping": {
            "get": {"responses": {"200": {"description": "pong"}}}
        }
    },
})

# Construct OpenAPI with mix of dict/object
open_api = OpenAPI.model_validate({
    "info": {"title": "My own API", "version": "v0.0.1"},
    "paths": {
        "/ping": PathItem(
            get={"responses": {"200": Response(description="pong")}}
        )
    },
})
```

---

## 🧑‍💻 Using Pydantic Classes as Schema

> 💡 **Tip:** Use your own Pydantic models for request/response schemas and let openapi-pydantic handle the conversion!

```python
from pydantic import BaseModel, Field
from openapi_pydantic import OpenAPI
from openapi_pydantic.util import PydanticSchema, construct_open_api_with_schema_class

def construct_base_open_api() -> OpenAPI:
    # For Pydantic 1.x, use `parse_obj` instead of `model_validate`
    return OpenAPI.model_validate({
        "info": {"title": "My own API", "version": "v0.0.1"},
        "paths": {
            "/ping": {
                "post": {
                    "requestBody": {"content": {"application/json": {
                        "schema": PydanticSchema(schema_class=PingRequest)
                    }}},
                    "responses": {"200": {
                        "description": "pong",
                        "content": {"application/json": {
                            "schema": PydanticSchema(schema_class=PingResponse)
                        }},
                    }},
                }
            }
        },
    })

class PingRequest(BaseModel):
    """Ping Request"""
    req_foo: str = Field(description="foo value of the request")
    req_bar: str = Field(description="bar value of the request")

class PingResponse(BaseModel):
    """Ping response"""
    resp_foo: str = Field(description="foo value of the response")
    resp_bar: str = Field(description="bar value of the response")

open_api = construct_base_open_api()
open_api = construct_open_api_with_schema_class(open_api)

# print the result openapi.json
# For Pydantic 1.x, use `json` instead of `model_dump_json`
print(open_api.model_dump_json(by_alias=True, exclude_none=True, indent=2))
```

<details>
<summary>Output</summary>

```json
{
  "openapi": "3.1.1",
  "info": {
    "title": "My own API",
    "version": "v0.0.1"
  },
  "servers": [
    {
      "url": "/"
    }
  ],
  "paths": {
    "/ping": {
      "post": {
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/PingRequest"
              }
            }
          },
          "required": false
        },
        "responses": {
          "200": {
            "description": "pong",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/PingResponse"
                }
              }
            }
          }
        },
        "deprecated": false
      }
    }
  },
  "components": {
    "schemas": {
      "PingRequest": {
        "title": "PingRequest",
        "required": [
          "req_foo",
          "req_bar"
        ],
        "type": "object",
        "properties": {
          "req_foo": {
            "title": "Req Foo",
            "type": "string",
            "description": "foo value of the request"
          },
          "req_bar": {
            "title": "Req Bar",
            "type": "string",
            "description": "bar value of the request"
          }
        },
        "description": "Ping Request"
      },
      "PingResponse": {
        "title": "PingResponse",
        "required": [
          "resp_foo",
          "resp_bar"
        ],
        "type": "object",
        "properties": {
          "resp_foo": {
            "title": "Resp Foo",
            "type": "string",
            "description": "foo value of the response"
          },
          "resp_bar": {
            "title": "Resp Bar",
            "type": "string",
            "description": "bar value of the response"
          }
        },
        "description": "Ping response"
      }
    }
  }
}
```
</details>

---

## Notes

### Use of OpenAPI.model_dump() / OpenAPI.model_dump_json() / OpenAPI.json() / OpenAPI.dict()

> ⚠️ **Important:** Always use `by_alias=True, exclude_none=True` when dumping models to JSON or dict, to ensure OpenAPI compatibility.

```python
# OK (Pydantic 2)
open_api.model_dump_json(by_alias=True, exclude_none=True, indent=2)
# OK (Pydantic 1)
open_api.json(by_alias=True, exclude_none=True, indent=2)

# Not good
open_api.model_dump_json(indent=2)
open_api.json(indent=2)
```

More info about field aliases:

| OpenAPI version | Field alias info |
| --------------- | ---------------- |
| 3.1 | [here](https://github.com/mike-oakley/openapi-pydantic/blob/main/openapi_pydantic/v3/v3_1/README.md#alias) |
| 3.0 | [here](https://github.com/mike-oakley/openapi-pydantic/blob/main/openapi_pydantic/v3/v3_0/README.md#alias) |

### Non-pydantic schema types

Some schema types are not implemented as pydantic classes.
See:

| OpenAPI version | Non-pydantic schema type info |
| --------------- | ----------------------------- |
| 3.1 | [here](https://github.com/mike-oakley/openapi-pydantic/blob/main/openapi_pydantic/v3/v3_1/README.md#non-pydantic-schema-types) |
| 3.0 | [here](https://github.com/mike-oakley/openapi-pydantic/blob/main/openapi_pydantic/v3/v3_0/README.md#non-pydantic-schema-types) |

### Use OpenAPI 3.0 instead of 3.1

> ℹ️ Some UI renderings (e.g. Swagger) do not support OpenAPI 3.1.x. You can use 3.0.x by importing from different paths:

```python
from openapi_pydantic.v3.v3_0 import OpenAPI, ...
from openapi_pydantic.v3.v3_0.util import PydanticSchema, construct_open_api_with_schema_class
```

### Pydantic version compatibility

Compatibility with both major versions of Pydantic (1.8+ and 2.*) is achieved using a module called `compat.py`. It detects the installed version and exports version-specific symbols for use by the rest of the package. The `compat.py` module is not intended to be imported by other packages, but may serve as an example for supporting multiple Pydantic versions.

---

## 🙏 Credits

This library is based on the original implementation by Kuimono of [OpenAPI Schema Pydantic](https://github.com/kuimono/openapi-schema-pydantic), which is no longer actively maintained.

---

## 📄 License

[MIT License](https://github.com/mike-oakley/openapi-pydantic/blob/main/LICENSE)
