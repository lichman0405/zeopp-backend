# Pore Size Distribution API Endpoint
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.2.0

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional
from app.utils.file import save_uploaded_file, compute_cache_key, get_cache_path
from app.core.runner import ZeoRunner
from app.core import config
from app.utils.logger import logger
from fastapi.responses import FileResponse

router = APIRouter()
runner = ZeoRunner()

@router.post(
    "/api/pore_size_dist/download", 
    response_class=FileResponse, 
    summary="Calculate and Download Pore Size Distribution File",
    tags=["Analysis"]
)
async def download_pore_size_dist(
    structure_file: UploadFile = File(..., description="A .cif, .cssr, .v1, or .arc file."),
    probe_radius: float = Form(1.21, description="Radius of the probe for MC sampling. Must be <= chan_radius."),
    chan_radius: Optional[float] = Form(None, description="Radius for accessibility check. Defaults to probe_radius."),
    samples: int = Form(50000, description="Number of Monte Carlo samples per unit cell for integration."),
    ha: bool = Form(True, description="Enable high accuracy mode."),
):
    """
    Calculates the pore size distribution and returns the resulting .psd_histo file for download.
    Corresponds to the `-psd` flag in Zeo++.
    """
    task_name = "psd_download"
    logger.info(f"[{task_name}] Received new request.")

    effective_chan_radius = chan_radius if chan_radius is not None else probe_radius
    if probe_radius > effective_chan_radius:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid radii: probe_radius ({probe_radius}) cannot be greater than chan_radius ({effective_chan_radius})."
        )

    input_path = save_uploaded_file(structure_file, prefix=task_name)
    
    zeo_args = [
        "-psd",
        str(effective_chan_radius),
        str(probe_radius),
        str(samples)
    ]
    if ha:
        zeo_args.insert(0, "-ha")
        
    final_runner_args = zeo_args + [input_path.name]
    
    cache_key = compute_cache_key(input_path, final_runner_args, task_name)
    cache_path = get_cache_path(cache_key)
    final_output_filename = f"{input_path.stem}.psd_histo"
    final_file_path = cache_path / final_output_filename

    if config.ENABLE_CACHE and final_file_path.exists():
        logger.info(f"[{task_name}] Cache hit. Returning file: {final_file_path}")
        return FileResponse(path=final_file_path, media_type='text/plain', filename=f"{structure_file.filename}.psd_histo")

    logger.info(f"[{task_name}] Cache miss. Running Zeo++...")

    result = runner.run_command(
        structure_file=input_path,
        zeo_args=final_runner_args,
        output_files=[final_output_filename],
        extra_identifier=task_name
    )

    if not result["success"] or not final_file_path.exists():
        stderr_content = result.get("stderr", "No stderr captured, command may have failed silently.")
        error_msg = f"Zeo++ command failed or did not generate the output file '{final_output_filename}'."
        logger.display_error_panel(f"{task_name} Failed", f"{error_msg}\n\n{stderr_content}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": error_msg, "stderr": stderr_content}
        )
    
    logger.success(f"[{task_name}] Task complete. Sending file for download: {final_file_path}")

    return FileResponse(
        path=final_file_path, 
        media_type='text/plain', 
        filename=f"{structure_file.filename}.psd_histo" 
    )