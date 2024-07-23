import streamlit as st
import requests

# FastAPI backend URL
API_URL = "http://localhost:8000"

# Streamlit App
st.title("Application Management")

# Sidebar for Search
st.sidebar.header("Search Applications")
search_name = st.sidebar.text_input("Enter Application Name to Search")
search_button = st.sidebar.button("Search")

application_data = None

if search_button:
    if search_name:
        response = requests.get(f"{API_URL}/applications/", params={"name": search_name})
        if response.status_code == 200:
            applications = response.json()
            if applications:
                st.sidebar.success("Application found!")
                application_data = applications[0]
            else:
                st.sidebar.error("No applications found.")
        else:
            st.sidebar.error("Error fetching applications.")
    else:
        st.sidebar.warning("Please enter a name to search.")

# Main Page
st.header("Application Form")
with st.form(key="application_form"):
    form_data = {}

    if application_data:
        form_data["id"] = application_data["id"]
        form_data["name"] = st.text_input("Name", application_data["name"])
        form_data["description"] = st.text_area("Description", application_data.get("description", ""))
    else:
        form_data["name"] = st.text_input("Name")
        form_data["description"] = st.text_area("Description")

    # Submit button within the form
    submit_button = st.form_submit_button(label="Submit")

    if submit_button:
        if application_data:
            response = requests.put(f"{API_URL}/applications/{form_data['id']}", json=form_data)
            if response.status_code == 200:
                st.success("Entry updated successfully!")
            else:
                st.error("Error updating entry.")
        else:
            response = requests.post(f"{API_URL}/applications/", json=form_data)
            if response.status_code == 200:
                st.success("Entry added successfully!")
            else:
                st.error("Error adding entry.")

# Display all entries
st.header("All Entries")
response = requests.get(f"{API_URL}/applications/")
if response.status_code == 200:
    all_applications = response.json()
    for app in all_applications:
        st.write(app)
else:
    st.error("Error fetching all entries.")