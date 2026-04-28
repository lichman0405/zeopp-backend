"""Zeo++ command runner with caching and async thread-pool execution."""

# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13
# Updated: 2026-02-25 - Added cross-platform subprocess fallback for Windows development

import asyncio
import functools
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.core.config import WORKSPACE_ROOT, ZEO_EXECUTABLE, settings
from app.utils.file import compute_cache_key, get_cache_path
from app.utils.logger import logger

try:
    import sh as sh_lib  # type: ignore[import-untyped]
except ImportError:
    sh_lib = None


_executor = ThreadPoolExecutor(max_workers=settings.max_concurrent_tasks)


def _safe_read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _decode_stream(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


class ZeoRunner:
    def __init__(self, zeo_exec_path: str = ZEO_EXECUTABLE, workspace: Path = WORKSPACE_ROOT):
        self.zeo_exec = zeo_exec_path
        self.workspace = workspace

    def _run_with_sh(self, zeo_args: List[str], cwd: Path) -> Tuple[bool, int, str, str]:
        """Run command via `sh` (Linux/macOS)."""
        try:
            result = sh_lib.Command(self.zeo_exec)(  # type: ignore[union-attr]
                *zeo_args,
                _cwd=str(cwd),
                _err_to_out=True,
                _timeout=settings.zeo_command_timeout_seconds,
            )
            return True, 0, str(result), ""
        except sh_lib.CommandNotFound as exc:  # type: ignore[union-attr]
            return False, 127, "", str(exc)
        except sh_lib.TimeoutException as exc:  # type: ignore[union-attr]
            logger.error(
                f"[runner] Zeo++ command timed out after "
                f"{settings.zeo_command_timeout_seconds}s: {zeo_args}"
            )
            return False, 124, "", f"Zeo++ command timed out after {settings.zeo_command_timeout_seconds}s: {exc}"
        except sh_lib.ErrorReturnCode as exc:  # type: ignore[union-attr]
            return (
                False,
                int(exc.exit_code),
                _decode_stream(exc.stdout),
                _decode_stream(exc.stderr),
            )

    def _run_with_subprocess(self, zeo_args: List[str], cwd: Path) -> Tuple[bool, int, str, str]:
        """Run command via subprocess (cross-platform fallback)."""
        cmd = [self.zeo_exec, *zeo_args]
        try:
            completed = subprocess.run(
                cmd,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                check=False,
                timeout=settings.zeo_command_timeout_seconds,
            )
            return completed.returncode == 0, completed.returncode, completed.stdout or "", completed.stderr or ""
        except FileNotFoundError:
            return False, 127, "", f"Executable not found: {self.zeo_exec}"
        except subprocess.TimeoutExpired as exc:
            logger.error(
                f"[runner] Zeo++ command timed out after "
                f"{settings.zeo_command_timeout_seconds}s: {zeo_args}"
            )
            stdout = _decode_stream(exc.stdout)
            return False, 124, stdout, f"Zeo++ command timed out after {settings.zeo_command_timeout_seconds}s"
        except Exception as exc:
            return False, 1, "", str(exc)

    def run_command(
        self,
        structure_file: Path,
        zeo_args: List[str],
        output_files: List[str],
        extra_identifier: Optional[str] = None,
        skip_cache: bool = False
    ) -> Dict:
        """
        Run Zeo++ command with cache lookup.

        Returns:
            Dict containing execution status and output file content.
        """
        logger.info(f"[runner] Preparing Zeo++ command: {zeo_args}")

        cache_key = compute_cache_key(structure_file, zeo_args, extra_identifier)
        cache_dir = get_cache_path(cache_key)

        if settings.enable_cache and cache_dir.exists() and not skip_cache:
            logger.info(f"[cache] Cache hit for key: {cache_key}")
            return {
                "success": True,
                "exit_code": 0,
                "stdout": "[cache] Used cached result.",
                "stderr": "",
                "cached": True,
                "output_data": {f.name: _safe_read_text(f) for f in cache_dir.glob("*") if f.is_file()}
            }

        if skip_cache:
            logger.info("[cache] Skipping cache (force_recalculate=True)")

        logger.info("[cache] Cache miss. Running Zeo++...")

        cwd = structure_file.parent
        if sh_lib is not None:
            success, exit_code, stdout, stderr = self._run_with_sh(zeo_args, cwd)
        else:
            success, exit_code, stdout, stderr = self._run_with_subprocess(zeo_args, cwd)

        if not success:
            logger.error(f"[zeo++] Error: Exit code {exit_code}")
            return {
                "success": False,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "cached": False,
                "output_data": {}
            }

        logger.info("[zeo++] Execution completed.")

        if settings.enable_cache:
            cache_dir.mkdir(parents=True, exist_ok=True)
            for out_file in output_files:
                out_path = cwd / out_file
                if out_path.exists():
                    (cache_dir / out_file).write_text(_safe_read_text(out_path), encoding="utf-8")

        return {
            "success": True,
            "exit_code": 0,
            "stdout": stdout,
            "stderr": stderr,
            "cached": False,
            "output_data": {
                filename: _safe_read_text(cwd / filename)
                for filename in output_files
                if (cwd / filename).exists()
            }
        }

    async def run_command_async(
        self,
        structure_file: Path,
        zeo_args: List[str],
        output_files: List[str],
        extra_identifier: Optional[str] = None,
        skip_cache: bool = False
    ) -> Dict:
        """Async wrapper for `run_command` that uses thread pool execution."""
        loop = asyncio.get_event_loop()
        func = functools.partial(
            self.run_command,
            structure_file,
            zeo_args,
            output_files,
            extra_identifier,
            skip_cache
        )
        return await loop.run_in_executor(_executor, func)
