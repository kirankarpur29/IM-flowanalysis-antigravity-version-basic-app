import os
import tempfile
import shutil
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
import trimesh
try:
    import gmsh
    GMSH_AVAILABLE = True
except OSError as e:
    # Render or environment missing libGLU
    logging.warning(f"GMSH import failed (likely missing libGLU): {e}. STEP conversion disabled.")
    GMSH_AVAILABLE = False
except ImportError as e:
    logging.warning(f"GMSH not installed: {e}. STEP conversion disabled.")
    GMSH_AVAILABLE = False

from pydantic import BaseModel
import numpy as np
import uuid

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/geometry", tags=["geometry"])

def safe_convert_step_to_stl(input_path: str, output_path: str):
    """Safely converts STEP to STL using GMSH."""
    if not GMSH_AVAILABLE:
        raise HTTPException(status_code=503, detail="STEP conversion unavailable on free cloud tier. Please export your model as .STL and upload again.")

    try:
        if not gmsh.is_initialized():
            gmsh.initialize()
        
        gmsh.clear()
        gmsh.open(input_path)
        gmsh.model.mesh.generate(2)
        gmsh.write(output_path)
    except Exception as e:
        logger.error(f"GMSH Conversion Failed: {e}")
        try:
           if gmsh.is_initialized():
                gmsh.finalize()
        except: pass
        raise HTTPException(status_code=500, detail=f"Geometry conversion failed: {str(e)}")
    finally:
        # Proper cleanup if needed, though finalize might block re-init on some setups. 
        # Keeping open is often safer in single-process, but here we finalize to be clean.
        try:
           if gmsh.is_initialized():
                gmsh.finalize()
        except: pass

@router.post("/upload")
async def upload_geometry(file: UploadFile = File(...)):
    logger.info(f"Received file upload: {file.filename}")
    
    # Max upload size: 25MB (Safety for free tier RAM)
    MAX_FILE_SIZE_MB = 25
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"File too large. Max size {MAX_FILE_SIZE_MB}MB for free tier.")

    # Use TemporaryDirectory for automatic cleanup
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, file.filename)
        
        # Save uploaded file safely
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            logger.error(f"File save error: {e}")
            raise HTTPException(status_code=500, detail="Failed to save uploaded file")
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        output_path = file_path
        
        # Conversion Logic
        if file_ext in ['.step', '.stp']:
            output_path = os.path.join(temp_dir, "converted.stl")
            safe_convert_step_to_stl(file_path, output_path)
        elif file_ext != '.stl':
            raise HTTPException(status_code=400, detail="Unsupported file format. Use .stl or .step")

        # Analysis Logic
        geometry_stats = {}
        try:
            mesh = trimesh.load(output_path, file_type='stl')
            
            if mesh.is_empty:
                 raise ValueError("Mesh is empty")

            volume_mm3 = float(mesh.volume)
            bbox_min, bbox_max = mesh.bounds
            dims = bbox_max - bbox_min
            
            projected_area_mm2 = float(dims[0] * dims[1])

            geometry_stats = {
                "volume_mm3": volume_mm3,
                "projected_area_mm2": projected_area_mm2,
                "bbox": {
                    "x": float(dims[0]),
                    "y": float(dims[1]),
                    "z": float(dims[2])
                }
            }
        except Exception as e:
            logger.error(f"Mesh analysis failed: {e}")
            geometry_stats = {"error": str(e)}

        # Persist to Static Directory
        static_dir = "static"
        os.makedirs(static_dir, exist_ok=True)
        final_filename = f"model_{uuid.uuid4().hex[:8]}.stl"
        final_path = os.path.join(static_dir, final_filename)
        
        try:
            shutil.copy2(output_path, final_path)
        except Exception as e:
            logger.error(f"Failed to move file to static: {e}")
            raise HTTPException(status_code=500, detail="File storage failed")

        logger.info(f"Upload successful: {final_filename}")
        return {
            "url": f"/static/{final_filename}",
            "filename": final_filename,
            "stats": geometry_stats
        }

class TransformInput(BaseModel):
    filename: str
    rotation_x: float = 0.0
    rotation_y: float = 0.0
    rotation_z: float = 0.0

@router.post("/transform")
def transform_geometry(input_data: TransformInput):
    static_dir = "static"
    file_path = os.path.join(static_dir, input_data.filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        mesh = trimesh.load(file_path, file_type='stl')
        
        # Apply rotations
        if input_data.rotation_x:
            mesh.apply_transform(trimesh.transformations.rotation_matrix(
                np.radians(input_data.rotation_x), [1, 0, 0]
            ))
        if input_data.rotation_y:
            mesh.apply_transform(trimesh.transformations.rotation_matrix(
                np.radians(input_data.rotation_y), [0, 1, 0]
            ))
        if input_data.rotation_z:
            mesh.apply_transform(trimesh.transformations.rotation_matrix(
                np.radians(input_data.rotation_z), [0, 0, 1]
            ))
            
        new_filename = f"rotated_{uuid.uuid4().hex[:8]}.stl"
        output_path = os.path.join(static_dir, new_filename)
        mesh.export(output_path)
        
        # Recalculate stats
        volume_mm3 = float(mesh.volume)
        bbox_min, bbox_max = mesh.bounds
        dims = bbox_max - bbox_min
        projected_area_mm2 = float(dims[0] * dims[1])

        geometry_stats = {
            "volume_mm3": volume_mm3,
            "projected_area_mm2": projected_area_mm2,
            "bbox": {
                "x": float(dims[0]),
                "y": float(dims[1]),
                "z": float(dims[2])
            }
        }

        return {
            "url": f"/static/{new_filename}",
            "filename": new_filename,
            "stats": geometry_stats
        }

    except Exception as e:
        logger.error(f"Transformation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transformation failed: {str(e)}")
