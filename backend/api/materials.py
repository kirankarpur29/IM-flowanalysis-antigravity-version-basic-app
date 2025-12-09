from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from backend.database import get_db

router = APIRouter(prefix="/materials", tags=["materials"])

class MaterialRead(BaseModel):
    id: str
    name: str
    density_g_cm3: float
    melt_temp_c: float
    mold_temp_c: float
    shrinkage: float

@router.get("/", response_model=List[MaterialRead])
def list_materials(db = Depends(get_db)):
    # Simulating SELECT * FROM materials
    response = db.table("materials").select("*").execute()
    
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=response.error)
        
    return response.data
