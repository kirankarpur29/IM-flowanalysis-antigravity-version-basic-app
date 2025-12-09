from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from backend.database import get_session
from backend.models_fixed import Machine

router = APIRouter(prefix="/machines", tags=["machines"])

@router.post("/", response_model=Machine)
def create_machine(machine: Machine, session: Session = Depends(get_session)):
    session.add(machine)
    session.commit()
    session.refresh(machine)
    return machine

@router.get("/", response_model=List[Machine])
def read_machines(
    offset: int = 0,
    limit: int = Query(default=100, le=100),
    session: Session = Depends(get_session)
):
    machines = session.exec(select(Machine).offset(offset).limit(limit)).all()
    return machines

@router.get("/{machine_id}", response_model=Machine)
def read_machine(machine_id: int, session: Session = Depends(get_session)):
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine
