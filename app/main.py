import logging
from fastapi import FastAPI
from app.routers import application
from app.database import engine, Base
from app.config import load_config

# Set up logging to file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

app.include_router(application.router, prefix="/applications")


@app.get("/config/")
def get_config():
    logger.info("Fetching configuration")
    config = load_config()
    logger.debug(f"Config loaded: {config}")
    return config


@app.get("/")
def read_root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Application Management API"}


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8000)
