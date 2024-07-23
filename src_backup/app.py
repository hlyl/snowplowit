
import streamlit as st
import json
import requests
import os

# Get the directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the config file
config_path = os.path

# Construct the full path to the config file
config_path = os.path.join(base_dir, "..", "config.json")

# Load JSON configuration
with open(config_path) as f:
    config = json.load(f)

def sanitize_field_name(name):
    return ''.join(c if c.isalnum() else '_' for c in name).lower()

def render_field(field, prefix="", value=None):
    field_type = field["type"]
    field_name = field["field_name"]
    display_name = field["display_name"]
    sanitized_field_name = sanitize_field_name(field_name)
    key = f"{prefix}_{sanitized_field_name}"
    default_value = value if value is not None else field.get("default")
    
    if field_type == "text":
        return st.text_input(display_name, value=default_value, key=key)
    elif field_type == "textarea":
        return st.text_area(
            display_name, value=default_value, key=key, max_chars=field.get("max_length")
        )
    elif field_type == "select":
        return st.selectbox(
            display_name,
            field["options"],
            index=(
                field["options"].index(default_value)
                if default_value in field["options"]
                else 0
            ),
            key=key,
        )
    elif field_type == "number":
        return st.number_input(
            display_name, value=default_value if default_value is not None else 0, key=key
        )
    elif field_type == "checkbox":
        return st.checkbox(display_name, value=default_value, key=key)
    elif field_type == "date":
        return st.date_input(display_name, value=default_value, key=key)
    elif field_type == "multiselect":
        return st.multiselect(
            display_name, field["options"], default=default_value, key=key
        )
    elif field_type == "group":
        st.subheader(display_name)
        group_data = {}
        for i, sub_field in enumerate(field["fields"]):
            sub_key = f"{key}_{i}"
            group_data[sub_field["field_name"]] = render_field(
                sub_field, prefix=sub_key, value=value
            )
        return group_data

st.title("SNOW - PlowIT")

# Create a search box and button
search_name = st.text_input("Search by Name")
original_data = {}

# Initialize search_data to None
search_data = {}
if st.button("Search"):
    sanitized_search_name = sanitize_field_name("Name")
    search_response = requests.get(f"http://127.0.0.1:8000/search/{search_name}")
    if search_response.status_code == 200:
        search_data = search_response.json()
        original_data = search_data
        st.success(f"Record found for {search_name}")
    else:
        st.warning(f"No record found for {search_name}. You can create a new entry.")
        search_data = {sanitized_search_name: search_name}  # Initialize with search name

# Render the form
form_data = {}
for i, field in enumerate(config["form"]["fields"]):
    sanitized_field_name = sanitize_field_name(field["field_name"])
    form_data[sanitized_field_name] = render_field(
        field,
        prefix=f"field_{i}",
        value=search_data.get(sanitized_field_name),
    )

if st.button("Generate and Download PDF"):
    response = requests.post("http://127.0.0.1:8000/submit/", json=form_data)
    if response.status_code == 200:
        st.success("Form submitted successfully!")

        # Download the generated PDF
        pdf_response = requests.get("http://127.0.0.1:8000/download/")
        if pdf_response.status_code == 200:
            st.download_button(
                label="Download PDF",
                data=pdf_response.content,
                file_name="output.pdf",
                mime="application/pdf",
            )
        else:
            st.error(f"Error downloading PDF: {pdf_response.text}")
    else:
        st.error(f"Error submitting form: {response.text}")