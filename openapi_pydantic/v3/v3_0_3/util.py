import logging
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    cast,
)

from pydantic import BaseModel

from openapi_pydantic.compat import (
    DEFS_KEY,
    PYDANTIC_V2,
    JsonSchemaMode,
    models_json_schema,
    v1_schema,
    get_flat_models_from_models,
    get_model_name_map
)

from . import Components, OpenAPI, Reference, Schema, schema_validate

logger = logging.getLogger(__name__)

PydanticType = TypeVar("PydanticType", bound=BaseModel)
ref_prefix = "#/components/schemas/"
ref_template = "#/components/schemas/{model}"


class PydanticSchema(Schema, Generic[PydanticType]):
    """Special `Schema` class to indicate a reference from pydantic class"""

    schema_class: Type[PydanticType]
    """the class that is used for generate the schema"""


def get_mode(
    cls: Type[BaseModel], default: JsonSchemaMode = "validation"
) -> JsonSchemaMode:
    """Get the JSON schema mode for a model class.

    The mode can be either "validation" or "serialization". In validation mode,
    computed fields are dropped and optional fields remain optional. In
    serialization mode, computed and optional fields are required.
    """
    if not hasattr(cls, "model_config"):
        return default
    mode = cls.model_config.get("json_schema_mode", default)
    if mode not in ("validation", "serialization"):
        raise ValueError(f"invalid json_schema_mode: {mode}")
    return cast(JsonSchemaMode, mode)


if TYPE_CHECKING:

    class GenerateOpenAPI30Schema:
        ...

elif PYDANTIC_V2:
    from enum import Enum

    from pydantic.json_schema import GenerateJsonSchema, JsonSchemaValue
    from pydantic_core import core_schema

    class GenerateOpenAPI30Schema(GenerateJsonSchema):
        """Modify the schema generation for OpenAPI 3.0."""

        def nullable_schema(
            self,
            schema: core_schema.NullableSchema,
        ) -> JsonSchemaValue:
            """Generates a JSON schema that matches a schema that allows null values.

            In OpenAPI 3.0, types can not be None, but a special "nullable" field is
            available.
            """
            inner_json_schema = self.generate_inner(schema["schema"])
            inner_json_schema["nullable"] = True
            return inner_json_schema

        def literal_schema(self, schema: core_schema.LiteralSchema) -> JsonSchemaValue:
            """Generates a JSON schema that matches a literal value.

            In OpenAPI 3.0, the "const" keyword is not supported, so this
            version of this method skips that optimization.
            """
            expected = [
                v.value if isinstance(v, Enum) else v for v in schema["expected"]
            ]

            types = {type(e) for e in expected}
            if types == {str}:
                return {"enum": expected, "type": "string"}
            elif types == {int}:
                return {"enum": expected, "type": "integer"}
            elif types == {float}:
                return {"enum": expected, "type": "number"}
            elif types == {bool}:
                return {"enum": expected, "type": "boolean"}
            elif types == {list}:
                return {"enum": expected, "type": "array"}
            # there is not None case because if it's mixed it hits the final `else`
            # if it's a single Literal[None] then it becomes a `const` schema above
            else:
                return {"enum": expected}

else:

    class GenerateOpenAPI30Schema:
        ...


def construct_open_api_with_schema_class(
    open_api: OpenAPI,
    schema_classes: Optional[List[Type[BaseModel]]] = None,
    scan_for_pydantic_schema_reference: bool = True,
    by_alias: bool = True,
) -> OpenAPI:
    """
    Construct a new OpenAPI object, utilising pydantic classes to produce JSON schemas.

    :param open_api: the base `OpenAPI` object
    :param schema_classes: Pydantic classes that their schema will be used
                           "#/components/schemas" values
    :param scan_for_pydantic_schema_reference: flag to indicate if scanning for
                                               `PydanticSchemaReference` class
                                               is needed for "#/components/schemas"
                                               value updates
    :param by_alias: construct schema by alias (default is True)
    :return: new OpenAPI object with "#/components/schemas" values updated.
             If there is no update in "#/components/schemas" values, the original
             `open_api` will be returned.
    """
    copy_func = getattr(open_api, "model_copy" if PYDANTIC_V2 else "copy")
    new_open_api: OpenAPI = copy_func(deep=True)

    model_name_map = _get_schemas_unique_names(new_open_api)

    if scan_for_pydantic_schema_reference:
        extracted_schema_classes = _handle_pydantic_schema(new_open_api, model_name_map)
        if schema_classes:
            schema_classes = list({*schema_classes, *extracted_schema_classes})
        else:
            schema_classes = extracted_schema_classes

    if not schema_classes:
        return open_api

    schema_classes.sort(key=lambda x: x.__name__)
    logger.debug("schema_classes: %s", schema_classes)

    # update new_open_api with new #/components/schemas
    if PYDANTIC_V2:
        _key_map, schema_definitions = models_json_schema(
            [(c, get_mode(c)) for c in schema_classes],
            by_alias=by_alias,
            ref_template=ref_template,
            schema_generator=GenerateOpenAPI30Schema,
        )
    else:
        schema_definitions = v1_schema(
            schema_classes, by_alias=by_alias, ref_prefix=ref_prefix
        )

    if not new_open_api.components:
        new_open_api.components = Components()
    if new_open_api.components.schemas:
        for existing_key in new_open_api.components.schemas:
            if existing_key in schema_definitions[DEFS_KEY]:
                logger.warning(
                    f'"{existing_key}" already exists in {ref_prefix}. '
                    f'The value of "{ref_prefix}{existing_key}" will be overwritten.'
                )
        new_open_api.components.schemas.update(_validate_schemas(schema_definitions))
    else:
        new_open_api.components.schemas = _validate_schemas(schema_definitions)
    return new_open_api


