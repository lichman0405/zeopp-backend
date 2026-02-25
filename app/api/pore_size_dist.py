# Pore Size Distribution API Endpoint
# Author: Shibo Li
# Date: 2025-06-16
# Updated: 2026-02-25 - Async execution, robust cache behavior, temp cleanup

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from app.core.config import settings
from app.core.middleware import get_allowed_extensions_str, validate_structure_file
from app.core.runner import ZeoRunner
from app.utils.cleanup import cleanup_temp_directory
from app.utils.file import compute_cache_key, get_cache_path, save_uploaded_file
from app.utils.logger import logger

router = APIRouter()
runner = ZeoRunner()


@router.post(
    "/api/v1/pore_size_dist/download",
    response_class=FileResponse,
    summary="Calculate and Download Pore Size Distribution File",
    tags=["Analysis"]
)
async def download_pore_size_dist(
    structure_file: UploadFile = File(..., description="A .cif, .cssr, .v1, or .arc file."),
    probe_radius: float = Form(1.21, description="Radius of the probe for MC sampling. Must be <= chan_radius."),
    chan_radius: Optional[float] = Form(None, description="Radius for accessibility check. Defaults to probe_radius."),
    samples: int = Form(50000, description="Number of Monte Carlo samples per unit cell for integration."),
    ha: bool = Form(True, description="Enable high accuracy mode."),
    force_recalculate: bool = Form(False, description="Force recalculation, bypassing cache."),
):
    """
    Calculates the pore size distribution and returns the resulting .psd_histo file for download.
    Corresponds to the `-psd` flag in Zeo++.
    """
    if not validate_structure_file(structure_file.filename):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid file type. Allowed extensions: {get_allowed_extensions_str()}"
        )

    if structure_file.size and structure_file.size > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB"
        )

    task_name = "psd_download"
    logger.info(f"[{task_name}] Received new request.")

    effective_chan_radius = chan_radius if chan_radius is not None else probe_radius
    if probe_radius > effective_chan_radius:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid radii: probe_radius ({probe_radius}) cannot be greater than chan_radius ({effective_chan_radius})."
        )

    input_path = save_uploaded_file(structure_file, prefix=task_name)
    temp_dir = input_path.parent
    cleanup_scheduled = False

    try:
        zeo_args = [
            "-psd",
            str(effective_chan_radius),
            str(probe_radius),
            str(samples)
        ]
        if ha:
            zeo_args.insert(0, "-ha")

        final_runner_args = zeo_args + [input_path.name]
        cache_key = compute_cache_key(input_path, final_runner_args, task_name)
        cache_path = get_cache_path(cache_key)

        final_output_filename = f"{input_path.stem}.psd_histo"
        cached_file_path = cache_path / final_output_filename
        generated_file_path = temp_dir / final_output_filename

        if settings.enable_cache and not force_recalculate and cached_file_path.exists():
            logger.info(f"[{task_name}] Cache hit. Returning file: {cached_file_path}")
            cleanup_temp_directory(temp_dir)
            download_name = f"{Path(structure_file.filename or 'result').name}.psd_histo"
            return FileResponse(path=cached_file_path, media_type="text/plain", filename=download_name)

        logger.info(
            f"[{task_name}] "
            f"{'Force recalculate requested. ' if force_recalculate else 'Cache miss. '}Running Zeo++..."
        )
        result = await runner.run_command_async(
            structure_file=input_path,
            zeo_args=final_runner_args,
            output_files=[final_output_filename],
            extra_identifier=task_name,
            skip_cache=force_recalculate
        )

        if not result["success"]:
            stderr_content = result.get("stderr", "No stderr captured, command may have failed silently.")
            error_msg = f"Zeo++ command failed for output '{final_output_filename}'."
            logger.display_error_panel(f"{task_name} Failed", f"{error_msg}\n\n{stderr_content}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": error_msg, "stderr": stderr_content}
            )

        final_file_path = cached_file_path if result.get("cached") else generated_file_path
        if not final_file_path.exists():
            error_msg = f"Expected output file '{final_output_filename}' was not generated."
            logger.display_error_panel(f"{task_name} Failed", error_msg)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"message": error_msg}
            )

        logger.success(f"[{task_name}] Task complete. Sending file for download: {final_file_path}")
        download_name = f"{Path(structure_file.filename or 'result').name}.psd_histo"

        if result.get("cached"):
            cleanup_temp_directory(temp_dir)
            return FileResponse(path=final_file_path, media_type="text/plain", filename=download_name)

        cleanup_scheduled = True
        return FileResponse(
            path=final_file_path,
            media_type="text/plain",
            filename=download_name,
            background=BackgroundTask(cleanup_temp_directory, temp_dir)
        )
    except Exception:
        if not cleanup_scheduled:
            cleanup_temp_directory(temp_dir)
        raise
