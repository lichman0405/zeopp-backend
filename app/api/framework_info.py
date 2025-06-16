# The module provides an API endpoint to retrieve framework information from a structure file.
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0

from fastapi import APIRouter, UploadFile, File, Form
from app.models.framework_info import FrameworkInfoResponse
from app.utils.parser import parse_strinfo_from_text
from app.core.handler import process_zeo_request

router = APIRouter()

@router.post(
    "/api/framework_info",
    response_model=FrameworkInfoResponse,
    summary="Get Framework Info (-strinfo)",
    tags=["Structure Analysis"]
)
async def get_framework_info(
    structure_file: UploadFile = File(..., description="A structure file (e.g., .cif, .cssr)."),
    ha: bool = Form(True, description="Enable high accuracy mode."),
):
    """
    Identifies the number of frameworks and their dimensionalities in the structure.
    Corresponds to the `-strinfo` flag in Zeo++.
    """
    output_filename = "result.strinfo"

    zeo_args = ["-strinfo", output_filename]
    if ha:
        zeo_args.insert(0, "-ha")

    return await process_zeo_request(
        structure_file=structure_file,
        zeo_args=zeo_args,
        output_files=[output_filename],
        parser=parse_strinfo_from_text,
        response_model=FrameworkInfoResponse,
        task_name="framework_info"
    )