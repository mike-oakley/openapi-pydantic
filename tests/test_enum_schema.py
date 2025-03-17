import pytest
from openapi_pydantic.v3.v3_0 import Schema as SchemaV3_0
from openapi_pydantic.v3.v3_1 import Schema as SchemaV3_1

def test_enum_schema_v3_0():
    schema = SchemaV3_0(type="string", enum=["value1", "value2", "value3"])
    assert schema.enum == ["value1", "value2", "value3"]

    with pytest.raises(ValueError):
        SchemaV3_0(type="string", enum="invalid_enum")

    with pytest.raises(ValueError):
        SchemaV3_0(type="string", enum=["value1", 2, "value3"])

def test_enum_schema_v3_1():
    schema = SchemaV3_1(type="string", enum=["value1", "value2", "value3"])
    assert schema.enum == ["value1", "value2", "value3"]

    with pytest.raises(ValueError):
        SchemaV3_1(type="string", enum="invalid_enum")

    with pytest.raises(ValueError):
        SchemaV3_1(type="string", enum=["value1", 2, "value3"])
