from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

class MaterialBase(SQLModel):
    name: str = Field(index=True)
    manufacturer: Optional[str] = None
    type: str  # e.g., "Generic", "Specific"
    family: str # e.g. "ABS", "PP"
    melt_temp_min: float
    melt_temp_max: float
    mold_temp_min: float
    mold_temp_max: float
    viscosity_class: str # "Low", "Medium", "High"
    shrinkage_min: float
    shrinkage_max: float
    density: float
    max_flow_length_ratio: Optional[float] = None # Heuristic

class Material(MaterialBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class MachineBase(SQLModel):
    name: str = Field(index=True)
    clamp_tonnage: float
    max_shot_volume: float
    tie_bar_spacing_x: Optional[float] = None
    tie_bar_spacing_y: Optional[float] = None

class Machine(MachineBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ProjectBase(SQLModel):
    name: str
    description: Optional[str] = None
    customer_name: Optional[str] = None
    designer_name: Optional[str] = None

class Project(ProjectBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    material_id: Optional[int] = Field(default=None, foreign_key="material.id")
    machine_id: Optional[int] = Field(default=None, foreign_key="machine.id")
    
    # Geometry stats (stored as JSON or separate fields, simplified here)
    volume: Optional[float] = None
    projected_area: Optional[float] = None
    
    # Results
    estimated_fill_time: Optional[float] = None
    estimated_pressure: Optional[float] = None
    feasibility_status: Optional[str] = None # "Feasible", "Borderline", "Not Recommended"
