# The module provides an API endpoint to count open metal sites in a structure file.
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0

from fastapi import APIRouter, UploadFile, File, Form
from app.models.open_metal_sites import OpenMetalSitesResponse
from app.utils.parser import parse_oms_from_text
from app.core.handler import process_zeo_request

router = APIRouter()

@router.post(
    "/api/open_metal_sites",
    response_model=OpenMetalSitesResponse,
    summary="Count Open Metal Sites (-oms)",
    tags=["Structure Analysis"]
)
async def count_open_metal_sites(
    structure_file: UploadFile = File(..., description="A structure file (e.g., .cif, .cssr)."),
    ha: bool = Form(True, description="Enable high accuracy mode."),
):
    """
    Counts the number of open metal sites in the provided structure.
    Corresponds to the `-oms` flag in Zeo++.
    """
    output_filename = "result.oms"

    zeo_args = ["-oms", output_filename]
    if ha:
        zeo_args.insert(0, "-ha")

    return await process_zeo_request(
        structure_file=structure_file,
        zeo_args=zeo_args,
        output_files=[output_filename],
        parser=parse_oms_from_text,
        response_model=OpenMetalSitesResponse,
        task_name="open_metal_sites"
    )