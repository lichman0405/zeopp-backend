# Cache Management API Endpoints
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-12-31
# Version: 0.3.1

"""
API endpoints for cache and temporary storage management.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.utils.cleanup import (
    cleanup_old_temp_files,
    get_temp_storage_stats,
    get_cache_storage_stats,
    clear_all_cache
)
from app.core.config import ENABLE_CACHE
from app.utils.logger import logger

router = APIRouter(prefix="/api/v1/cache", tags=["Cache Management"])


class StorageStatsResponse(BaseModel):
    """Response model for storage statistics."""
    cache: dict
    temp: dict
    cache_enabled: bool


class CleanupResponse(BaseModel):
    """Response model for cleanup operations."""
    success: bool
    message: str
    removed: int
    failed: int


class CacheClearResponse(BaseModel):
    """Response model for cache clear operation."""
    success: bool
    message: str
    entries_removed: int
    entries_failed: int


@router.get(
    "/stats",
    response_model=StorageStatsResponse,
    summary="Get Cache and Temp Storage Statistics"
)
async def get_storage_stats():
    """
    Get statistics about cache and temporary storage usage.
    
    Returns information about:
    - Number of cached entries
    - Total cache size in MB
    - Number of temp directories
    - Total temp size in MB
    """
    return StorageStatsResponse(
        cache=get_cache_storage_stats(),
        temp=get_temp_storage_stats(),
        cache_enabled=ENABLE_CACHE
    )


@router.post(
    "/cleanup",
    response_model=CleanupResponse,
    summary="Clean Up Old Temporary Files"
)
async def cleanup_temp_storage(max_age_hours: float = 24.0):
    """
    Remove temporary directories older than specified age.
    
    Args:
        max_age_hours: Maximum age in hours for temp directories (default: 24)
    
    Returns:
        Number of directories removed and failed
    """
    if max_age_hours <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="max_age_hours must be greater than 0"
        )
    
    logger.info(f"[cache] Starting cleanup of temp files older than {max_age_hours} hours")
    removed, failed = cleanup_old_temp_files(max_age_hours)
    
    return CleanupResponse(
        success=failed == 0,
        message=f"Cleaned up {removed} directories" if removed > 0 else "No old directories found",
        removed=removed,
        failed=failed
    )


@router.delete(
    "/clear",
    response_model=CacheClearResponse,
    summary="Clear All Cached Results"
)
async def clear_cache():
    """
    Clear all cached Zeo++ computation results.
    
    ⚠️ Warning: This will remove all cached results. Subsequent requests
    will need to recompute, which may take longer.
    """
    logger.warning("[cache] Clearing all cached results...")
    removed, failed = clear_all_cache()
    
    return CacheClearResponse(
        success=failed == 0,
        message=f"Cleared {removed} cache entries" if removed > 0 else "Cache was already empty",
        entries_removed=removed,
        entries_failed=failed
    )
