import json
import pytest
import requests
import requests_mock
import os

# Ensure the correct path for config.json
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "..", "config.json")

# Load JSON configuration
with open(config_path) as f:
    config = json.load(f)

# Sample data for testing
sample_form_data = {
    "name": "TestApp",
    "application_type": "SaaS",
    "description": "This is a test application.",
    "architecture_type": "Monolithic",
    "platform_host": "TestHost",
    "install_type": "On Premise",
    "life_cycle_stage": "Operational",
    "life_cycle_stage_status": "In Use",
    "life_cycle_status": "Active",
    "environments": ["Development", "Validation", "Production"],
    "no._of_users": "100-499",
    "regulatory_compliance": {
        "Valid Assessment": True,
        "GxP (Healthcare)": True,
        "GxP data": True,
        "GxP signature": False,
        "Financial": True,
        "Other regulatory": False,
    },
    "recovery": {"RTO": "7", "RPO": "7", "WRT": None},
    "data": {
        "Process class": None,
        "Organisational unit": "Development",
        "External users": [],
    },
    "it_solution_owner": "Owner Name",
    "it_solution_manager": "Manager Name",
    "qa": "QA Details",
    "commission": True,
    "decommission_date": None,
    "access_mgmt_system": ["System1", "System2"],
    "capabilities": "Sample capabilities",
    "links_to_cis": "Link to CI",
    "it_risk_assessment": "Risk assessment details",
    "impact_assessment": "Impact assessment details",
}


@pytest.fixture
def mock_requests(requests_mock):
    # Mock the search request
    requests_mock.get("http://127.0.0.1:8000/search/TestApp", json=sample_form_data)
    requests_mock.get(
        "http://127.0.0.1:8000/search/NonexistentApp",
        status_code=404,
        json={"detail": "Record not found"},
    )

    # Mock the submit request
    requests_mock.post(
        "http://127.0.0.1:8000/submit/",
        status_code=200,
        json={"message": "Form data submitted successfully!"},
    )

    # Mock the download request
    requests_mock.get(
        "http://127.0.0.1:8000/download/", content=b"PDF content", status_code=200
    )


def test_search_existing(mock_requests):
    response = requests.get("http://127.0.0.1:8000/search/TestApp")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestApp"


def test_search_non_existing(mock_requests):
    response = requests.get("http://127.0.0.1:8000/search/NonexistentApp")
    assert response.status_code == 404


def test_submit_form(mock_requests):
    response = requests.post("http://127.0.0.1:8000/submit/", json=sample_form_data)
    assert response.status_code == 200


def test_download_pdf(mock_requests):
    response = requests.get("http://127.0.0.1:8000/download/")
    assert response.status_code == 200
    assert response.content == b"PDF content"
