import json
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Date, JSON
from sqlalchemy.orm import declarative_base, sessionmaker

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the config.json file
config_path = os.path.join(current_dir, "../config.json")

# Load JSON configuration
with open(config_path) as f:
    config = json.load(f)

Base = declarative_base()

# Helper function to sanitize field names
def sanitize_field_name(name):
    return ''.join(c if c.isalnum() else '_' for c in name)

# Dynamically create the SQLAlchemy model
class DynamicModel(Base):
    __tablename__ = 'dynamic_table'
    id = Column(Integer, primary_key=True)

    # Map the fields from the JSON config to SQLAlchemy columns
    for field in config['form']['fields']:
        if field['type'] == 'group':
            for subfield in field['fields']:
                column_name = sanitize_field_name(subfield['field_name'])
                print(f"Adding column: {column_name} with type {subfield['data_type']}")
                exec(f"{column_name} = Column({subfield['data_type']})")
        else:
            column_name = sanitize_field_name(field['field_name'])
            print(f"Adding column: {column_name} with type {field['data_type']}")
            exec(f"{column_name} = Column({field['data_type']})")

# Create an SQLite database
engine = create_engine('sqlite:///dynamic_db.sqlite')
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Example of inserting data (you can modify this part as needed)
new_entry = DynamicModel()
for field in config['form']['fields']:
    if field['type'] == 'group':
        for subfield in field['fields']:
            column_name = sanitize_field_name(subfield['field_name'])
            setattr(new_entry, column_name, subfield.get('default'))
    else:
        column_name = sanitize_field_name(field['field_name'])
        setattr(new_entry, column_name, field.get('default'))

session.add(new_entry)
session.commit()

print("Database created and initial data inserted.")