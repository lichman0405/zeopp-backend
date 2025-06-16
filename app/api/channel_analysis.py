# Channel Dimensionality API Endpoint refactored to use a handler function
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.2.0

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from app.models.channel_analysis import ChannelAnalysisResponse
from app.core.handler import process_zeo_request
from app.utils.parser import parse_chan_from_text

router = APIRouter()

@router.post(
        "/api/channel_analysis", 
        response_model=ChannelAnalysisResponse,
        summary="Analyze Channel Dimensionality (chan)",
        tags=["Analysis"]
)
async def compute_channel_analysis(
    structure_file: UploadFile = File(..., description="A .cif, .cssr, .v1, or .arc file."),
    probe_radius: float = Form(1.21, description="Radius of the probe molecule in Angstroms."),
    output_filename: str = Form("result.chan", description="Name of the output file containing accessible volume results."),
    ha: bool = Form(True, description="Whether to use high accuracy mode (default: True)")

):
    """
    Analyze channel dimensionality using Zeo++ -chan
    """
    output_filename = "result.chan"

    zeo_args = [
        "-chan",
        str(probe_radius),
        output_filename,
    ]
    if ha:
        zeo_args.insert(0, "-ha")

    return await process_zeo_request(
        structure_file=structure_file,
        zeo_args=zeo_args,
        output_files=[output_filename],
        parser=parse_chan_from_text,
        response_model=ChannelAnalysisResponse,
        task_name="channel_analysis"
    )