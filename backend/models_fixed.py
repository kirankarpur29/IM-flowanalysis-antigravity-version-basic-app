from typing import Optional
from sqlmodel import Field, SQLModel

class Material(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    type: str
    family: str
    manufacturer: str = "Generic"
    
    # Properties
    melt_temp_min: float
    melt_temp_max: float
    mold_temp_min: float
    mold_temp_max: float
    viscosity_class: str
    shrinkage_min: float
    shrinkage_max: float
    density: float
    max_flow_length_ratio: float

class Machine(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    clamp_tonnage: float
    max_shot_volume: float
    tie_bar_spacing_x: float
    tie_bar_spacing_y: float
