from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from backend.database import get_db
from pydantic import BaseModel
from datetime import datetime
import uuid

# Mock Auth (Since we are in Mock Mode)
def get_current_user():
    return "mock-user-id-123"

router = APIRouter(prefix="/projects", tags=["projects"])

# API Models
class ProjectCreate(BaseModel):
    name: str

class ProjectRead(BaseModel):
    id: str
    user_id: str
    name: str
    status: str
    created_at: str

@router.post("/", response_model=ProjectRead)
def create_project(project: ProjectCreate, db = Depends(get_db), user_id: str = Depends(get_current_user)):
    # Create Record
    new_project = {
        "user_id": user_id,
        "name": project.name,
        "status": "draft"
    }
    
    # Insert via Client (Supabase Style)
    response = db.table("projects").insert(new_project).execute()
    
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=f"DB Error: {response.error}")
        
    return response.data[0]

@router.get("/", response_model=List[ProjectRead])
def list_projects(db = Depends(get_db), user_id: str = Depends(get_current_user)):
    # Select via Client (Supabase Style)
    response = db.table("projects").select("*").eq("user_id", user_id).execute()
    
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=response.error)
        
    return response.data

@router.get("/{project_id}", response_model=dict)
def get_project(project_id: str, db = Depends(get_db)):
    # 1. Get Project
    p_res = db.table("projects").select("*").eq("id", project_id).execute()
    if not p_res.data:
        raise HTTPException(status_code=404, detail="Project not found")
    project = p_res.data[0]

    # 2. Get Parts (Geometry)
    parts_res = db.table("parts").select("*").eq("project_id", project_id).execute()
    project["parts"] = parts_res.data if parts_res.data else []
    
    # 3. Get Simulations
    sim_res = db.table("simulations").select("*").eq("project_id", project_id).execute()
    # Sort by created_at desc to get latest
    sims = sorted(sim_res.data, key=lambda x: x["created_at"], reverse=True) if sim_res.data else []
    project["simulation_result"] = sims[0]["result"] if sims else None

    return project

@router.delete("/{project_id}")
def delete_project(project_id: str, db = Depends(get_db)):
    # Note: Mock DB doesn't support delete yet in client, but API exists
    return {"message": "Project deleted (Mock)"}

