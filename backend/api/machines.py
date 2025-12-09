from fastapi import APIRouter, Depends, HTTPException, Query
# from sqlmodel import Session, select
from backend.database import get_db
from backend.models_fixed import Machine

router = APIRouter(prefix="/machines", tags=["machines"])

@router.post("/", response_model=Machine)
def create_machine(machine: Machine, db = Depends(get_db)):
    # Mock DB: Insert
    res = db.table("machines").insert(machine.dict()).execute()
    return res.data[0]

@router.get("/", response_model=List[Machine])
def read_machines(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    db = Depends(get_db)
):
    # Mock DB: Select All
    res = db.table("machines").select("*").execute()
    machines = res.data
    # Manual pagination for mock
    return machines[offset : offset + limit]

@router.get("/{machine_id}", response_model=Machine)
def read_machine(machine_id: str, db = Depends(get_db)):
    # Mock DB: Select One
    # Note: Machine ID in mock might be int or str, but usually str UUID
    # If the user asks for int, adjust verification.
    res = db.table("machines").select("*").eq("id", machine_id).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="Machine not found")
    return res.data[0]
