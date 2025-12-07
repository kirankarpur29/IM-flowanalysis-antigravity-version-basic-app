from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlmodel import Session, select
from backend.database import get_session
from backend.models import Project
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    material_id: Optional[int] = None
    machine_id: Optional[int] = None
    geometry_stats: Optional[dict] = None
    simulation_result: Optional[dict] = None

class ProjectRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    material_id: Optional[int] = None
    machine_id: Optional[int] = None
    geometry_stats: Optional[dict] = None
    simulation_result: Optional[dict] = None

@router.post("/", response_model=ProjectRead)
def create_project(project: ProjectCreate, session: Session = Depends(get_session)):
    db_project = Project(
        name=project.name,
        description=project.description,
        material_id=project.material_id,
        machine_id=project.machine_id,
        geometry_stats=project.geometry_stats,
        simulation_result=project.simulation_result
    )
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectRead])
def list_projects(session: Session = Depends(get_session)):
    projects = session.exec(select(Project)).all()
    return projects

@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}")
def delete_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session.delete(project)
    session.commit()
    return {"ok": True}
