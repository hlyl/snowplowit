import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.model import Base, Application
from app.config import load_config

# Load configuration
config = load_config()

# SQLite engine and session
DATABASE_URL = "sqlite:///applications.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Streamlit App
st.title("Application Management")

# Sidebar for Search
st.sidebar.header("Search Applications")
search_name = st.sidebar.text_input("Enter Application Name to Search")
search_button = st.sidebar.button("Search")


def get_all_fields(fields):
    all_fields = []
    for field in fields:
        if "fields" in field:
            all_fields.extend(get_all_fields(field["fields"]))
        else:
            all_fields.append(field["field_name"])
    return all_fields


all_field_names = get_all_fields(config["form"]["fields"])

application_data = None

if search_button:
    if search_name:
        applications = (
            session.query(Application)
            .filter(Application.name.like(f"%{search_name}%"))
            .all()
        )
        if applications:
            st.sidebar.success("Application found!")
            application_data = applications[0]
        else:
            st.sidebar.error("No applications found.")
    else:
        st.sidebar.warning("Please enter a name to search.")

# Main Page
st.header("Application Form")
with st.form(key="application_form"):
    form_data = {}

    def process_fields(fields):
        for field in fields:
            field_name = field["field_name"]
            display_name = field["display_name"]
            field_type = field["type"]
            default = field.get("default", None)

            if application_data and hasattr(application_data, field_name):
                default = getattr(application_data, field_name)

            if field_type == "text":
                form_data[field_name] = st.text_input(
                    display_name, default if default is not None else ""
                )
            elif field_type == "textarea":
                form_data[field_name] = st.text_area(
                    display_name, default if default is not None else ""
                )
            elif field_type == "select":
                options = field["options"]
                if default is not None and default not in options:
                    options.insert(0, default)  # Ensure default is in options
                form_data[field_name] = st.selectbox(
                    display_name,
                    options,
                    index=options.index(default) if default in options else 0,
                )
            elif field_type == "multiselect":
                options = field["options"]
                if default is not None:
                    if isinstance(default, list):
                        for d in default:
                            if d not in options:
                                options.append(
                                    d
                                )  # Ensure all default values are in options
                    elif default not in options:
                        options.append(default)
                form_data[field_name] = st.multiselect(
                    display_name, options, default if default is not None else []
                )
            elif field_type == "checkbox":
                form_data[field_name] = st.checkbox(
                    display_name, default if default is not None else False
                )
            elif field_type == "group":
                st.subheader(display_name)
                process_fields(field["fields"])

    process_fields(config["form"]["fields"])

    # Submit button within the form
    submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        if application_data:
            for key, value in form_data.items():
                setattr(application_data, key, value)
            session.commit()
            st.success("Entry updated successfully!")
        else:
            new_application = Application(**form_data)
            session.add(new_application)
            session.commit()
            st.success("Entry added successfully!")

# Display all entries
st.header("All Entries")
all_applications = session.query(Application).all()
for app in all_applications:
    st.write(
        {field: getattr(app, field) for field in all_field_names if hasattr(app, field)}
    )
