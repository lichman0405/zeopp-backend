# Cleanup Utilities for Temporary Files
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-12-31
# Version: 0.3.1

"""
Utilities for cleaning up temporary files and managing workspace storage.
"""

import shutil
import time
from pathlib import Path
from typing import Tuple
from contextlib import contextmanager

from app.core.config import TMP_DIR, CACHE_DIR
from app.utils.logger import logger


def cleanup_temp_directory(task_dir: Path) -> bool:
    """
    Remove a specific task directory from the temporary folder.
    
    Args:
        task_dir: Path to the task directory to remove
        
    Returns:
        True if cleanup was successful, False otherwise
    """
    try:
        if task_dir.exists() and task_dir.is_dir():
            shutil.rmtree(task_dir)
            logger.info(f"[cleanup] Removed temporary directory: {task_dir.name}")
            return True
        return False
    except Exception as e:
        logger.warning(f"[cleanup] Failed to remove {task_dir}: {e}")
        return False


def cleanup_old_temp_files(max_age_hours: float = 24.0) -> Tuple[int, int]:
    """
    Remove temporary directories older than specified age.
    
    Args:
        max_age_hours: Maximum age in hours for temp directories
        
    Returns:
        Tuple of (directories_removed, directories_failed)
    """
    if not TMP_DIR.exists():
        return 0, 0
    
    removed = 0
    failed = 0
    cutoff_time = time.time() - (max_age_hours * 3600)
    
    for item in TMP_DIR.iterdir():
        if item.is_dir():
            try:
                # Use modification time to determine age
                mtime = item.stat().st_mtime
                if mtime < cutoff_time:
                    shutil.rmtree(item)
                    removed += 1
                    logger.info(f"[cleanup] Removed old temp directory: {item.name}")
            except Exception as e:
                logger.warning(f"[cleanup] Failed to remove {item}: {e}")
                failed += 1
    
    if removed > 0:
        logger.success(f"[cleanup] Cleaned up {removed} old temporary directories")
    
    return removed, failed


def get_temp_storage_stats() -> dict:
    """
    Get statistics about temporary storage usage.
    
    Returns:
        Dict with temp directory statistics
    """
    if not TMP_DIR.exists():
        return {"exists": False, "count": 0, "total_size_mb": 0}
    
    count = 0
    total_size = 0
    
    for item in TMP_DIR.iterdir():
        if item.is_dir():
            count += 1
            for file in item.rglob("*"):
                if file.is_file():
                    total_size += file.stat().st_size
    
    return {
        "exists": True,
        "count": count,
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }


def get_cache_storage_stats() -> dict:
    """
    Get statistics about cache storage usage.
    
    Returns:
        Dict with cache directory statistics
    """
    if not CACHE_DIR.exists():
        return {"exists": False, "count": 0, "total_size_mb": 0}
    
    count = 0
    total_size = 0
    
    for item in CACHE_DIR.iterdir():
        if item.is_dir():
            count += 1
            for file in item.rglob("*"):
                if file.is_file():
                    total_size += file.stat().st_size
    
    return {
        "exists": True,
        "count": count,
        "total_size_mb": round(total_size / (1024 * 1024), 2)
    }


def clear_all_cache() -> Tuple[int, int]:
    """
    Clear all cached results.
    
    Returns:
        Tuple of (entries_removed, entries_failed)
    """
    if not CACHE_DIR.exists():
        return 0, 0
    
    removed = 0
    failed = 0
    
    for item in CACHE_DIR.iterdir():
        if item.is_dir():
            try:
                shutil.rmtree(item)
                removed += 1
            except Exception as e:
                logger.warning(f"[cache] Failed to remove cache entry {item}: {e}")
                failed += 1
    
    if removed > 0:
        logger.success(f"[cache] Cleared {removed} cache entries")
    
    return removed, failed


@contextmanager
def auto_cleanup_temp(task_dir: Path):
    """
    Context manager that automatically cleans up temp directory after use.
    
    Usage:
        with auto_cleanup_temp(task_dir):
            # do work with task_dir
        # task_dir is automatically cleaned up
    """
    try:
        yield task_dir
    finally:
        cleanup_temp_directory(task_dir)
