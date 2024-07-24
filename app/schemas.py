from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class ApplicationCreate(BaseModel):
    name: str
    application_type: Optional[str] = None
    description: Optional[str] = None
    architecture_type: Optional[str] = None
    platform_host: Optional[str] = None
    install_type: Optional[str] = None
    life_cycle_stage: Optional[str] = None
    life_cycle_stage_status: Optional[str] = None
    life_cycle_status: Optional[str] = None
    environments: List[str] = Field(default=["Development", "Validation", "Production"])
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
    external_users: List[str] = []
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
    decommission_date: Optional[date] = None
    access_mgmt_system: Optional[str] = None
    capabilities: Optional[str] = None
    links_to_cis: Optional[str] = None
    it_risk_assessment: Optional[str] = None
    impact_assessment: Optional[str] = None


class ApplicationUpdate(ApplicationCreate):
    pass


class ApplicationResponse(ApplicationCreate):
    id: str

    class Config:
        from_attributes = True
