# Pore Size Distribution API Endpoint
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.2.0


# /app/api/pore_size_dist.py (Temporary Debugging Version)

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional
from app.utils.file import save_uploaded_file
from app.core.runner import ZeoRunner
from app.utils.logger import logger
from fastapi.responses import PlainTextResponse

router = APIRouter()
runner = ZeoRunner()

@router.post(
    "/api/pore_size_dist",
    summary="[DEBUG] Calculate Pore Size Distribution (psd)",
    tags=["Analysis"]
)
async def compute_pore_size_dist(
    structure_file: UploadFile = File(..., description="A .cif, .cssr, .v1, or .arc file."),
    probe_radius: float = Form(1.21, description="Radius of the probe for MC sampling. Must be <= chan_radius."),
    chan_radius: Optional[float] = Form(None, description="Radius for accessibility check. Defaults to probe_radius."),
    samples: int = Form(50000, description="Number of Monte Carlo samples per unit cell for integration."),
    ha: bool = Form(True, description="Enable high accuracy mode."),
):
    task_name = "pore_size_dist_debug"
    logger.info(f"[{task_name}] Received new request.")

    effective_chan_radius = chan_radius if chan_radius is not None else probe_radius
    if probe_radius > effective_chan_radius:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid radii: probe_radius ({probe_radius}) cannot be greater than chan_radius ({effective_chan_radius})."
        )

    input_path = save_uploaded_file(structure_file, prefix=task_name)

    base_output_filename = f"{input_path.stem}.psd"
    
    zeo_args = [
        "-psd",
        str(effective_chan_radius),
        str(probe_radius),
        str(samples),
        base_output_filename
    ]
    if ha:
        zeo_args.insert(0, "-ha")

    final_runner_args = zeo_args + [input_path.name]
    logger.info(f"[{task_name}] Running Zeo++ with args: {' '.join(final_runner_args)}")

    result = runner.run_command(
        structure_file=input_path,
        zeo_args=final_runner_args,
        output_files=[], 
        extra_identifier=task_name
    )


    stdout_content = result.get("stdout", "No stdout captured.")
    stderr_content = result.get("stderr", "No stderr captured.")

    response_text = (
        "--- ZEO++ STDOUT ---\n"
        f"{stdout_content}\n"
        "--- END OF STDOUT ---\n\n"
        "--- ZEO++ STDERR ---\n"
        f"{stderr_content}\n"
        "--- END OF STDERR ---\n\n"
        f"Exit Code: {result.get('exit_code', 'N/A')}\n"
        f"Success Flag: {result.get('success', 'N/A')}"
    )
    
    logger.info(f"[{task_name}] Returning raw output for debugging.")
    
    # Return the raw output as a plain text response
    return PlainTextResponse(content=response_text)