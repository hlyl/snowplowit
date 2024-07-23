from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from uuid import UUID


class ApplicationBase(BaseModel):
    name: str
    application_type: str
    description: Optional[str] = None
    architecture_type: Optional[str] = None
    platform_host: Optional[str] = None
    install_type: Optional[str] = None
    life_cycle_stage: Optional[str] = None
    life_cycle_stage_status: Optional[str] = None
    life_cycle_status: Optional[str] = None
    environments: Optional[dict] = None
    number_of_users: Optional[str] = None
    valid_assessment: Optional[bool] = None
    gxp_healthcare: Optional[bool] = None
    gxp_data: Optional[bool] = None
    gxp_signature: Optional[bool] = None
    financial: Optional[bool] = None
    other_regulatory: Optional[bool] = None
    rto: Optional[str] = None
    rpo: Optional[str] = None
    wrt: Optional[str] = None
    process_class: Optional[str] = None
    organisational_unit: Optional[str] = None
    external_users: Optional[dict] = None
    data_classification: Optional[str] = None
    personal_data: Optional[bool] = None
    personal_data_is_only_for_user_login_and_logging_of_user_actions: Optional[bool] = (
        None
    )
    personal_type: Optional[str] = None
    it_solution_owner: Optional[str] = None
    it_solution_manager: Optional[str] = None
    qa: Optional[str] = None
    commission: Optional[bool] = None
    decommission_date: Optional[str] = None  # Ensure this is a string
    access_mgmt_system: Optional[str] = None
    capabilities: Optional[str] = None
    links_to_cis: Optional[str] = None
    it_risk_assessment: Optional[str] = None
    impact_assessment: Optional[str] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(ApplicationBase):
    pass


class ApplicationResponse(ApplicationBase):
    id: UUID  # Ensure this is a UUID

    class Config:
        orm_mode = True
