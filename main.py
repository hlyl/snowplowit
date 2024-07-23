from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import date
from model import Base, ITApplication, SessionLocal, engine

app = FastAPI()


class ITApplicationCreate(BaseModel):
    name: str = "Default Name"
    application_type: str = "SaaS"
    description: Optional[str] = None
    architecture_type: str = "Monolithic"
    platform_host: Optional[str] = None
    install_type: str = "SaaS"
    life_cycle_stage: str = "Operational"
    life_cycle_stage_status: str = "In Use"
    life_cycle_status: str = "Operational"
    environments: List[str] = []
    number_of_users: Optional[str] = None
    it_solution_owner: Optional[str] = None
    it_solution_manager: Optional[str] = None
    qa: Optional[str] = None
    commission: bool = True
    decommission_date: Optional[str] = None
    access_mgmt_system: Optional[str] = None
    capabilities: Optional[str] = None
    links_to_cis: Optional[str] = None
    it_risk_assessment: Optional[str] = None
    impact_assessment: Optional[str] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        data = super().model_validate(obj).__dict__
        if obj.decommission_date:
            data["decommission_date"] = obj.decommission_date.isoformat()
        return cls(**data)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/applications/", response_model=ITApplicationCreate)
def create_application(application: ITApplicationCreate, db: Session = Depends(get_db)):
    application_data = application.model_dump()

    # Convert decommission_date from string to date object if it exists
    if application_data["decommission_date"]:
        application_data["decommission_date"] = date.fromisoformat(
            application_data["decommission_date"]
        )

    db_application = ITApplication(**application_data)
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return ITApplicationCreate.from_orm(db_application)


@app.get("/applications/{app_id}", response_model=ITApplicationCreate)
def read_application(app_id: int, db: Session = Depends(get_db)):
    db_application = db.query(ITApplication).filter(ITApplication.id == app_id).first()
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return ITApplicationCreate.from_orm(db_application)


@app.put("/applications/{app_id}", response_model=ITApplicationCreate)
def update_application(
    app_id: int, application: ITApplicationCreate, db: Session = Depends(get_db)
):
    db_application = db.query(ITApplication).filter(ITApplication.id == app_id).first()
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    application_data = application.dict()
    for key, value in application_data.items():
        setattr(db_application, key, value)

    # Convert decommission_date from string to date object if it exists
    if application_data["decommission_date"]:
        db_application.decommission_date = date.fromisoformat(
            application_data["decommission_date"]
        )

    db.commit()
    db.refresh(db_application)
    return ITApplicationCreate.from_orm(db_application)


@app.delete("/applications/{app_id}")
def delete_application(app_id: int, db: Session = Depends(get_db)):
    db_application = db.query(ITApplication).filter(ITApplication.id == app_id).first()
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    db.delete(db_application)
    db.commit()
    return {"detail": "Application deleted"}
