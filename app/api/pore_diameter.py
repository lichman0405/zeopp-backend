# Pore Diameter API Endpoint
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

from app.models.pore_diameter import PoreDiameterResponse
from app.core.runner import ZeoRunner
from app.utils.file import save_uploaded_file
from app.utils.parser import parse_res_from_text

router = APIRouter()
runner = ZeoRunner()

@router.post("/api/pore_diameter", response_model=PoreDiameterResponse)
async def compute_pore_diameter(
    structure_file: UploadFile = File(...),
    ha: bool = Form(True),
    output_filename: str = Form("result.res")
):
    """
    Compute largest included / free / along-free sphere diameters using Zeo++ -res
    """
    input_path: Path = save_uploaded_file(structure_file, prefix="pore")

    args = []
    if ha:
        args.append("-ha")
    args += ["-res", output_filename, input_path.name]

    result = runner.run_command(
        structure_file=input_path,
        zeo_args=args,
        output_files=[output_filename],
        extra_identifier="pore_diameter"
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

    parsed = parse_res_from_text(content)

    return PoreDiameterResponse(
        **parsed,
        cached=result["cached"]
    )
