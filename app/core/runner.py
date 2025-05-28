# The Code is to implement the command of zeo++
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2025-05-13

# app/core/runner.py

import sh
from pathlib import Path
from typing import List, Dict, Optional

from app.utils.logger import logger
from app.utils.file import compute_cache_key, get_cache_path
from app.core.config import ZEO_EXECUTABLE, WORKSPACE_ROOT, ENABLE_CACHE


class ZeoRunner:
    def __init__(self, zeo_exec_path: str = ZEO_EXECUTABLE, workspace: Path = WORKSPACE_ROOT):
        self.zeo_exec = zeo_exec_path
        self.workspace = workspace

    def run_command(
        self,
        structure_file: Path,
        zeo_args: List[str],
        output_files: List[str],
        extra_identifier: Optional[str] = None
    ) -> Dict:
        """
        Run Zeo++ with given args. Check cache first. If hit, return cached result.

        Args:
            structure_file (Path): uploaded input file path
            zeo_args (List[str]): command args passed to `network`
            output_files (List[str]): list of expected output filenames
            extra_identifier (str): optional string to distinguish different calls

        Returns:
            Dict: {
                success: bool,
                exit_code: int,
                stdout: str,
                stderr: str,
                cached: bool,
                output_data: Dict[filename] = file content
            }
        """
        logger.info(f"[runner] Preparing Zeo++ command: {zeo_args}")

        # create cache directory and cache key
        cache_key = compute_cache_key(structure_file, zeo_args, extra_identifier)
        cache_dir = get_cache_path(cache_key)

        if ENABLE_CACHE and cache_dir.exists():
            logger.info(f"[cache] Cache hit for key: {cache_key}")
            return {
                "success": True,
                "exit_code": 0,
                "stdout": "[cache] Used cached result.",
                "stderr": "",
                "cached": True,
                "output_data": {f.name: f.read_text() for f in cache_dir.glob("*")}
            }

        logger.info(f"[cache] Cache miss. Running Zeo++...")

        try:
            result = sh.Command(self.zeo_exec)(*zeo_args, _cwd=str(structure_file.parent), _err_to_out=True)
            logger.info(f"[zeo++] Execution completed.")

            if ENABLE_CACHE:
                cache_dir.mkdir(parents=True, exist_ok=True)
                for out_file in output_files:
                    out_path = structure_file.parent / out_file
                    if out_path.exists():
                        cached_path = cache_dir / out_file
                        cached_path.write_text(out_path.read_text())

            return {
                "success": True,
                "exit_code": 0,
                "stdout": str(result),
                "stderr": "",
                "cached": False,
                "output_data": {
                    f: (structure_file.parent / f).read_text()
                    for f in output_files if (structure_file.parent / f).exists()
                }
            }

        except sh.ErrorReturnCode as e:
            logger.error(f"[zeo++] Error: Exit code {e.exit_code}")
            return {
                "success": False,
                "exit_code": e.exit_code,
                "stdout": e.stdout.decode() if e.stdout else "",
                "stderr": e.stderr.decode() if e.stderr else "",
                "cached": False,
                "output_data": {}
            }
