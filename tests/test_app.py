import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Application
from app.schemas import ApplicationCreate

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


def test_create_application(client):
    application_data = {
        "name": "Test Application",
        "application_type": "SaaS",
        "description": "A test application",
        "architecture_type": "Monolithic",
        "install_type": "SaaS",
        "life_cycle_stage": "Operational",
        "life_cycle_stage_status": "In Use",
        "life_cycle_status": "Operational",
        "environments": ["Development", "Validation", "Production"],
        "number_of_users": "100",
        "valid_assessment": True,
        "gxp_healthcare": True,
        "gxp_data": False,
        "gxp_signature": False,
        "financial": True,
        "other_regulatory": False,
        "process_class": "Test Class",
        "organisational_unit": "Test Unit",
        "external_users": ["External User"],
        "data_classification": "Confidential",
        "personal_data": True,
        "personal_data_is_only_for_user_login_and_logging_of_user_actions": True,
        "personal_type": "Employees",
        "it_solution_owner": "Owner",
        "it_solution_manager": "Manager",
        "qa": "QA",
        "commission": True,
        "decommission_date": "2025-01-01",
        "access_mgmt_system": "AMS",
        "capabilities": "Capabilities",
        "links_to_cis": "Links",
        "it_risk_assessment": "Risk Assessment",
        "impact_assessment": "Impact Assessment",
    }
    response = client.post("/applications/", json=application_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Application"


def test_read_applications(client):
    response = client.get("/applications/")
    assert response.status_code == 200
    applications = response.json()
    assert len(applications) > 0
    assert applications[0]["name"] == "Test Application"


def test_update_application(client):
    # First create an application
    application_data = {
        "name": "Test Application",
        "application_type": "SaaS",
        "description": "A test application",
        "architecture_type": "Monolithic",
        "install_type": "SaaS",
        "life_cycle_stage": "Operational",
        "life_cycle_stage_status": "In Use",
        "life_cycle_status": "Operational",
        "environments": ["Development", "Validation", "Production"],
        "number_of_users": "100",
        "valid_assessment": True,
        "gxp_healthcare": True,
        "gxp_data": False,
        "gxp_signature": False,
        "financial": True,
        "other_regulatory": False,
        "process_class": "Test Class",
        "organisational_unit": "Test Unit",
        "external_users": ["External User"],
        "data_classification": "Confidential",
        "personal_data": True,
        "personal_data_is_only_for_user_login_and_logging_of_user_actions": True,
        "personal_type": "Employees",
        "it_solution_owner": "Owner",
        "it_solution_manager": "Manager",
        "qa": "QA",
        "commission": True,
        "decommission_date": "2025-01-01",
        "access_mgmt_system": "AMS",
        "capabilities": "Capabilities",
        "links_to_cis": "Links",
        "it_risk_assessment": "Risk Assessment",
        "impact_assessment": "Impact Assessment",
    }
    response = client.post("/applications/", json=application_data)
    assert response.status_code == 200
    app_id = response.json()["id"]

    # Update the application
    update_data = {"name": "Updated Application", "application_type": "PaaS"}
    response = client.put(f"/applications/{app_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Application"
    assert response.json()["application_type"] == "PaaS"
