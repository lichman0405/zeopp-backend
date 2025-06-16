# The module provides an API endpoint to generate blocking spheres in a structure file.
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.2.0

from fastapi import APIRouter, UploadFile, File, Form
from app.models.blocking_spheres import BlockingSpheresResponse
from app.utils.parser import parse_block_from_text
from app.core.handler import process_zeo_request

router = APIRouter()

@router.post(
    "/api/blocking_spheres",
    response_model=BlockingSpheresResponse,
    summary="Generate Blocking Spheres (-block)",
    tags=["Calculation"]
)
async def compute_blocking_spheres(
    structure_file: UploadFile = File(..., description="A .cif, .cssr, .v1, or .arc file."),
    probe_radius: float = Form(1.86, description="Radius of the probe molecule in Angstroms."),
    samples: int = Form(100, description="Number of Monte Carlo samples for integration."),
    ha: bool = Form(True, description="Enable high accuracy mode."),
):
    """
    Identifies inaccessible regions and generates blocking spheres in RASPA format.
    Corresponds to the `-block` flag in Zeo++.
    """
    output_filename = "result.block"

    zeo_args = [
        "-block",
        str(probe_radius),
        str(samples),
        output_filename
    ]

    if ha:
        zeo_args.insert(0, "-ha")

    return await process_zeo_request(
        structure_file=structure_file,
        zeo_args=zeo_args,
        output_files=[output_filename],
        parser=parse_block_from_text,
        response_model=BlockingSpheresResponse,
        task_name="blocking_spheres"
    )