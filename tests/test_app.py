import pytest
from sqlalchemy import text
from .conftest import TestingSessionLocal


def test_database_setup(client):
    session = TestingSessionLocal()
    result = session.execute(
        text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='applications';"
        )
    ).fetchall()
    assert len(result) == 1, "Applications table not created"
    session.close()


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
