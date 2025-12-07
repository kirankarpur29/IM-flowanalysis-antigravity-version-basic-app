from fastapi import APIRouter, HTTPException, Body, Depends
from pydantic import BaseModel
from typing import Optional, Dict
import math
from backend.models import Material, Machine
from backend.database import get_session
from sqlmodel import Session

router = APIRouter(prefix="/simulation", tags=["simulation"])

class SimulationInput(BaseModel):
    material_id: int
    machine_id: Optional[int] = None
    geometry_stats: Dict[str, float] # volume_mm3, projected_area_mm2, bbox (x,y,z)
    flow_length_mm: Optional[float] = None # Optional override from frontend
    # Process overrides (optional)
    melt_temp: Optional[float] = None
    mold_temp: Optional[float] = None
    thickness_mm: Optional[float] = None # If not provided, estimated from Vol/Area

class SimulationResult(BaseModel):
    fill_time_s: float
    injection_pressure_mpa: float
    clamp_tonnage_tons: float
    cooling_time_s: float
    cycle_time_s: float
    shot_weight_g: float
    feasibility: str # "Feasible", "Borderline", "Not Recommended"
    warnings: list[str]
    recommendations: list[str]

def estimate_thickness(stats: Dict[str, float]) -> float:
    # Very rough estimate: Volume / Area * 2 (assuming shell)
    vol = stats.get("volume_mm3", 0)
    area = stats.get("projected_area_mm2", 1) # Avoid div by zero
    if area == 0: return 1.0
    
    thickness = vol / area
    
    # Sanity check with bbox
    bbox = stats.get("bbox", {"x": 0, "y": 0, "z": 0})
    min_dim = min(bbox["x"], bbox["y"], bbox["z"])
    
    if min_dim > 0 and thickness > min_dim:
        thickness = min_dim 
        
    return max(thickness, 0.5) # Min 0.5mm

def calculate_cooling_time(thickness_mm: float, material: Material, melt_temp: float, mold_temp: float) -> float:
    # Simplified cooling equation
    alpha = 0.08 # Thermal diffusivity (mm^2/s)
    eject_temp = material.melt_temp_min - 100 
    if eject_temp < mold_temp: eject_temp = mold_temp + 20
    
    try:
        term1 = (thickness_mm ** 2) / (math.pi ** 2 * alpha)
        term2 = math.log((4 / math.pi) * (melt_temp - mold_temp) / (eject_temp - mold_temp))
        return max(term1 * term2, 1.0)
    except:
        return 10.0 

@router.post("/run", response_model=SimulationResult)
def run_simulation(input_data: SimulationInput, session: Session = Depends(get_session)):
    # 1. Fetch Material
    material = session.get(Material, input_data.material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
        
    # 2. Determine Process Parameters
    melt_temp = input_data.melt_temp or ((material.melt_temp_min + material.melt_temp_max) / 2)
    mold_temp = input_data.mold_temp or ((material.mold_temp_min + material.mold_temp_max) / 2)
    
    # 3. Analyze Geometry
    stats = input_data.geometry_stats
    thickness = input_data.thickness_mm or estimate_thickness(stats)
    
    bbox = stats.get("bbox", {"x": 0, "y": 0, "z": 0})
    
    # Flow length estimation
    if input_data.flow_length_mm:
        flow_length = input_data.flow_length_mm
    else:
        # Fallback: Diagonal of the bounding box
        flow_length = math.sqrt(bbox["x"]**2 + bbox["y"]**2 + bbox["z"]**2)
    
    # 4. Flow Analysis (L/t Ratio)
    lt_ratio = flow_length / thickness
    max_lt = material.max_flow_length_ratio or 150 
    
    warnings = []
    recommendations = []
    feasibility = "Feasible"
    
    if lt_ratio > max_lt:
        warnings.append(f"Flow length ratio ({lt_ratio:.1f}) exceeds material limit ({max_lt}). Risk of short shot.")
        feasibility = "Not Recommended"
    elif lt_ratio > max_lt * 0.8:
        warnings.append(f"Flow length ratio ({lt_ratio:.1f}) is high. High injection pressure required.")
        feasibility = "Borderline"
        
    # 5. Pressure Estimation
    base_pressure = 40
    viscosity_factor = {"Low": 0.8, "Medium": 1.0, "High": 1.4}.get(material.viscosity_class, 1.0)
    lt_factor = lt_ratio / 100
    
    injection_pressure = base_pressure * viscosity_factor * lt_factor
    if injection_pressure > 200:
        warnings.append(f"Estimated injection pressure ({injection_pressure:.0f} MPa) is very high.")
        if feasibility != "Not Recommended": feasibility = "Borderline"

    # 6. Clamp Tonnage
    cavity_pressure = injection_pressure * 0.4 
    clamp_force_n = stats.get("projected_area_mm2", 0) * cavity_pressure
    clamp_tonnage = clamp_force_n / 9800
    clamp_tonnage *= 1.1 # Safety factor
    
    # Machine Check (Clamp Tonnage)
    if input_data.machine_id:
        machine = session.get(Machine, input_data.machine_id)
        if machine:
            if clamp_tonnage > machine.clamp_tonnage:
                warnings.append(f"Required tonnage ({clamp_tonnage:.0f} T) exceeds machine limit ({machine.clamp_tonnage} T).")
                feasibility = "Not Recommended"
            
            # Tie Bar Spacing Check
            # Assuming bbox x/y are mold dimensions. 
            # We need to ensure at least one dimension fits between tie bars.
            # Simplified check: Min mold dimension < Min tie bar spacing
            mold_x = bbox.get("x", 0)
            mold_y = bbox.get("y", 0)
            mold_min = min(mold_x, mold_y)
            
            tb_x = machine.tie_bar_spacing_x or 9999
            tb_y = machine.tie_bar_spacing_y or 9999
            tb_min = min(tb_x, tb_y)
            
            if mold_min > tb_min:
                warnings.append(f"Mold size ({mold_min:.0f} mm) may not fit between tie bars ({tb_min:.0f} mm).")
                if feasibility != "Not Recommended": feasibility = "Borderline"

    # 7. Cooling & Cycle Time
    cooling_time = calculate_cooling_time(thickness, material, melt_temp, mold_temp)
    cycle_time = cooling_time + 5 + 2 
    
    # 8. Shot Weight
    shot_weight = (stats.get("volume_mm3", 0) / 1000) * material.density
    
    # 9. Shrinkage (Display Only)
    avg_shrinkage = (material.shrinkage_min + material.shrinkage_max) / 2
    recommendations.append(f"Expected shrinkage: {material.shrinkage_min*100:.1f}% - {material.shrinkage_max*100:.1f}%. Design mold cavity accordingly.")

    return SimulationResult(
        fill_time_s=max(0.5, flow_length / 100), 
        injection_pressure_mpa=injection_pressure,
        clamp_tonnage_tons=clamp_tonnage,
        cooling_time_s=cooling_time,
        cycle_time_s=cycle_time,
        shot_weight_g=shot_weight,
        feasibility=feasibility,
        warnings=warnings,
        recommendations=recommendations
    )
