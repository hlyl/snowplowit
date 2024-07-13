import json
from sqlalchemy import Column, Integer, create_engine, String, Text, Date, Boolean, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Load JSON configuration
with open("config.json") as f:
    config = json.load(f)

Base = declarative_base()

# Map sqlalchemy_type from string to actual SQLAlchemy types
type_mapping = {
    "String(255)": String(255),
    "Text": Text,
    "Date": Date,
    "Boolean": Boolean,
    "JSON": JSON,
}


class DynamicModel(Base):
    __tablename__ = "form_data"

    # Primary key id set to auto-increment
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Loop through each field in the configuration
    for field in config["form"]["fields"]:
        col_name = field["name"].replace(" ", "_").lower()
        col_type = type_mapping.get(
            field.get("sqlalchemy_type"), String(255)
        )  # Default to String(255) if not found

        vars()[col_name] = Column(col_type, nullable=True)


# SQLite database URL
DATABASE_URL = "sqlite:///./form_data.db"

# Create the database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the database
Base.metadata.create_all(bind=engine)
