from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import date


class ApplicationCreate(BaseModel):
    name: str
    application_type: str
    description: Optional[str] = None
    architecture_type: str
    platform_host: Optional[str] = None
    install_type: str
    life_cycle_stage: str
    life_cycle_stage_status: str
    life_cycle_status: str
    environments: List[str]
    number_of_users: str
    valid_assessment: bool
    gxp_healthcare: bool
    gxp_data: bool
    gxp_signature: bool
    financial: bool
    other_regulatory: bool
    process_class: str
    organisational_unit: str
    external_users: List[str]
    data_classification: str
    personal_data: bool
    personal_data_is_only_for_user_login_and_logging_of_user_actions: bool
    personal_type: str
    it_solution_owner: str
    it_solution_manager: str
    qa: str
    commission: bool
    decommission_date: Optional[date] = None
    access_mgmt_system: str
    capabilities: str
    links_to_cis: str
    it_risk_assessment: str
    impact_assessment: str

    model_config = ConfigDict(from_attributes=True)


class ApplicationUpdate(ApplicationCreate):
    pass


class ApplicationResponse(BaseModel):
    id: str
    name: str
    application_type: str
    description: Optional[str] = None
    architecture_type: str
    platform_host: Optional[str] = None
    install_type: str
    life_cycle_stage: str
    life_cycle_stage_status: str
    life_cycle_status: str
    environments: List[str]
    number_of_users: str
    valid_assessment: bool
    gxp_healthcare: bool
    gxp_data: bool
    gxp_signature: bool
    financial: bool
    other_regulatory: bool
    process_class: str
    organisational_unit: str
    external_users: List[str]
    data_classification: str
    personal_data: bool
    personal_data_is_only_for_user_login_and_logging_of_user_actions: bool
    personal_type: str
    it_solution_owner: str
    it_solution_manager: str
    qa: str
    commission: bool
    decommission_date: Optional[date] = None
    access_mgmt_system: str
    capabilities: str
    links_to_cis: str
    it_risk_assessment: str
    impact_assessment: str

    model_config = ConfigDict(from_attributes=True)
