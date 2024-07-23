from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db, engine
from app.model import Application, Base
from pydantic import BaseModel, create_model

# Create the database tables if they do not exist
Base.metadata.create_all(bind=engine)

# Dynamically create a Pydantic model based on the SQLAlchemy model
def create_dynamic_pydantic_model(sqlalchemy_model):
    fields = {column.name: (column.type.python_type, ...) for column in sqlalchemy_model.__table__.columns}
    return create_model(sqlalchemy_model.__name__, **fields)

DynamicPydanticModel = create_dynamic_pydantic_model(Application)

router = APIRouter()

@router.post("/applications/", response_model=DynamicPydanticModel)
def create_application(
    application: DynamicPydanticModel, db: Session = Depends(get_db)
):
    application_data = application.dict()
    new_application = Application(**application_data)
    db.add(new_application)
    db.commit()
    db.refresh(new_application)
    return new_application

@router.get("/applications/", response_model=List[DynamicPydanticModel])
def read_applications(name: Optional[str] = None, db: Session = Depends(get_db)):
    if name:
        applications = db.query(Application).filter(Application.name.ilike(f"%{name}%")).all()
    else:
        applications = db.query(Application).all()
    return applications

@router.put("/applications/{app_id}", response_model=DynamicPydanticModel)
def update_application(
    app_id: str, application: DynamicPydanticModel, db: Session = Depends(get_db)
):
    existing_application = db.query(Application).filter(Application.id == app_id).first()
    if not existing_application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    for key, value in application.dict().items():
        setattr(existing_application, key, value)
    
    db.commit()
    db.refresh(existing_application)
    return existing_application