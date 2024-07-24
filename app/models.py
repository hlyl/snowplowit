from sqlalchemy import Column, String, Text, Boolean, JSON, Date, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid

Base = declarative_base()


class Application(Base):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    application_type = Column(String(255))
    description = Column(Text)
    architecture_type = Column(String(255))
    platform_host = Column(Text)
    install_type = Column(String(255))
    life_cycle_stage = Column(String(255))
    life_cycle_stage_status = Column(String(255))
    life_cycle_status = Column(String(255))
    environments = Column(JSON)
    number_of_users = Column(String(255))
    valid_assessment = Column(Boolean, default=False)
    gxp_healthcare = Column(Boolean, default=False)
    gxp_data = Column(Boolean, default=False)
    gxp_signature = Column(Boolean, default=False)
    financial = Column(Boolean, default=False)
    other_regulatory = Column(Boolean, default=False)
    rto = Column(String(255))
    rpo = Column(String(255))
    wrt = Column(String(255))
    process_class = Column(String(255))
    organisational_unit = Column(String(255))
    external_users = Column(JSON)
    data_classification = Column(String(255))
    personal_data = Column(Boolean, default=False)
    personal_data_is_only_for_user_login_and_logging_of_user_actions = Column(
        Boolean, default=False
    )
    personal_type = Column(String(255))
    it_solution_owner = Column(String(255))
    it_solution_manager = Column(String(255))
    qa = Column(String(255))
    commission = Column(Boolean, default=False)
    decommission_date = Column(Date)
    access_mgmt_system = Column(String(255))
    capabilities = Column(String(255))
    links_to_cis = Column(String(255))
    it_risk_assessment = Column(String(255))
    impact_assessment = Column(String(255))

    def to_dict(self):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        # Convert decommission_date to string
        if self.decommission_date:
            result["decommission_date"] = self.decommission_date.isoformat()
        return result
