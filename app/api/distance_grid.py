# Distance Grid API Endpoint
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

from app.core.runner import ZeoRunner
from app.models.distance_grid import DistanceGridResponse
from app.utils.file import save_uploaded_file

router = APIRouter()
runner = ZeoRunner()

@router.post("/api/distance_grid", response_model=DistanceGridResponse)
async def generate_distance_grid(
    structure_file: UploadFile = File(...),
    mode: str = Form(...),  # gridG, gridGBohr, gridBOV
    output_basename: str = Form("result"),
    ha: bool = Form(True)
):
    """
    Generate distance grid file using Zeo++ (-gridG, -gridBOV, etc.)
    """
    if mode not in {"gridG", "gridGBohr", "gridBOV"}:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Invalid mode. Use gridG, gridGBohr, or gridBOV."}
        )

    input_path: Path = save_uploaded_file(structure_file, prefix="grid")

    args = []
    if ha:
        args.append("-ha")
    args += [f"-{mode}", input_path.name]

    if mode.startswith("gridG"):
        output_files = [f"{output_basename}.cube"]
    elif mode == "gridBOV":
        output_files = [f"{output_basename}.bov", f"{output_basename}.dat"]
    else:
        output_files = []

    result = runner.run_command(
        structure_file=input_path,
        zeo_args=args,
        output_files=output_files,
        extra_identifier="distance_grid"
    )

    if not result["success"]:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Zeo++ failed", "stderr": result["stderr"]}
        )

    # 检查每个输出文件是否在 output_data 中（非 None 表示确实生成了）
    missing_files = [f for f in output_files if f not in result["output_data"]]
    if missing_files:
        raise HTTPException(status_code=500, detail=f"Missing output files: {', '.join(missing_files)}")

    return DistanceGridResponse(
        message="Grid file(s) generated successfully",
        output_files=output_files,
        cached=result["cached"]
    )
