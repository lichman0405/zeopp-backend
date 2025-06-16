# The module provides an API endpoint to retrieve framework information from a structure file.
# Author: Shibo Li
# Date: 2025-06-16
# Version: 0.1.0

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from app.utils.file import save_uploaded_file, compute_cache_key, get_cache_path
from app.core.runner import ZeoRunner
from app.core import config
from app.utils.logger import logger

router = APIRouter()
runner = ZeoRunner()

@router.post(
    "/api/framework_info/download",
    response_class=FileResponse,
    summary="Get and Download Framework Info File (-strinfo)",
    tags=["Structure Analysis"]
)
async def download_framework_info(
    structure_file: UploadFile = File(..., description="A structure file (e.g., .cif, .cssr)."),
    ha: bool = Form(True, description="Enable high accuracy mode."),
):
    """
    Identifies framework information and returns the resulting .strinfo file for download.
    Corresponds to the `-strinfo` flag in Zeo++.
    """
    task_name = "framework_info_download"
    output_filename = "result.strinfo"
    logger.info(f"[{task_name}] Received new request.")

    zeo_args = ["-strinfo", output_filename]
    if ha:
        zeo_args.insert(0, "-ha")
        
    input_path = save_uploaded_file(structure_file, prefix=task_name)
    final_runner_args = zeo_args + [input_path.name]

    cache_key = compute_cache_key(input_path, final_runner_args, task_name)
    cache_path = get_cache_path(cache_key)
    final_file_path = cache_path / output_filename

    if config.ENABLE_CACHE and final_file_path.exists():
        logger.info(f"[{task_name}] Cache hit. Returning file: {final_file_path}")
        return FileResponse(
            path=final_file_path,
            media_type='text/plain',
            filename=f"{structure_file.filename}.strinfo"
        )

    logger.info(f"[{task_name}] Cache miss. Running Zeo++ with args: {' '.join(final_runner_args)}")

    result = runner.run_command(
        structure_file=input_path,
        zeo_args=final_runner_args,
        output_files=[output_filename],
        extra_identifier=task_name
    )

    if not result["success"] or not final_file_path.exists():
        stderr_content = result.get("stderr", "No stderr captured, command may have failed silently.")
        error_msg = f"Zeo++ command failed or did not generate the output file '{output_filename}'."
        logger.display_error_panel(f"{task_name} Failed", f"{error_msg}\n\n{stderr_content}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": error_msg, "stderr": stderr_content}
        )
    
    logger.success(f"[{task_name}] Task complete. Sending file for download.")

    return FileResponse(
        path=final_file_path, 
        media_type='text/plain', 
        filename=f"{structure_file.filename}.strinfo" 
    )