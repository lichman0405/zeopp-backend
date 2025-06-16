# Pore Size Distribution API Endpoint refactored to use a handler function
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.2.0

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from typing import Optional
from app.models.pore_size_dist import PoreSizeDistResponse
from app.utils.parser import parse_psd_from_text
from app.core.handler import process_zeo_request

router = APIRouter()

@router.post(
    "/api/pore_size_dist",
    response_model=PoreSizeDistResponse,
    summary="Calculate Pore Size Distribution (psd)",
    tags=["Analysis"]
)
async def compute_pore_size_dist(
    structure_file: UploadFile = File(..., description="A .cif, .cssr, .v1, or .arc file."),
    probe_radius: float = Form(1.21, description="Radius of the probe for MC sampling. Must be <= chan_radius."),
    chan_radius: Optional[float] = Form(None, description="Radius for accessibility check. Defaults to probe_radius."),
    samples: int = Form(50000, description="Number of Monte Carlo samples per unit cell for integration."),
    ha: bool = Form(True, description="Enable high accuracy mode."),
):
    """
    Calculates the pore size distribution histogram.
    Corresponds to the `-psd` flag in Zeo++.
    The actual result is read from the `_histo` output file.
    """
    base_output_filename = "result.psd"

    final_output_filename = f"{base_output_filename}_histo"

    effective_chan_radius = chan_radius if chan_radius is not None else probe_radius

    if probe_radius > effective_chan_radius:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid radii: probe_radius ({probe_radius}) cannot be greater than chan_radius ({effective_chan_radius})."
        )

    zeo_args = [
        "-psd",
        str(effective_chan_radius),
        str(probe_radius),
        str(samples),
        base_output_filename
    ]

    if ha:
        zeo_args.insert(0, "-ha")

    return await process_zeo_request(
        structure_file=structure_file,
        zeo_args=zeo_args,
        output_files=[final_output_filename], 
        parser=parse_psd_from_text,
        response_model=PoreSizeDistResponse,
        task_name="pore_size_dist"
    )