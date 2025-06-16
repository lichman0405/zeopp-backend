# Probe-Occupiable Volume API Endpoint refactored to use a handler function
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.2.0

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from app.models.probe_volume import ProbeVolumeResponse
from app.utils.parser import parse_volpo_from_text
from app.core.handler import process_zeo_request

router = APIRouter()

@router.post(
        "/api/probe_volume", 
        response_model=ProbeVolumeResponse,
        summary="Calculate Probe-Occupiable Volume (volpo)",
        tags=["Analysis"]
)


async def compute_probe_volume(
    structure_file: UploadFile = File(..., description="A .cif, .cssr, .v1, or .arc file."),
    chan_radius: float = Form(1.21, description="Channel radius in Angstroms."),
    probe_radius: float = Form(1.21, description="Radius of the probe molecule in Angstroms."),
    samples: int = Form(2000, description="Number of Monte Carlo samples for integration."),
    output_filename: str = Form("result.sa", description="Name of the output file containing probe-occupiable volume results."),
    ha: bool = Form(True, description="Whether to use high accuracy mode (default: True)")

):
    """
    Compute probe-occupiable volume using Zeo++ -volpo command
    Args:
        structure_file (UploadFile): A .cif, .cssr, .v1, or .arc file containing the structure.
        chan_radius (float): Channel radius in Angstroms.
        probe_radius (float): Radius of the probe molecule in Angstroms.
        samples (int): Number of Monte Carlo samples for integration.
        output_filename (str): Name of the output file containing probe-occupiable volume results.
        ha (bool): Whether to use high accuracy mode (default: True).
    Returns:
        ProbeVolumeResponse: Response model containing the results of the probe-occupiable volume calculation.
    """
    
    output_filename = "result.volpo"

    effective_chan_radius = chan_radius if chan_radius is not None else probe_radius
    if probe_radius > effective_chan_radius:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid radii: probe_radius ({probe_radius}) cannot be greater than chan_radius ({effective_chan_radius})."
        )

    zeo_args = [
        "-volpo",
        str(effective_chan_radius),
        str(probe_radius),
        str(samples),
        output_filename,
    ]
    if ha:
        zeo_args.insert(0, "-ha")

    return await process_zeo_request(
        structure_file=structure_file,
        zeo_args=zeo_args,
        output_files=[output_filename],
        parser=parse_volpo_from_text,
        response_model=ProbeVolumeResponse,
        task_name="probe_volume"
    )