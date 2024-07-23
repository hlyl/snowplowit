import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Application
from app.config import load_config

# Load configuration
config = load_config()

# SQLite engine and session
DATABASE_URL = "sqlite:///applications.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Streamlit App
st.title("Application Form")

# Form input fields based on config
form_data = {}


def process_fields(fields):
    for field in fields:
        field_name = field["field_name"]
        display_name = field["display_name"]
        field_type = field["type"]
        default = field.get("default", "")

        if field_type == "text":
            form_data[field_name] = st.text_input(display_name, default)
        elif field_type == "textarea":
            form_data[field_name] = st.text_area(display_name, default)
        elif field_type == "select":
            options = field["options"]
            form_data[field_name] = st.selectbox(
                display_name,
                options,
                index=options.index(default) if default in options else 0,
            )
        elif field_type == "multiselect":
            options = field["options"]
            form_data[field_name] = st.multiselect(display_name, options, default)
        elif field_type == "checkbox":
            form_data[field_name] = st.checkbox(display_name, default)
        elif field_type == "group":
            st.subheader(display_name)
            process_fields(field["fields"])


process_fields(config["form"]["fields"])

# Submit button
if st.button("Submit"):
    new_application = Application(**form_data)
    session.add(new_application)
    session.commit()
    st.success("Entry added successfully!")

# Display entries
st.header("Entries")

# Search functionality
search_name = st.text_input("Search by Application Name")

if search_name:
    applications = (
        session.query(Application)
        .filter(Application.name.like(f"%{search_name}%"))
        .all()
    )
else:
    applications = session.query(Application).all()

if applications:
    for app in applications:
        st.write({field: getattr(app, field) for field in form_data.keys()})
else:
    st.write("No applications found")

# Display all entries
st.header("All Entries")
all_applications = session.query(Application).all()
for app in all_applications:
    st.write({field: getattr(app, field) for field in form_data.keys()})
