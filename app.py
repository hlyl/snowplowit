import streamlit as st
import requests
from datetime import date

API_URL = "http://localhost:8000/applications/"

st.title("Snow PlowIT Application Form")

# Gather form inputs
form_data = {
    "name": st.text_input("Name", "Default Name"),
    "application_type": st.selectbox(
        "Application Type", [None, "SaaS", "Homegrown", "COTS"], index=1
    ),
    "description": st.text_area("Description"),
    "architecture_type": st.selectbox(
        "Architecture Type", ["Monolithic", "Microservices", "Serverless"], index=0
    ),
    "platform_host": st.text_input("Platform Host"),
    "install_type": st.selectbox(
        "Install Type",
        [
            None,
            "On Premise",
            "Hybrid",
            "Private Cloud",
            "Public Cloud",
            "Cloud",
            "SaaS",
            "PaaS",
            "Third Party Hosted",
        ],
        index=6,
    ),
    "life_cycle_stage": st.selectbox(
        "Life cycle stage", [None, "Operational"], index=1
    ),
    "life_cycle_stage_status": st.selectbox(
        "Life cycle stage status", [None, "In Use"], index=1
    ),
    "life_cycle_status": st.selectbox(
        "Life cycle status",
        ["Development", "Operational", "Retired", "Non-Operational"],
        index=1,
    ),
    "environments": st.multiselect(
        "Environments",
        ["Sandbox", "Development", "Training", "Test", "Validation", "Production"],
    ),
    "number_of_users": st.selectbox(
        "Number of users",
        ["0", "0-49", "50-99", "100-499", "500-999", "1000+"],
        index=1,
    ),
    "it_solution_owner": st.text_input("IT Solution Owner"),
    "it_solution_manager": st.text_input("IT Solution Manager"),
    "qa": st.text_input("QA"),
    "commission": st.checkbox("Commission", value=True),
    "decommission_date": st.date_input("Decommission date", value=None),
    "access_mgmt_system": st.selectbox(
        "Access Mgmt System",
        ["UserAR2", "novoAccess", "Other", "System Access Management (SAM)", None],
        index=4,
    ),
    "capabilities": st.text_input("Capabilities"),
    "links_to_cis": st.text_input("Links to CIs"),
    "it_risk_assessment": st.text_input("IT Risk Assessment"),
    "impact_assessment": st.text_input("Impact Assessment"),
}

# Convert date object to string if it is not None
if form_data["decommission_date"]:
    form_data["decommission_date"] = form_data["decommission_date"].isoformat()

# Submit form data
if st.button("Submit"):
    try:
        response = requests.post(API_URL, json=form_data)
        if response.status_code == 200:
            st.success("Application submitted successfully!")
        else:
            st.error(f"Error submitting application: {response.text}")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
