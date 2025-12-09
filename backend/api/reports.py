from fastapi import APIRouter, HTTPException, Response, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from backend.models_fixed import Material, Machine
from backend.database import get_db
# Remove SQLModel/get_session dependencies
# from sqlmodel import Session
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except OSError:
    # GTK3 not installed
    WEASYPRINT_AVAILABLE = False
    print("WARNING: WeasyPrint (GTK3) not found. PDF generation disabled.")
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("WARNING: WeasyPrint not installed. PDF generation disabled.")

import io
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["reports"])

class ReportInput(BaseModel):
    material_id: int
    machine_id: Optional[int] = None
    geometry_stats: Dict[str, float]
    simulation_result: Dict[str, Any]
    project_name: str = "Untitled Project"
    designer_name: str = "Designer"

@router.post("/generate")
def generate_report(input_data: ReportInput, db = Depends(get_db)):
    # Fetch Data
    # Mock DB Query Logic
    mat_res = db.table("materials").select("*").eq("id", input_data.material_id).execute()
    material = mat_res.data[0] if mat_res.data else None
    
    machine = None
    if input_data.machine_id:
        mach_res = db.table("machines").select("*").eq("id", input_data.machine_id).execute()
        machine = mach_res.data[0] if mach_res.data else None
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # Generate HTML Content
    # In a real app, use Jinja2 templates. For MVP, f-strings are fine.
    
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            @page {{ size: A4; margin: 2cm; }}
            body {{ font-family: Helvetica, Arial, sans-serif; color: #333; line-height: 1.5; }}
            h1 {{ color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px; }}
            h2 {{ color: #1e40af; margin-top: 30px; }}
            .header {{ display: flex; justify-content: space-between; margin-bottom: 40px; }}
            .meta {{ font-size: 0.9em; color: #666; }}
            .section {{ margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
            th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8fafc; color: #475569; }}
            .result-card {{ background: #f1f5f9; padding: 15px; border-radius: 8px; margin-bottom: 10px; }}
            .feasibility {{ font-weight: bold; padding: 5px 10px; border-radius: 4px; display: inline-block; }}
            .feasible {{ background: #dcfce7; color: #166534; }}
            .borderline {{ background: #fef9c3; color: #854d0e; }}
            .not-recommended {{ background: #fee2e2; color: #991b1b; }}
            .warning {{ color: #b45309; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div>
                <h1>Mold Flow Analysis Report</h1>
                <div class="meta">Generated on {date_str}</div>
            </div>
        </div>

        <div class="section">
            <h2>Project Details</h2>
            <table>
                <tr><th>Project Name</th><td>{input_data.project_name}</td></tr>
                <tr><th>Designer</th><td>{input_data.designer_name}</td></tr>
                <tr><th>Material</th><td>{material['name']} ({material.get('family', 'Generic')}) - {material.get('manufacturer', 'Generic')}</td></tr>
                <tr><th>Machine</th><td>{machine['name'] if machine else "Auto-Selected"}</td></tr>
            </table>
        </div>

        <div class="section">
            <h2>Geometry Analysis</h2>
            <table>
                <tr><th>Volume</th><td>{input_data.geometry_stats.get('volume_mm3', 0)/1000:.2f} cm³</td></tr>
                <tr><th>Projected Area</th><td>{input_data.geometry_stats.get('projected_area_mm2', 0)/100:.2f} cm²</td></tr>
                <tr><th>Bounding Box</th><td>{input_data.geometry_stats.get('bbox', {}).get('x',0):.1f} x {input_data.geometry_stats.get('bbox', {}).get('y',0):.1f} x {input_data.geometry_stats.get('bbox', {}).get('z',0):.1f} mm</td></tr>
            </table>
        </div>

        <div class="section">
            <h2>Simulation Results</h2>
            <div class="result-card">
                <strong>Feasibility: </strong>
                <span class="feasibility {input_data.simulation_result.get('feasibility', '').lower().replace(' ', '-')}">
                    {input_data.simulation_result.get('feasibility', 'Unknown')}
                </span>
            </div>
            
            <table>
                <tr><th>Fill Time</th><td>{input_data.simulation_result.get('fill_time_s', 0):.2f} s</td></tr>
                <tr><th>Injection Pressure</th><td>{input_data.simulation_result.get('injection_pressure_mpa', 0):.0f} MPa</td></tr>
                <tr><th>Clamp Tonnage</th><td>{input_data.simulation_result.get('clamp_tonnage_tons', 0):.0f} Tons</td></tr>
                <tr><th>Cycle Time</th><td>{input_data.simulation_result.get('cycle_time_s', 0):.1f} s</td></tr>
                <tr><th>Shot Weight</th><td>{input_data.simulation_result.get('shot_weight_g', 0):.1f} g</td></tr>
            </table>
        </div>

        {f'<div class="section"><h2>Warnings & Risks</h2><ul>' + ''.join([f'<li class="warning">{w}</li>' for w in input_data.simulation_result.get('warnings', [])]) + '</ul></div>' if input_data.simulation_result.get('warnings') else ''}

        <div class="section">
            <h2>Recommendations</h2>
            <ul>
                <li>Review gate location to minimize flow length.</li>
                <li>Ensure adequate venting in last-to-fill areas.</li>
                <li>Verify cooling channel layout for uniform heat dissipation.</li>
            </ul>
        </div>
        
        <div style="margin-top: 50px; font-size: 0.8em; color: #999; text-align: center;">
            Disclaimer: This is a preliminary analysis based on heuristic approximations. 
            Results should be verified with detailed CAE simulation before cutting steel.
        </div>
    </body>
    </html>
    """
    
    # Generate PDF
    if not WEASYPRINT_AVAILABLE:
        raise HTTPException(status_code=503, detail="PDF generation unavailable. Server missing GTK3 libraries.")

    pdf_file = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)
    
    return Response(content=pdf_file.read(), media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=report_{datetime.now().strftime('%Y%m%d')}.pdf"})
