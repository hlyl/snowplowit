import os
import pytest
import json
from fastapi.testclient import TestClient
from src.main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base, DynamicModel

# Ensure the correct path for config.json
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, "..", "config.json")

# Load JSON configuration
with open(config_path) as f:
    config = json.load(f)

# Create a new SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency to use the testing database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

# Create the database tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

# Sample form data
form_data = {
    "Name": "TestApp",
    "Application Type": "SaaS",
    "Description": "This is a test application.",
    "Architecture Type": "Monolithic",
    "Platform Host": "TestHost",
    "Install Type": "On Premise",
    "Life Cycle Stage": "Operational",
    "Life Cycle Stage Status": "In Use",
    "Life Cycle Status": "Active",
    "Environments": ["Development", "Validation", "Production"],
    "No. of Users": "100",
    "Regulatory Compliance": {
        "Valid Assessment": True,
        "GxP (Healthcare)": True,
        "GxP data": True,
        "GxP signature": False,
        "Financial": True,
        "Other regulatory": False,
    },
    "Recovery": {"RTO": "7", "RPO": "7", "WRT": None},
    "Usage": {
        "Process class": None,
        "Organisational unit": "Development",
        "External users": [],
    },
    "Data": {
        "Data classification": "Internal use",
        "Personal Data": True,
        "Personal Data is only for User login and logging of User actions?": True,
        "Personal type": "Employees",
    },
    "IT Solution Owner": "Owner Name",
    "IT Solution Manager": "Manager Name",
    "QA": "QA Details",
    "Commission": True,
    "Decommission Date": "2024-01-01",
    "Access Mgmt System": {"System1": "System1 details", "System2": "System2 details"},
    "Capabilities": "Sample capabilities",
    "Links to CIs": "Link to CI",
    "IT Risk Assessment": "Risk assessment details",
    "Impact Assessment": "Impact assessment details",
}


def test_submit_form():
    response = client.post("/submit/", json=form_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Form data submitted successfully!"}


def test_search_form_data():
    response = client.get("/search/TestApp")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TestApp"
    assert data["application_type"] == "SaaS"


def test_download_pdf():
    response = client.get("/download/")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_update_form_data():
    updated_data = form_data.copy()
    updated_data["Description"] = "This is an updated test application."
    response = client.post("/submit/", json=updated_data)
    assert response.status_code == 200
    assert response.json() == {"message": "Form data submitted successfully!"}

    search_response = client.get("/search/TestApp")
    assert search_response.status_code == 200
    data = search_response.json()
    assert data["description"] == "This is an updated test application."


def test_search_nonexistent_form_data():
    response = client.get("/search/NonexistentApp")
    assert response.status_code == 404
    assert response.json() == {"detail": "Record not found"}
