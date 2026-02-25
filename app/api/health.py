# Health Check and System Information API Endpoint
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-12-22
# Version: 0.3.1

from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime
import sys
import shutil
import subprocess
from pathlib import Path

from app.core.config import ZEO_EXECUTABLE, WORKSPACE_ROOT, ENABLE_CACHE, LOG_LEVEL, settings

router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    
    
class DetailedHealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    api_version: str
    zeopp_executable: str
    zeopp_available: bool
    workspace_root: str
    cache_enabled: bool
    log_level: str
    python_version: str
    uptime_seconds: float


# Store start time for uptime calculation
_start_time = datetime.utcnow()


def _check_zeopp_available() -> bool:
    """
    Check whether the Zeo++ executable is callable in current environment.
    Supports both PATH lookups and explicit file paths.
    """
    exec_candidate = ZEO_EXECUTABLE
    executable = None

    candidate_path = Path(exec_candidate)
    if candidate_path.exists():
        executable = str(candidate_path)
    else:
        executable = shutil.which(exec_candidate)

    if not executable:
        return False

    try:
        result = subprocess.run(
            [executable, "--help"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10
        )
        return result.returncode in (0, 1)
    except Exception:
        return False


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Basic Health Check",
    tags=["System"],
    status_code=status.HTTP_200_OK
)
async def health_check():
    """
    Basic health check endpoint to verify the service is running.
    
    Returns:
        HealthCheckResponse: Basic health status and timestamp
    """
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version=settings.version
    )


@router.get(
    "/health/detailed",
    response_model=DetailedHealthResponse,
    summary="Detailed Health Check",
    tags=["System"],
    status_code=status.HTTP_200_OK
)
async def detailed_health_check():
    """
    Detailed health check endpoint with system information.
    
    Returns:
        DetailedHealthResponse: Comprehensive health status and system info
    """
    zeopp_available = _check_zeopp_available()
    
    # Calculate uptime
    uptime = (datetime.utcnow() - _start_time).total_seconds()
    
    return DetailedHealthResponse(
        status="healthy" if zeopp_available else "degraded",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version=settings.version,
        api_version="v1",
        zeopp_executable=ZEO_EXECUTABLE,
        zeopp_available=zeopp_available,
        workspace_root=str(WORKSPACE_ROOT),
        cache_enabled=ENABLE_CACHE,
        log_level=LOG_LEVEL,
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        uptime_seconds=round(uptime, 2)
    )


@router.get(
    "/version",
    summary="Get API Version",
    tags=["System"],
    status_code=status.HTTP_200_OK
)
async def get_version():
    """
    Get the current API version information.
    
    Returns:
        dict: Version information including API version and service version
    """
    return {
        "service": "Zeo++ API Service",
        "version": settings.version,
        "api_version": "v1",
        "description": "A containerized FastAPI service for Zeo++ structure analysis"
    }
