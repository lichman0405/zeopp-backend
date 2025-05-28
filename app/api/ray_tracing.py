# Ray Tracing API Endpoint
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

from app.core.runner import ZeoRunner
from app.models.ray_tracing import RayTracingResponse
from app.utils.file import save_uploaded_file

router = APIRouter()
runner = ZeoRunner()

@router.post("/api/ray_tracing", response_model=RayTracingResponse)
async def compute_ray_tracing_histogram(
    structure_file: UploadFile = File(...),
    chan_radius: float = Form(...),
    probe_radius: float = Form(...),
    samples: int = Form(...),
    output_filename: str = Form("result.ray"),
    ha: bool = Form(True)
):
    """
    Perform stochastic ray tracing using Zeo++ -ray_atom command (returns raw histogram text)
    """
    input_path: Path = save_uploaded_file(structure_file, prefix="ray")

    args = []
    if ha:
        args.append("-ha")
    args += ["-ray_atom", str(chan_radius), str(probe_radius), str(samples), output_filename, input_path.name]

    result = runner.run_command(
        structure_file=input_path,
        zeo_args=args,
        output_files=[output_filename],
        extra_identifier="ray_tracing"
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

    content = result["output_data"].get(output_filename)
    if not content:
        raise HTTPException(status_code=500, detail=f"Output file '{output_filename}' was not generated.")

    return RayTracingResponse(
        content=content,
        cached=result["cached"]
    )