def _validate_schemas(
    schema_definitions: Dict[str, Any]
) -> Dict[str, Union[Reference, Schema]]:
    """Convert JSON Schema definitions to parsed OpenAPI objects"""
    # Note: if an error occurs in schema_validate(), it may indicate that
    # the generated JSON schemas are not compatible with the version
    # of OpenAPI this module depends on.
    return {
        key: schema_validate(schema_dict)
        for key, schema_dict in schema_definitions[DEFS_KEY].items()
    }


def _handle_pydantic_schema(open_api: OpenAPI, model_name_map: Dict[Type[BaseModel], str]) -> List[Type[BaseModel]]:
    """
    This function traverses the `OpenAPI` object and

    1. Replaces the `PydanticSchema` object with `Reference` object, with correct ref
       value;
    2. Extracts the involved schema class from `PydanticSchema` object.

    **This function will mutate the input `OpenAPI` object.**

    :param open_api: the `OpenAPI` object to be traversed and mutated
    :model_name_map: a dict of schema classes as a key and unique name as a value
    :return: a list of schema classes extracted from `PydanticSchema` objects
    """

    pydantic_types: Set[Type[BaseModel]] = set()

    def _traverse(obj: Any) -> None:
        if isinstance(obj, BaseModel):
            fields = getattr(
                obj, "model_fields_set" if PYDANTIC_V2 else "__fields_set__"
            )
            for field in fields:
                child_obj = obj.__getattribute__(field)
                if isinstance(child_obj, PydanticSchema):
                    logger.debug("PydanticSchema found in %s: %s", obj, child_obj)
                    obj.__setattr__(field, _construct_ref_obj(child_obj, model_name_map))
                    pydantic_types.add(child_obj.schema_class)
                else:
                    _traverse(child_obj)
        elif isinstance(obj, list):
            for index, elem in enumerate(obj):
                if isinstance(elem, PydanticSchema):
                    logger.debug(f"PydanticSchema found in list: {elem}")
                    obj[index] = _construct_ref_obj(elem)
                    pydantic_types.add(elem.schema_class)
                else:
                    _traverse(elem)
        elif isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, PydanticSchema):
                    logger.debug(f"PydanticSchema found in dict: {value}")
                    obj[key] = _construct_ref_obj(value)
                    pydantic_types.add(value.schema_class)
                else:
                    _traverse(value)

    _traverse(open_api)
    return list(pydantic_types)


def _construct_ref_obj(pydantic_schema: PydanticSchema[PydanticType], model_name_map: Dict[Type[BaseModel], str]) -> Reference:
    unique_model_name = model_name_map.get(pydantic_schema.schema_class)
    if unique_model_name is None:
        unique_model_name = pydantic_schema.schema_class.__name__
    ref_obj = Reference(**{"$ref": ref_prefix + unique_model_name})
    logger.debug(f"ref_obj={ref_obj}")
    return ref_obj


def _get_schemas_unique_names(open_api: OpenAPI) -> Dict[Type[BaseModel], str]:
    """
    This function traverses the `OpenAPI` object and

    1. Finds the `PydanticSchema`
    2. Extracts the involved schema class from `PydanticSchema` object.
    3. Generates unique schema names.

    :param open_api: the `OpenAPI` object to be traversed
    :return: a dict of schema classes extracted from `PydanticSchema`
        objects as key and unique name as a value
    """

    pydantic_types: Set[Type[BaseModel]] = set()

    def _traverse(obj: Any) -> None:
        if isinstance(obj, BaseModel):
            fields = getattr(
                obj, "model_fields_set" if PYDANTIC_V2 else "__fields_set__"
            )
            for field in fields:
                child_obj = obj.__getattribute__(field)
                if isinstance(child_obj, PydanticSchema):
                    logger.debug("PydanticSchema found in %s: %s", obj, child_obj)
                    pydantic_types.add(child_obj.schema_class)
                else:
                    _traverse(child_obj)
        elif isinstance(obj, list):
            for index, elem in enumerate(obj):
                if isinstance(elem, PydanticSchema):
                    logger.debug(f"PydanticSchema found in list: {elem}")
                    pydantic_types.add(elem.schema_class)
                else:
                    _traverse(elem)
        elif isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, PydanticSchema):
                    logger.debug(f"PydanticSchema found in dict: {value}")
                    pydantic_types.add(value.schema_class)
                else:
                    _traverse(value)

    _traverse(open_api)
    if PYDANTIC_V2:
        model_name_map = {}
    else:
        flat_models = get_flat_models_from_models(pydantic_types)
        model_name_map = get_model_name_map(flat_models)
    return model_name_map
