from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.model import Application
from src.utils.dynamic_model import DynamicPydanticModel

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
def read_applications(db: Session = Depends(get_db)):
    applications = db.query(Application).all()
    return applications
