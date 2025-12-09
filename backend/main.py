from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from backend.api import geometry, simulation, reports, projects, materials

# Static directory for served files
os.makedirs("static", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # V2: Mock DB handles seeding internally on load
    print("🚀 V2 Backend Started (Mock Mode)")
    yield
    print("🛑 Shutting down")

app = FastAPI(lifespan=lifespan)

# CORS - Allow frontend to communicate
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
