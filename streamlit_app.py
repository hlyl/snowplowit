import streamlit as st
import requests
import datetime
import logging
import uuid

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPI backend URL
API_URL = "http://localhost:8000"

# Load the configuration to dynamically generate form fields
config_response = requests.get(f"{API_URL}/config/")
if config_response.status_code == 200:
    config = config_response.json()
    logger.info("Configuration loaded successfully")
    if "form" not in config or "fields" not in config["form"]:
        st.error("Configuration format error: 'form' key or 'fields' key not found")
        st.stop()
else:
    st.error("Error loading configuration")
    st.stop()


def process_fields(fields, data=None):
    form_data = {}
    for field in fields:
        field_name = field["field_name"]
        display_name = field["display_name"]
        field_type = field["type"]
        default = field.get("default")

        if data and field_name in data:
            default = data[field_name]

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
        elif field_type == "date":
            if default is not None and isinstance(default, str):
                default = datetime.datetime.strptime(default, "%Y-%m-%d").date()
            form_data[field_name] = st.date_input(
                display_name, default if default is not None else datetime.date.today()
            )
        elif field_type == "group":
            st.subheader(display_name)
            nested_form_data = process_fields(field["fields"], data)
            form_data.update(nested_form_data)

    return form_data


# Streamlit App
st.title("Application Management")

# Sidebar for Search
st.sidebar.header("Search Applications")
search_name = st.sidebar.text_input("Enter Application Name to Search")
search_button = st.sidebar.button("Search")

application_data = None

if search_button:
    logger.info(f"Searching for application with name: {search_name}")
    if search_name:
        response = requests.get(
            f"{API_URL}/applications/", params={"name": search_name}
        )
        logger.debug(f"Search response: {response.status_code} {response.text}")
        if response.status_code == 200:
            applications = response.json()
            if applications:
                st.sidebar.success("Application found!")
                application_data = applications[0]
                logger.info(f"Application found: {application_data}")
            else:
                st.sidebar.error("No applications found.")
                logger.info("No applications found.")
        else:
            st.sidebar.error("Error fetching applications.")
            logger.error(f"Error fetching applications: {response.status_code}")
    else:
        st.sidebar.warning("Please enter a name to search.")
        logger.warning("Search name is empty")

# Main Page
st.header("Application Form")
with st.form(key="application_form"):
    form_data = process_fields(config["form"]["fields"], application_data)

    # Submit button within the form
    submit_button = st.form_submit_button(label="Submit")
    generate_pdf_button = st.form_submit_button(label="Generate PDF")

    if submit_button:
        # Log the form data
        logger.info(f"Submitting the following data: {form_data}")
        st.write("Submitting the following data:", form_data)

        # Convert form_data to match expected types
        if "environments" in form_data and isinstance(form_data["environments"], list):
            form_data["environments"] = {env: True for env in form_data["environments"]}
        if "external_users" in form_data and isinstance(
            form_data["external_users"], list
        ):
            form_data["external_users"] = {
                user: True for user in form_data["external_users"]
            }
        if "process_class" in form_data:
            form_data["process_class"] = str(form_data["process_class"])
        if "data_classification" in form_data:
            form_data["data_classification"] = str(form_data["data_classification"])
        if "access_mgmt_system" in form_data:
            form_data["access_mgmt_system"] = str(form_data["access_mgmt_system"])
        if "decommission_date" in form_data:
            form_data["decommission_date"] = (
                form_data["decommission_date"].strftime("%Y-%m-%d")
                if form_data["decommission_date"]
                else None
            )

        # Log the converted form data
        logger.debug(f"Converted data to be submitted: {form_data}")
        st.write("Converted data to be submitted:", form_data)

        if application_data:
            response = requests.put(
                f"{API_URL}/applications/{application_data['id']}", json=form_data
            )
        else:
            response = requests.post(f"{API_URL}/applications/", json=form_data)

        # Log the response
        logger.debug(f"Response from server: {response.status_code} {response.text}")
        st.write("Response from server:", response.status_code, response.text)

        if response.status_code == 200:
            st.success(
                "Entry added successfully!"
                if not application_data
                else "Entry updated successfully!"
            )
            logger.info("Entry added/updated successfully")
        else:
            st.error(
                "Error adding entry" if not application_data else "Error updating entry"
            )
            logger.error(f"Error adding/updating entry: {response.status_code}")

    if generate_pdf_button and application_data:
        # Trigger PDF generation
        logger.info(f"Generating PDF for application ID: {application_data['id']}")
        pdf_response = requests.get(
            f"{API_URL}/applications/pdf/{application_data['id']}"
        )
        logger.debug(f"PDF generation response: {pdf_response.status_code}")
        if pdf_response.status_code == 200:
            # Save PDF to a temporary file
            with open(f"/tmp/{application_data['id']}.pdf", "wb") as f:
                f.write(pdf_response.content)
            st.success("PDF generated successfully!")
            st.download_button(
                "Download PDF",
                data=open(f"/tmp/{application_data['id']}.pdf", "rb"),
                file_name=f"{application_data['id']}.pdf",
                mime="application/pdf",
            )
            logger.info("PDF generated and download link provided")
        else:
            st.error("Error generating PDF")
            logger.error(f"Error generating PDF: {pdf_response.status_code}")

# Display all entries
st.header("All Entries")
response = requests.get(f"{API_URL}/applications/")
logger.debug(f"All entries response: {response.status_code}")
if response.status_code == 200:
    all_applications = response.json()
    for app in all_applications:
        st.write(app)
    logger.info(f"All applications displayed: {all_applications}")
else:
    st.error("Error fetching all entries.")
    logger.error(f"Error fetching all entries: {response.status_code}")
