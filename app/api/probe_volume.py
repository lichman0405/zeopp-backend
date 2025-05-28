# Probe-Occupiable Volume API Endpoint
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

from app.core.runner import ZeoRunner
from app.models.probe_volume import ProbeVolumeResponse
from app.utils.file import save_uploaded_file
from app.utils.parser import parse_volpo_from_text

router = APIRouter()
runner = ZeoRunner()

@router.post("/api/probe_volume", response_model=ProbeVolumeResponse)
async def compute_probe_volume(
    structure_file: UploadFile = File(...),
    chan_radius: float = Form(...),
    probe_radius: float = Form(...),
    samples: int = Form(...),
    output_filename: str = Form("result.volpo"),
    ha: bool = Form(True)
):
    """
    Compute probe-occupiable volume using Zeo++ -volpo command
    """
    input_path: Path = save_uploaded_file(structure_file, prefix="volpo")

    args = []
    if ha:
        args.append("-ha")
    args += ["-volpo", str(chan_radius), str(probe_radius), str(samples), output_filename, input_path.name]

    result = runner.run_command(
        structure_file=input_path,
        zeo_args=args,
        output_files=[output_filename],
        extra_identifier="probe_volume"
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

    parsed = parse_volpo_from_text(output_text)

    return ProbeVolumeResponse(
        **parsed,
        cached=result["cached"]
    )
