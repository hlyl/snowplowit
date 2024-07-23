import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
from datetime import date
from uuid import UUID  # Add this import

from app.database import get_db
from app.models import Application
from app.schemas import ApplicationCreate, ApplicationUpdate, ApplicationResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ApplicationResponse)
def create_application(application: ApplicationCreate, db: Session = Depends(get_db)):
    try:
        logger.info("Creating new application")
        application_data = application.dict()

        # Convert decommission_date to date object if present
        if application_data.get("decommission_date"):
            application_data["decommission_date"] = date.fromisoformat(
                application_data["decommission_date"]
            )

        logger.debug(f"Application data: {application_data}")
        new_application = Application(**application_data)
        db.add(new_application)
        db.commit()
        db.refresh(new_application)
        logger.info("New application created")
        return new_application.to_dict()
    except Exception as e:
        logger.error(f"Error creating application: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/", response_model=List[ApplicationResponse])
def read_applications(name: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        logger.info(f"Reading applications with name filter: {name}")
        if name:
            applications = (
                db.query(Application).filter(Application.name.ilike(f"%{name}%")).all()
            )
        else:
            applications = db.query(Application).all()
        logger.debug(f"Applications found: {applications}")
        return [app.to_dict() for app in applications]
    except Exception as e:
        logger.error(f"Error reading applications: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.put("/{app_id}", response_model=ApplicationResponse)
def update_application(
    app_id: UUID, application: ApplicationUpdate, db: Session = Depends(get_db)
):
    try:
        logger.info(f"Updating application with ID: {app_id}")
        existing_application = (
            db.query(Application).filter(Application.id == app_id).first()
        )
        if not existing_application:
            logger.error(f"Application with ID {app_id} not found")
            raise HTTPException(status_code=404, detail="Application not found")

        update_data = application.dict()

        # Convert decommission_date to date object if present
        if update_data.get("decommission_date"):
            update_data["decommission_date"] = date.fromisoformat(
                update_data["decommission_date"]
            )

        for key, value in update_data.items():
            setattr(existing_application, key, value)

        db.commit()
        db.refresh(existing_application)
        logger.info(f"Application with ID {app_id} updated")
        return existing_application.to_dict()
    except Exception as e:
        logger.error(f"Error updating application: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/pdf/{app_id}", response_class=FileResponse)
def generate_pdf(app_id: UUID, db: Session = Depends(get_db)):
    try:
        logger.info(f"Generating PDF for application with ID: {app_id}")
        application = db.query(Application).filter(Application.id == app_id).first()
        if not application:
            logger.error(f"Application with ID {app_id} not found")
            raise HTTPException(status_code=404, detail="Application not found")

        # Create a PDF file
        file_path = f"/tmp/{app_id}.pdf"
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        y = height - 50
        c.drawString(100, y, f"Application ID: {application.id}")
        y -= 30
        for field, value in application.to_dict().items():
            if field != "_sa_instance_state":
                c.drawString(100, y, f"{field}: {value}")
                y -= 30

        c.save()

        logger.info(f"PDF generated for application with ID: {app_id}")
        return FileResponse(
            file_path, filename=f"{app_id}.pdf", media_type="application/pdf"
        )
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")