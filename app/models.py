from sqlalchemy import Column, String, Text, Boolean, JSON, Date
from sqlalchemy.dialects.postgresql import (
    UUID,
)  # If using PostgreSQL, adjust accordingly for SQLite
from sqlalchemy.orm import declarative_base
import uuid
from datetime import date

Base = declarative_base()


class Application(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    application_type = Column(String(255), nullable=False)
    description = Column(Text)
    architecture_type = Column(String(255))
    platform_host = Column(Text)
    install_type = Column(String(255))
    life_cycle_stage = Column(String(255))
    life_cycle_stage_status = Column(String(255))
    life_cycle_status = Column(String(255))
    environments = Column(JSON)
    number_of_users = Column(String(255))
    valid_assessment = Column(Boolean)
    gxp_healthcare = Column(Boolean)
    gxp_data = Column(Boolean)
    gxp_signature = Column(Boolean)
    financial = Column(Boolean)
    other_regulatory = Column(Boolean)
    rto = Column(String(255))
    rpo = Column(String(255))
    wrt = Column(String(255))
    process_class = Column(String(255))
    organisational_unit = Column(String(255))
    external_users = Column(JSON)
    data_classification = Column(String(255))
    personal_data = Column(Boolean)
    personal_data_is_only_for_user_login_and_logging_of_user_actions = Column(Boolean)
    personal_type = Column(String(255))
    it_solution_owner = Column(String(255))
    it_solution_manager = Column(String(255))
    qa = Column(String(255))
    commission = Column(Boolean)
    decommission_date = Column(Date)
    access_mgmt_system = Column(String(255))
    capabilities = Column(String(255))
    links_to_cis = Column(String(255))
    it_risk_assessment = Column(String(255))
    impact_assessment = Column(String(255))

    def to_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        if isinstance(result["decommission_date"], date):
            result["decommission_date"] = result["decommission_date"].isoformat()
        result["id"] = str(result["id"])  # Ensure id is a string
        return result
