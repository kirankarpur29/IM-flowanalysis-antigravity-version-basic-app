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
        # Retry import in case it was a transient load issue (Docker should have it)
        try:
            import gmsh
            GMSH_AVAILABLE = True
        except:
             raise HTTPException(status_code=503, detail="Server missing GMSH libraries. If on Free Tier, switch to Docker Runtime.")

    try:
        if not gmsh.is_initialized():
            gmsh.initialize()
        
        gmsh.clear()
        
        # Optimize for Low Memory / Render Free Tier
        gmsh.option.setNumber("General.NumThreads", 1)  # Avoid thread overhead
        gmsh.option.setNumber("Mesh.Algorithm", 6)      # Frontal-Delaunay 2D (Usually efficient)
        gmsh.option.setNumber("General.Terminal", 1)    # Log output
        
        gmsh.open(input_path)
        gmsh.model.mesh.generate(2)
        
        # Write Binary STL (Faster, smaller)
        gmsh.option.setNumber("Mesh.Binary", 1)
        gmsh.write(output_path)
    except Exception as e:
        logger.error(f"GMSH Conversion Failed: {e}")
        try:
           if gmsh.is_initialized():
                gmsh.finalize()
        except: pass
        # Provide specific user feedback
        raise HTTPException(status_code=422, detail=f"Geometry conversion failed (Likely Memory Limit). Try a smaller file or STL. Internal: {str(e)}")
    finally:
        # Proper cleanup if needed, though finalize might block re-init on some setups. 
        # Keeping open is often safer in single-process, but here we finalize to be clean.
        try:
           if gmsh.is_initialized():
                gmsh.finalize()
        except: pass

@router.post("/upload")
async def upload_geometry(
    file: UploadFile = File(...),
    project_id: str = Form(None), # Optional for now to support legacy/wizard
    db = Depends(get_db)
):
    logger.info(f"Received file upload: {file.filename} for Project: {project_id}")
    
    # Max upload size: 15MB
    MAX_FILE_SIZE_MB = 15
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(status_code=413, detail=f"File too large ({file_size/1024/1024:.1f}MB). Max size {MAX_FILE_SIZE_MB}MB.")

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
            raise HTTPException(status_code=422, detail=f"Geometry Analysis Failed: {str(e)}")

        # Persist to Static Directory (Mocking S3)
        static_dir = "static"
        os.makedirs(static_dir, exist_ok=True)
        final_filename = f"model_{uuid.uuid4().hex[:8]}.stl"
        final_path = os.path.join(static_dir, final_filename)
        
        try:
            shutil.copy2(output_path, final_path)
        except Exception as e:
            logger.error(f"Failed to move file to static: {e}")
            raise HTTPException(status_code=500, detail="File storage failed")
        
        file_url = f"/static/{final_filename}"

        # DB Insertion (If Project ID provided)
        part_id = str(uuid.uuid4())
        if project_id:
            logger.info(f"Linking geometry to Project {project_id}")
            part_record = {
                "id": part_id,
                "project_id": project_id,
                "file_url": file_url,
                "file_name": file.filename,
                "volume": geometry_stats["volume_mm3"],
                "projected_area": geometry_stats["projected_area_mm2"],
                "bbox_x": geometry_stats["bbox"]["x"],
                "bbox_y": geometry_stats["bbox"]["y"],
                "bbox_z": geometry_stats["bbox"]["z"]
            }
            db.table("parts").insert(part_record).execute()

        logger.info(f"Upload successful: {final_filename}")
        return {
            "url": file_url,
            "filename": final_filename,
            "part_id": part_id,
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
