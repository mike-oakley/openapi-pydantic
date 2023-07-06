import enum


class DataType(str, enum.Enum):
    """Data type of an object."""

    NULL = "null"
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
