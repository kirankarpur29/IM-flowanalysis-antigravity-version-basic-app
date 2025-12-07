from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import os
from sqlmodel import Session

from backend.database import create_db_and_tables, engine
from backend.api import materials, machines, geometry, simulation, reports, projects
from backend import models, preload_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    # Auto-seed database on startup
    with Session(engine) as session:
        preload_data.create_materials(session)
        preload_data.create_machines(session)
        session.commit()
    yield

app = FastAPI(title="Mold Flow Analysis API", version="0.1.0", lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(materials.router)
app.include_router(machines.router)
app.include_router(geometry.router)
app.include_router(simulation.router)
app.include_router(reports.router)
app.include_router(projects.router)

os.makedirs("static", exist_ok=True)
# Mount static files for geometry (existing)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Mount frontend build (New)
# Ensure the path is correct relative to backend/main.py
# Assuming structure:
# /mold-flow-app
#   /backend
#   /frontend
#     /dist
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    print(f"WARNING: Frontend build not found at {frontend_dist}. Run 'npm run build' in frontend.")

# Force reload
