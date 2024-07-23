from pydantic import BaseModel, Field, create_model
from typing import List, Optional, Dict, Any
from app.config import load_config

config = load_config()

# Generate Pydantic Model using a dictionary
pydantic_fields = {}


def get_pydantic_type(data_type: str, default: Any):
    if data_type.startswith("String"):
        return (str, Field(default=default))
    elif data_type == "Text":
        return (str, Field(default=default))
    elif data_type == "Boolean":
        return (bool, Field(default=default))
    elif data_type == "JSON":
        return (Dict[str, Any], Field(default=default))
    elif data_type == "Date":
        return (str, Field(default=default))  # Date handling can be customized
    return None


def process_fields(fields: List[Dict[str, Any]], model_fields: Dict[str, Any]):
    for field in fields:
        field_name = field.get("field_name")
        data_type = field.get("data_type")
        field_default = field.get("default", None)

        if not field_name or not data_type:
            # Check for nested fields in groups
            nested_fields = field.get("fields")
            if nested_fields:
                process_fields(nested_fields, model_fields)
            else:
                print(
                    f"Skipping field due to missing 'field_name' or 'data_type': {field}"
                )
            continue

        field_type = get_pydantic_type(data_type, field_default)
        if field_type:
            model_fields[field_name] = field_type
        else:
            print(f"Unsupported data type for field {field_name}: {data_type}")


process_fields(config["form"]["fields"], pydantic_fields)

# Define the Pydantic model
DynamicPydanticModel = create_model("DynamicPydanticModel", **pydantic_fields)


# Example usage
class ApplicationCreate(DynamicPydanticModel):
    pass


class ApplicationUpdate(DynamicPydanticModel):
    pass


class ApplicationResponse(DynamicPydanticModel):
    id: int

    class Config:
        orm_mode = True
