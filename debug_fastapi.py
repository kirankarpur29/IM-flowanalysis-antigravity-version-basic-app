from fastapi import FastAPI
from backend.models import Material, Project
from backend.database import create_db_and_tables
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/material", response_model=Material)
def create_material(material: Material):
    return material

@app.post("/project", response_model=Project)
def create_project(project: Project):
    return project

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
