from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, List
import math
import uuid
import datetime
from backend.database import get_db

router = APIRouter(prefix="/simulation", tags=["simulation"])

class SimulationRequest(BaseModel):
    project_id: str
    material_id: Optional[str] = None # Optional override if not in project

class SimulationResult(BaseModel):
    fill_time_s: float
    injection_pressure_mpa: float
    clamp_tonnage_tons: float
    cooling_time_s: float
    cycle_time_s: float
    shot_weight_g: float
    feasibility: str
    warnings: List[str]
    recommendations: List[str]

def estimate_thickness(vol, area):
    if area == 0: return 1.0
    thickness = vol / area
    return max(thickness, 0.5)

def calculate_cooling_time(thickness_mm, melt_temp, mold_temp, eject_temp, alpha=0.08):
    try:
        term1 = (thickness_mm ** 2) / (math.pi ** 2 * alpha)
        if (eject_temp - mold_temp) == 0: return 10.0
        ratio = (4 / math.pi) * (melt_temp - mold_temp) / (eject_temp - mold_temp)
        if ratio <= 0: return 1.0
        term2 = math.log(ratio)
        return max(term1 * term2, 1.0)
    except:
        return 10.0

@router.post("/run", response_model=SimulationResult)
def run_simulation(input_data: SimulationRequest, db = Depends(get_db)):
    # 1. Fetch Project & Part
    project_res = db.table("projects").select("*").eq("id", input_data.project_id).execute()
    if not project_res.data:
        raise HTTPException(status_code=404, detail="Project not found")
    project = project_res.data[0]

    parts_res = db.table("parts").select("*").eq("project_id", input_data.project_id).execute()
    if not parts_res.data:
        raise HTTPException(status_code=400, detail="Project has no geometry/part uploaded.")
    part = parts_res.data[0] # Assume one part for now

    # 2. Fetch Material
    mat_id = input_data.material_id or project.get("material_id")
    if not mat_id:
        raise HTTPException(status_code=400, detail="Material not selected for project.")
    
    mat_res = db.table("materials").select("*").eq("id", mat_id).execute()
    if not mat_res.data:
         raise HTTPException(status_code=404, detail="Material not found in DB.")
    material = mat_res.data[0]

    # 3. Prepare Physics Data
    vol = float(part.get("volume", 0))
    area = float(part.get("projected_area", 1))
    bbox_x = float(part.get("bbox_x", 0))
    bbox_y = float(part.get("bbox_y", 0))
    bbox_z = float(part.get("bbox_z", 0))

    # Material Props (Handle missing gracefully with defaults)
    melt_temp = float(material.get("melt_temp_c", 230))
    mold_temp = float(material.get("mold_temp_c", 50))
    density = float(material.get("density_g_cm3", 1.0))
    shrinkage = float(material.get("shrinkage", 0.01))

    # 4. Run Heuristics
    thickness = estimate_thickness(vol, area)
    
    # Flow Length (Diagonal of bbox)
    flow_length = math.sqrt(bbox_x**2 + bbox_y**2 + bbox_z**2)
    
    # L/t Ratio
    lt_ratio = flow_length / thickness
    max_lt = 200 # Generic limit
    
    warnings = []
    feasibility = "Feasible"
    
    if lt_ratio > max_lt:
        warnings.append(f"High Flow/Thickness ratio ({lt_ratio:.1f}). Risk of short shot.")
        feasibility = "Not Recommended"
    
    # Pressure
    viscosity_factor = 1.0 # Placeholder
    pressure_mpa = 40 * viscosity_factor * (lt_ratio / 100)
    if pressure_mpa > 180:
        warnings.append("High injection pressure required.")
        feasibility = "Borderline"

    # Clamp Force
    cavity_pressure = pressure_mpa * 0.5 
    clamp_force_n = area * cavity_pressure
    clamp_tonnage = clamp_force_n / 9800 * 1.1

    # Cooling
    eject_temp = melt_temp - 100 # Approx
    cooling_time = calculate_cooling_time(thickness, melt_temp, mold_temp, eject_temp)
    cycle_time = cooling_time + 5

    # Shot Weight
    shot_weight = (vol / 1000) * density

    result_data = {
        "fill_time_s": round(max(0.5, flow_length / 100), 2),
        "injection_pressure_mpa": round(pressure_mpa, 1),
        "clamp_tonnage_tons": round(clamp_tonnage, 1),
        "cooling_time_s": round(cooling_time, 1),
        "cycle_time_s": round(cycle_time, 1),
        "shot_weight_g": round(shot_weight, 1),
        "feasibility": feasibility,
        "warnings": warnings,
        "recommendations": [f"Expected shrinkage: ~{shrinkage*100:.1f}%"]
    }

    # 5. Save Result
    sim_record = {
        "id": str(uuid.uuid4()),
        "project_id": input_data.project_id,
        "created_at": datetime.datetime.now().isoformat(),
        "result": result_data
    }
    db.table("simulations").insert(sim_record).execute()

    return result_data

