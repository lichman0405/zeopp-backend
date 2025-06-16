# Pore Diameter API Endpoint
# Edited version for build handler function to reduce the complexity of the API endpoint
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13


from fastapi import APIRouter, UploadFile, File, Form
from app.models.pore_diameter import PoreDiameterResponse
from app.utils.parser import parse_res_from_text
from app.core.handler import process_zeo_request 

router = APIRouter()

@router.post(
    "/api/pore_diameter",
    response_model=PoreDiameterResponse,
    summary="Calculate Pore Diameter (res)",
    tags=["Analysis"]
)
async def compute_pore_diameter(
    structure_file: UploadFile = File(..., description="A .cif, .cssr, .v1, or .arc file."),
    ha: bool = Form(True, description="Enable high accuracy mode."),
):
    """
    Calculates the largest free sphere (Di) and largest included sphere (Df) 
    that can diffuse along the channels of the framework.
    Corresponds to the `-res` flag in Zeo++.
    """
    output_filename = "result.res"
    
    zeo_args = ["-ha", "-res", output_filename] if ha else ["-res", output_filename]
    
    return await process_zeo_request(
        structure_file=structure_file,
        zeo_args=zeo_args,
        output_files=[output_filename],
        parser=parse_res_from_text,
        response_model=PoreDiameterResponse,
        task_name="pore_diameter"
    )