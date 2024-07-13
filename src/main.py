from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from models import DynamicModel, SessionLocal
from fpdf import FPDF
from datetime import datetime
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import os

# Get the directory of the current script
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to the config file
config_path = os.path.join(base_dir, "config.json")

# Load JSON configuration
with open(config_path) as f:
    # Load your configuration here
    config = json.load(f)

app = FastAPI()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Form Data", 0, 1, "C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

    def add_multicell_text(self, key, text, original_text=None):
        if original_text is not None and text != original_text:
            self.set_text_color(255, 0, 0)  # Red color for updated text
            self.multi_cell(0, 10, f"{key}: {text}")
            self.set_text_color(0, 0, 0)  # Black color for original text
            self.multi_cell(0, 10, f"{key}: {original_text}")
        else:
            self.multi_cell(0, 10, f"{key}: {text}")

    def check_page_overflow(self, height_needed):
        if self.get_y() + height_needed > self.page_break_trigger:
            self.add_page()


def generate_pdf(data, original_data):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for key, value in data.items():
        original_value = original_data.get(key)
        if isinstance(value, dict):
            pdf.multi_cell(0, 10, f"{key}:", ln=True)
            for sub_key, sub_value in value.items():
                sub_original_value = (
                    json.loads(original_value).get(sub_key) if original_value else None
                )
                pdf.check_page_overflow(10)
                pdf.add_multicell_text(f"  {sub_key}", sub_value, sub_original_value)
        else:
            pdf.check_page_overflow(10)
            pdf.add_multicell_text(key, value, original_value)

    pdf.output("output.pdf")


@app.post("/submit/")
async def submit_form(form_data: dict, db: Session = Depends(get_db)):
    logger.info("Received form submission")
    try:
        # Convert date fields to datetime objects and other complex types to JSON
        for field in config["form"]["fields"]:
            field_name = field["name"]
            if field["type"] == "date" and form_data.get(field_name):
                form_data[field_name] = datetime.strptime(
                    form_data[field_name], "%Y-%m-%d"
                ).date()
            elif field["type"] in ["multiselect", "group"] and form_data.get(
                field_name
            ):
                form_data[field_name] = json.dumps(form_data[field_name])
            elif isinstance(form_data.get(field_name), dict):
                form_data[field_name] = json.dumps(form_data[field_name])

        # Ensure all expected fields are in form_data, with None for missing fields
        data_dict = {
            field["name"].replace(" ", "_").lower(): form_data.get(field["name"], None)
            for field in config["form"]["fields"]
        }

        # Check if the record exists
        existing_data = (
            db.query(DynamicModel)
            .filter(func.lower(DynamicModel.name) == data_dict["name"].lower())
            .first()
        )
        if existing_data:
            original_data = {
                col.name: getattr(existing_data, col.name)
                for col in DynamicModel.__table__.columns
            }
            for key, value in data_dict.items():
                setattr(existing_data, key, value)
            db.commit()
            db.refresh(existing_data)
            logger.info("Form data updated successfully")
        else:
            original_data = {key: None for key in data_dict.keys()}
            data = DynamicModel(**data_dict)
            db.add(data)
            db.commit()
            db.refresh(data)
            logger.info("Form data submitted successfully")

        # Generate PDF with comparison
        generate_pdf(data_dict, original_data)

        return {"message": "Form data submitted successfully!"}
    except Exception as e:
        db.rollback()
        logger.error("Error submitting form data: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/")
async def download_pdf():
    logger.info("Download PDF request received")
    file_path = "output.pdf"
    return FileResponse(
        path=file_path, filename="output.pdf", media_type="application/pdf"
    )


@app.get("/search/{name}")
async def search_form_data(name: str, db: Session = Depends(get_db)):
    logger.info("Search request received for name: %s", name)
    try:
        # Case-insensitive search
        data = (
            db.query(DynamicModel)
            .filter(func.lower(DynamicModel.name) == name.lower())
            .first()
        )
        if not data:
            raise HTTPException(status_code=404, detail="Record not found")

        result = {
            col.name: getattr(data, col.name) for col in DynamicModel.__table__.columns
        }
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error searching form data: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
