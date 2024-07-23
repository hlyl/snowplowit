import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Application  # Ensure models are correctly imported
from app.config import load_config
from app.schemas import DynamicPydanticModel  # Ensure the Pydantic model is imported
from app.database import SessionLocal

# Initialize database session
engine = create_engine("sqlite:///../applications.db")
Session = sessionmaker(bind=engine)
session = Session()

# Load JSON configuration
config = load_config()


# Helper function to display an application's details
def display_application(application):
    for field in config["form"]["fields"]:
        field_name = field["field_name"]
        display_name = field["display_name"]
        value = getattr(application, field_name, "N/A")
        st.write(f"**{display_name}:** {value}")


# Streamlit UI
st.sidebar.title("Application Manager")
search_name = st.sidebar.text_input("Search by Application Name")
search_button = st.sidebar.button("Search")

create_new_button = st.sidebar.button("Create New")

if search_button:
    with SessionLocal() as session:
        application = (
            session.query(Application).filter(Application.name == search_name).first()
        )
        if application:
            st.title(f"Application: {application.name}")
            display_application(application)
        else:
            st.error("Application not found.")

if create_new_button:
    st.title("Create New Application")
    form_data = {}

    for field in config["form"]["fields"]:
        field_name = field["field_name"]
        display_name = field["display_name"]
        data_type = field["data_type"]
        field_default = field.get("default", "")

        if data_type.startswith("String"):
            form_data[field_name] = st.text_input(display_name, field_default)
        elif data_type == "Text":
            form_data[field_name] = st.text_area(display_name, field_default)
        elif data_type == "Boolean":
            form_data[field_name] = st.checkbox(display_name, field_default)
        elif data_type == "JSON":
            form_data[field_name] = st.text_area(display_name, str(field_default))
        elif data_type == "Date":
            form_data[field_name] = st.date_input(display_name, field_default)
        elif "options" in field:
            options = field["options"]
            if data_type == "select":
                form_data[field_name] = st.selectbox(display_name, options)
            elif data_type == "multiselect":
                form_data[field_name] = st.multiselect(display_name, options)

    if st.button("Submit"):
        with SessionLocal() as session:
            new_application = Application(**form_data)
            session.add(new_application)
            session.commit()
            st.success("Application created successfully!")
