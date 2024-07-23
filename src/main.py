from fastapi import FastAPI
from src.routers import application
from src.database import engine, Base

app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

app.include_router(application.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
