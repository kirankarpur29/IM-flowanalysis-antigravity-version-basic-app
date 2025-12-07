from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from backend.database import get_session
from backend.models import Material

router = APIRouter(prefix="/materials", tags=["materials"])

@router.post("/", response_model=Material)
def create_material(material: Material, session: Session = Depends(get_session)):
    session.add(material)
    session.commit()
    session.refresh(material)
    return material

@router.get("/", response_model=List[Material])
def read_materials(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    materials = session.exec(select(Material).offset(offset).limit(limit)).all()
    return materials

@router.get("/{material_id}", response_model=Material)
def read_material(material_id: int, session: Session = Depends(get_session)):
    material = session.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    return material
