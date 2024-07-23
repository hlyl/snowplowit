from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, func, Column, Integer, String, Text, Boolean, Date, JSON
from sqlalchemy.ext.declarative import declarative_base
from fpdf import FPDF
from datetime import datetime
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the current directory of the script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the config.json file
config_path = os.path.join(current_dir, "../config.json")

# Load JSON configuration
with open(config_path) as f:
    config = json.load(f)

# Database setup
Base = declarative_base()

# Helper function to sanitize field names
def sanitize_field_name(name):
    return ''.join(c if c.isalnum() else '_' for c in name).lower()

# Dynamically create the SQLAlchemy model
class DynamicModel(Base):
    __tablename__ = 'dynamic_table'
    id = Column(Integer, primary_key=True)

    # Map the fields from the JSON config to SQLAlchemy columns
    for field in config['form']['fields']:
        if field['type'] == 'group':
            for subfield in field['fields']:
                column_name = sanitize_field_name(subfield['field_name'])
                exec(f"{column_name} = Column({subfield['data_type']})")
        else:
            column_name = sanitize_field_name(field['field_name'])
            exec(f"{column_name} = Column({field['data_type']})")

# Create an SQLite database
engine = create_engine('sqlite:///dynamic_db.sqlite')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
        # Convert date fields to datetime objects and other complex types to
        # Convert date fields to datetime objects and other complex types to JSON
        for field in config["form"]["fields"]:
            field_name = field["field_name"]
            sanitized_field_name = sanitize_field_name(field_name)
            if field["type"] == "date" and form_data.get(field_name):
                form_data[sanitized_field_name] = datetime.strptime(
                    form_data[field_name], "%Y-%m-%d"
                ).date()
            elif field["type"] in ["multiselect", "group"] and form_data.get(field_name):
                form_data[sanitized_field_name] = json.dumps(form_data[field_name])
            elif isinstance(form_data.get(field_name), dict):
                form_data[sanitized_field_name] = json.dumps(form_data[field_name])
            else:
                form_data[sanitized_field_name] = form_data.get(field_name)

        # Ensure all expected fields are in form_data, with None for missing fields
        data_dict = {}
        for field in config["form"]["fields"]:
            if field["type"] == "group":
                for subfield in field["fields"]:
                    sanitized_subfield_name = sanitize_field_name(subfield["field_name"])
                    data_dict[sanitized_subfield_name] = form_data.get(sanitized_subfield_name, None)
            else:
                sanitized_field_name = sanitize_field_name(field["field_name"])
                data_dict[sanitized_field_name] = form_data.get(sanitized_field_name, None)

        # Use the correct field name for the search
        sanitized_name_field = sanitize_field_name("Name")
        print("the search field is: ", sanitized_name_field)
        # Check if the record exists
        existing_data = (
            db.query(DynamicModel)
            .filter(func.lower(getattr(DynamicModel, sanitized_name_field)) == data_dict[sanitized_name_field].lower())
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
        data = (
            db.query(DynamicModel)
            .filter(DynamicModel.name == name)
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