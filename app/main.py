from fastapi import FastAPI
from app.routers import application
from app.database import engine, Base

app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

app.include_router(application.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
