from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.sqlite import JSON

# SQLite database URL
DATABASE_URL = "sqlite:///./form_data.db"

# Create the database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative models
Base = declarative_base()


class FormData(Base):
    __tablename__ = "form_data"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), default="Default Name")
    application_type = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    architecture_type = Column(String(255), nullable=True)
    platform_host = Column(String(255), nullable=True)
    install_type = Column(String(255), nullable=True)
    life_cycle_stage = Column(String(255), nullable=True)
    life_cycle_stage_status = Column(String(255), nullable=True)
    life_cycle_status = Column(String(255), nullable=True)
    no_of_users = Column(String(255), nullable=True)
    it_solution_owner = Column(String(255), nullable=True)
    it_solution_manager = Column(String(255), nullable=True)
    qa = Column(String(255), nullable=True)
    commission = Column(Boolean, default=True)
    decommission_date = Column(Date, nullable=True)
    capabilities = Column(Text, nullable=True)
    links_to_cis = Column(Text, nullable=True)
    it_risk_assessment = Column(Text, nullable=True)
    impact_assessment = Column(Text, nullable=True)
    regulatory_compliance = Column(JSON, nullable=True)
    recovery = Column(JSON, nullable=True)
    usage = Column(JSON, nullable=True)
    data = Column(JSON, nullable=True)
    access_mgmt_system = Column(JSON, nullable=True)


# Create all tables in the database
Base.metadata.create_all(bind=engine)
