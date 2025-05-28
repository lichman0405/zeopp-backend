# Surface Area API Endpoint
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

from app.core.runner import ZeoRunner
from app.models.surface_area import SurfaceAreaResponse
from app.utils.file import save_uploaded_file
from app.utils.parser import parse_sa_from_text

router = APIRouter()
runner = ZeoRunner()

@router.post("/api/surface_area", response_model=SurfaceAreaResponse)
async def compute_surface_area(
    structure_file: UploadFile = File(...),
    chan_radius: float = Form(...),
    probe_radius: float = Form(...),
    samples: int = Form(...),
    output_filename: str = Form("result.sa"),
    ha: bool = Form(True)
):
    """
    Compute accessible surface area using Zeo++ -sa command
    """
    input_path: Path = save_uploaded_file(structure_file, prefix="sa")

    args = []
    if ha:
        args.append("-ha")
    args += ["-sa", str(chan_radius), str(probe_radius), str(samples), output_filename, input_path.name]

    result = runner.run_command(
        structure_file=input_path,
        zeo_args=args,
        output_files=[output_filename],
        extra_identifier="surface_area"
    )

    if not result["success"]:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Zeo++ failed",
                "stderr": result["stderr"]
            }
        )

    output_text = result["output_data"].get(output_filename)
    if not output_text:
        raise HTTPException(status_code=500, detail=f"Output file '{output_filename}' was not generated.")

    parsed = parse_sa_from_text(output_text)

    return SurfaceAreaResponse(
        **parsed,
        cached=result["cached"]
    )
