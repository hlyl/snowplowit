from sqlalchemy import create_engine, Column, String, Text, Boolean, JSON, Date, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from app.database import Base
from app.config import load_config
import uuid

config = load_config()

# SQLAlchemy Base
Base = declarative_base()

# Helper function to determine column type
def get_column_type(data_type):
    if data_type.startswith("String"):
        return String(255)
    elif data_type == "Text":
        return Text
    elif data_type == "Boolean":
        return Boolean
    elif data_type == "JSON":
        return JSON
    elif data_type == "Date":
        return Date
    return None

# Function to process fields
def process_fields(fields, attributes):
    for field in fields:
        field_name = field.get("field_name")
        data_type = field.get("data_type")

        if not field_name or not data_type:
            # Check for nested fields in groups
            nested_fields = field.get("fields")
            if nested_fields:
                process_fields(nested_fields, attributes)
            else:
                print(
                    f"Skipping field due to missing 'field_name' or 'data_type': {field}"
                )
            continue

        column_type = get_column_type(data_type)
        if column_type:
            attributes[field_name] = Column(column_type)
        else:
            print(f"Unsupported data type for field {field_name}: {data_type}")

# Generate SQLAlchemy Model using a dictionary
attributes = {
    "__tablename__": "applications",
    "id": Column(String, primary_key=True, default=lambda: str(uuid.uuid4())),
}

process_fields(config["form"]["fields"], attributes)

# Define the Application class
Application = type("Application", (Base,), attributes)

# SQLite engine and session
engine = create_engine("sqlite:///applications.db")
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

print("Database and table created successfully.")