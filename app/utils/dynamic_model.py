from pydantic import BaseModel, Field, create_model, field_validator
from typing import List, Dict, Any, Type, Union
from app.config import load_config
from app.utils.utils import handle_date

config = load_config()


def get_field_type(data_type: str, field_default: Any) -> Any:
    if data_type.startswith("String"):
        return (str, Field(default=field_default))
    elif data_type == "Text":
        return (str, Field(default=field_default))
    elif data_type == "Boolean":
        return (bool, Field(default=field_default))
    elif data_type == "JSON":
        return (Dict[str, Any], Field(default=field_default))
    elif data_type == "Date":
        return (
            str,
            Field(default=field_default),
        )  # Date handling will be customized with a validator
    return None


def create_pydantic_model(name: str, fields: List[Dict[str, Any]]) -> Type[BaseModel]:
    pydantic_fields = {}
    validators = {}

    for field in fields:
        field_name = field["field_name"]
        data_type = field["data_type"]
        field_default = field.get("default", None)

        field_type = get_field_type(data_type, field_default)
        if field_type:
            pydantic_fields[field_name] = field_type
            if data_type == "Date":
                # Add a validator for date fields
                validators[field_name] = field_validator(field_name, pre=True)(
                    handle_date
                )
        else:
            print(f"Unsupported data type for field {field_name}: {data_type}")

    # Create model with validators
    model = create_model(name, **pydantic_fields)

    # Add validators to the model
    for field_name, validator_func in validators.items():
        setattr(model, f"_{field_name}_validator", validator_func)

    return model


def process_fields(fields: List[Dict[str, Any]]) -> List[Type[BaseModel]]:
    models = []
    for field in fields:
        field_name = field.get("field_name")
        data_type = field.get("data_type")

        if not field_name or not data_type:
            # Check for nested fields in groups
            nested_fields = field.get("fields")
            if nested_fields:
                nested_model_name = field.get("display_name", "NestedModel")
                nested_model = create_pydantic_model(nested_model_name, nested_fields)
                models.append(nested_model)
            else:
                print(
                    f"Skipping field due to missing 'field_name' or 'data_type': {field}"
                )
            continue

        field_type = get_field_type(data_type, field.get("default", None))
        if field_type:
            models.append(create_pydantic_model(field_name.capitalize(), [field]))
        else:
            print(f"Unsupported data type for field {field_name}: {data_type}")

    return models


# Process fields and generate models
models = process_fields(config["form"]["fields"])

# Combine all models into a single dynamic model
DynamicPydanticModel = create_model(
    "DynamicPydanticModel",
    **{model.__name__: (Optional[model], Field(default=None)) for model in models},
)

# Print generated models for debugging
for model in models:
    print(model.model_json_schema(indent=2))

# Example usage
print(DynamicPydanticModel.schema_json(indent=2))
