# Surface Area API Endpoint refactored to use a handler function
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.2.0


from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from app.models.surface_area import SurfaceAreaResponse
from app.utils.parser import parse_sa_from_text
from app.core.handler import process_zeo_request

router = APIRouter()

@router.post(
    "/api/surface_area",
    response_model=SurfaceAreaResponse,
    summary="Calculate Accessible Surface Area (sa)",
    tags=["Analysis"]
)
async def compute_surface_area(
    structure_file: UploadFile = File(..., description="A .cif, .cssr, .v1, or .arc file."),
    chan_radius: float = Form(1.21, description="Channel radius in Angstroms."),
    probe_radius: float = Form(1.21, description="Radius of the probe molecule in Angstroms."),
    samples: int = Form(2000, description="Number of Monte Carlo samples for integration."),
    output_filename: str = Form("result.sa", description="Name of the output file containing surface area results."),
    ha: bool = Form(True, description="Whether to use high accuracy mode (default: True)")

):
    """
    Calculates the accessible surface area of the framework using a Monte Carlo sampling method.
    Corresponds to the `-sa` flag in Zeo++.
    """
    output_filename = "result.sa"

    effective_chan_radius = chan_radius if chan_radius is not None else probe_radius

    if probe_radius > effective_chan_radius:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid radii: probe_radius ({probe_radius}) cannot be greater than chan_radius ({effective_chan_radius})."
        )

    zeo_args = [
        "-sa",
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
        parser=parse_sa_from_text,
        response_model=SurfaceAreaResponse,
        task_name="surface_area"
    )