# MCP Tools for Zeo++ backend (transport-agnostic)
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2026-03-02
# Version: 0.3.2
#
# This module defines the FastMCP instance and all Zeo++ analysis tools.
# It is shared between the HTTP transport (main.py) and stdio transport (stdio_main.py).

import base64
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Type

from mcp.server.fastmcp import Context, FastMCP
from pydantic import BaseModel

from app.api.health import _check_zeopp_available
from app.core.config import CACHE_DIR, TMP_DIR, settings
from app.core.exceptions import ZeoppParsingError
from app.core.middleware import get_allowed_extensions_str, validate_structure_file
from app.core.runner import ZeoRunner
from app.models.accessible_volume import AccessibleVolumeResponse
from app.models.blocking_spheres import BlockingSpheresResponse
from app.models.channel_analysis import ChannelAnalysisResponse
from app.models.framework_info import FrameworkInfoResponse
from app.models.open_metal_sites import OpenMetalSitesResponse
from app.models.pore_diameter import PoreDiameterResponse
from app.models.probe_volume import ProbeVolumeResponse
from app.models.surface_area import SurfaceAreaResponse
from app.utils.cleanup import (
    cleanup_old_temp_files,
    cleanup_temp_directory,
    clear_all_cache,
    get_cache_storage_stats,
    get_temp_storage_stats,
)
from app.utils.parser import (
    parse_block_from_text,
    parse_chan_from_text,
    parse_oms_from_text,
    parse_res_from_text,
    parse_sa_from_text,
    parse_strinfo_from_text,
    parse_vol_from_text,
    parse_volpo_from_text,
)


# ── Helpers ─────────────────────────────────────────────────────────────────

def _normalize_path(path: str) -> str:
    cleaned = "/" + path.strip().strip("/")
    return "/" if cleaned == "//" else cleaned


def _as_log_level(level: str) -> str:
    normalized = (level or "").strip().upper()
    allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    return normalized if normalized in allowed else "INFO"


MCP_PATH = _normalize_path(settings.mcp_streamable_http_path)
MAX_RESULT_CHARS = max(512, settings.mcp_max_result_chars)


# ── Core instances ──────────────────────────────────────────────────────────

runner = ZeoRunner()

mcp = FastMCP(
    name="zeopp-backend",
    instructions=(
        "Tools for porous material analysis using Zeo++. "
        "Provide exactly one structure source: structure_path, structure_text, or structure_base64."
    ),
    log_level=_as_log_level(settings.log_level),
)


# ── Data classes / response helpers ─────────────────────────────────────────

@dataclass
class PreparedStructure:
    input_path: Path
    task_dir: Path
    size_bytes: int
    source: str
    filename: str


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _truncate_text(value: str) -> str:
    if len(value) <= MAX_RESULT_CHARS:
        return value
    return value[:MAX_RESULT_CHARS] + f"\n...[truncated {len(value) - MAX_RESULT_CHARS} chars]"


def _truncate_large_strings(value: Any) -> Any:
    if isinstance(value, str):
        return _truncate_text(value)
    if isinstance(value, list):
        return [_truncate_large_strings(item) for item in value]
    if isinstance(value, dict):
        return {k: _truncate_large_strings(v) for k, v in value.items()}
    return value


def _ok(tool: str, result: Dict[str, Any], *, cached: Optional[bool] = None, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "ok": True,
        "tool": tool,
        "timestamp": _now_iso(),
        "result": _truncate_large_strings(result),
    }
    if cached is not None:
        payload["cached"] = cached
    if meta:
        payload["meta"] = _truncate_large_strings(meta)
    return payload


def _error(tool: str, message: str, *, code: str = "TOOL_ERROR", details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "ok": False,
        "tool": tool,
        "timestamp": _now_iso(),
        "error_code": code,
        "message": message,
    }
    if details:
        payload["details"] = _truncate_large_strings(details)
    return payload


def _validate_positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be greater than 0")


def _decode_base64_content(raw: str) -> bytes:
    payload = raw.strip()
    marker = ";base64,"
    if marker in payload:
        payload = payload.split(marker, 1)[1]
    try:
        return base64.b64decode(payload, validate=True)
    except Exception as exc:
        raise ValueError(f"Invalid base64 content: {exc}") from exc


def _sanitize_filename(filename: Optional[str], fallback: str = "structure.cif") -> str:
    safe = Path(filename or fallback).name
    safe = safe.replace("\\", "_").replace("/", "_").strip()
    if not safe:
        safe = fallback
    if "." not in safe:
        safe = f"{safe}.cif"
    return safe


def _is_under_allowed_roots(candidate: Path) -> bool:
    roots = settings.mcp_allowed_path_roots_list
    if not roots:
        return False
    for root in roots:
        try:
            candidate.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def _prepare_structure(
    *,
    task_name: str,
    structure_path: Optional[str],
    structure_text: Optional[str],
    structure_base64: Optional[str],
    filename: Optional[str],
) -> PreparedStructure:
    provided = [bool(structure_path), bool(structure_text), bool(structure_base64)]
    if sum(provided) != 1:
        raise ValueError("Provide exactly one of structure_path, structure_text, or structure_base64")

    file_bytes: bytes
    source: str
    final_name: str

    if structure_path:
        source_path = Path(structure_path).expanduser().resolve()
        if not source_path.exists() or not source_path.is_file():
            raise ValueError(f"structure_path does not exist or is not a file: {source_path}")
        if not _is_under_allowed_roots(source_path):
            allowed = ", ".join(str(p) for p in settings.mcp_allowed_path_roots_list) or "(none configured)"
            raise ValueError(f"structure_path is outside MCP_ALLOWED_PATH_ROOTS. Allowed roots: {allowed}")
        final_name = _sanitize_filename(filename or source_path.name, fallback=source_path.name)
        file_bytes = source_path.read_bytes()
        source = "path"
    elif structure_text is not None:
        final_name = _sanitize_filename(filename, fallback="structure.cif")
        file_bytes = structure_text.encode("utf-8")
        source = "text"
    else:
        final_name = _sanitize_filename(filename, fallback="structure.cif")
        file_bytes = _decode_base64_content(structure_base64 or "")
        source = "base64"

    if not validate_structure_file(final_name):
        raise ValueError(f"Invalid file type for '{final_name}'. Allowed extensions: {get_allowed_extensions_str()}")

    if len(file_bytes) > settings.max_upload_size_bytes:
        raise ValueError(
            f"File too large ({len(file_bytes)} bytes). Maximum size: {settings.max_upload_size_mb}MB"
        )

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    task_dir = TMP_DIR / f"mcp_{task_name}_{uuid.uuid4().hex}"
    task_dir.mkdir(parents=True, exist_ok=True)
    input_path = task_dir / final_name
    input_path.write_bytes(file_bytes)

    return PreparedStructure(
        input_path=input_path,
        task_dir=task_dir,
        size_bytes=len(file_bytes),
        source=source,
        filename=final_name,
    )


async def _execute_analysis(
    *,
    tool_name: str,
    task_name: str,
    structure_path: Optional[str],
    structure_text: Optional[str],
    structure_base64: Optional[str],
    filename: Optional[str],
    zeo_args: list[str],
    output_files: list[str],
    parser: Callable[[str], Dict[str, Any]],
    response_model: Type[BaseModel],
    force_recalculate: bool,
    ctx: Optional[Context] = None,
) -> Dict[str, Any]:
    async def _progress(step: int) -> None:
        if ctx is not None:
            try:
                await ctx.report_progress(step, 4)
            except Exception:
                pass

    await _progress(1)
    try:
        prepared = _prepare_structure(
            task_name=task_name,
            structure_path=structure_path,
            structure_text=structure_text,
            structure_base64=structure_base64,
            filename=filename,
        )
    except ValueError as exc:
        return _error(tool_name, str(exc), code="INPUT_VALIDATION_ERROR")

    await _progress(2)
    try:
        final_args = zeo_args + [prepared.input_path.name]
        result = await runner.run_command_async(
            structure_file=prepared.input_path,
            zeo_args=final_args,
            output_files=output_files,
            extra_identifier=task_name,
            skip_cache=force_recalculate,
        )
        await _progress(3)

        if not result.get("success"):
            return _error(
                tool_name,
                "Zeo++ execution failed",
                code="ZEOPP_EXECUTION_FAILED",
                details={
                    "exit_code": result.get("exit_code"),
                    "stderr": result.get("stderr", ""),
                },
            )

        main_output = result.get("output_data", {}).get(output_files[0])
        if main_output is None:
            return _error(
                tool_name,
                f"Expected output file not found: {output_files[0]}",
                code="OUTPUT_NOT_FOUND",
            )

        try:
            parsed = parser(main_output)
        except ZeoppParsingError as exc:
            return _error(
                tool_name,
                exc.message,
                code="PARSING_FAILED",
                details=exc.details,
            )
        except Exception as exc:
            return _error(
                tool_name,
                f"Failed to parse Zeo++ output: {exc}",
                code="PARSING_FAILED",
            )

        validated = response_model(**{**parsed, "cached": result.get("cached", False)}).model_dump()
        await _progress(4)
        return _ok(
            tool_name,
            validated,
            cached=result.get("cached", False),
            meta={
                "source": prepared.source,
                "filename": prepared.filename,
                "input_size_bytes": prepared.size_bytes,
            },
        )
    finally:
        cleanup_temp_directory(prepared.task_dir)


def _summarize_psd_histogram(hist_text: str) -> Dict[str, Any]:
    lines = hist_text.splitlines()
    bins: list[tuple[float, float]] = []
    for line in lines:
        item = line.strip()
        if not item or item.startswith("#"):
            continue
        tokens = item.split()
        if len(tokens) < 2:
            continue
        try:
            radius = float(tokens[0])
            value = float(tokens[1])
        except ValueError:
            continue
        bins.append((radius, value))

    if not bins:
        raise ValueError("No numeric bins parsed from .psd_histo output")

    radii = [item[0] for item in bins]
    values = [item[1] for item in bins]
    area = 0.0
    for idx in range(1, len(bins)):
        x0, y0 = bins[idx - 1]
        x1, y1 = bins[idx]
        area += (x1 - x0) * (y0 + y1) * 0.5

    top_peaks = sorted(bins, key=lambda item: item[1], reverse=True)[:5]
    return {
        "bin_count": len(bins),
        "radius_min": min(radii),
        "radius_max": max(radii),
        "value_min": min(values),
        "value_max": max(values),
        "integral_estimate": area,
        "top_peaks": [{"radius": r, "value": v} for r, v in top_peaks],
    }


# =============================================================================
# Tool Registrations (transport-agnostic)
# =============================================================================

@mcp.tool(name="health", description="Get Zeo++ MCP service health status.")
async def tool_health() -> Dict[str, Any]:
    health_payload = {
        "status": "healthy" if _check_zeopp_available() else "degraded",
        "version": settings.version,
        "auth_enabled": bool(settings.mcp_auth_token.strip()),
        "zeopp_available": _check_zeopp_available(),
        "cache_enabled": settings.enable_cache,
        "cache_dir_exists": CACHE_DIR.exists(),
        "tmp_dir_exists": TMP_DIR.exists(),
    }
    return _ok("health", health_payload)


@mcp.tool(name="version", description="Get Zeo++ MCP service version information.")
async def tool_version() -> Dict[str, Any]:
    return _ok(
        "version",
        {
            "service": "Zeo++ MCP Server",
            "version": settings.version,
            "api_version": "v1",
        },
    )


@mcp.tool(name="cache_stats", description="Get cache and temp storage statistics.")
async def tool_cache_stats() -> Dict[str, Any]:
    return _ok(
        "cache_stats",
        {
            "cache": get_cache_storage_stats(),
            "temp": get_temp_storage_stats(),
            "cache_enabled": settings.enable_cache,
        },
    )


@mcp.tool(name="cache_cleanup", description="Clean temporary task directories older than max_age_hours.")
async def tool_cache_cleanup(max_age_hours: float = 24.0) -> Dict[str, Any]:
    if max_age_hours <= 0:
        return _error("cache_cleanup", "max_age_hours must be greater than 0", code="INPUT_VALIDATION_ERROR")
    removed, failed = cleanup_old_temp_files(max_age_hours=max_age_hours)
    return _ok(
        "cache_cleanup",
        {
            "success": failed == 0,
            "max_age_hours": max_age_hours,
            "removed": removed,
            "failed": failed,
        },
    )


@mcp.tool(name="cache_clear", description="Clear all Zeo++ cached entries.")
async def tool_cache_clear() -> Dict[str, Any]:
    removed, failed = clear_all_cache()
    return _ok(
        "cache_clear",
        {
            "success": failed == 0,
            "entries_removed": removed,
            "entries_failed": failed,
        },
    )


@mcp.tool(name="pore_diameter", description="Calculate pore diameter using Zeo++ -res.")
async def tool_pore_diameter(
    structure_path: str | None = None,
    structure_text: str | None = None,
    structure_base64: str | None = None,
    filename: str | None = None,
    ha: bool = True,
    force_recalculate: bool = False,
    ctx: Context = None,
) -> Dict[str, Any]:
    zeo_args = ["-res", "result.res"]
    if ha:
        zeo_args.insert(0, "-ha")
    return await _execute_analysis(
        tool_name="pore_diameter",
        task_name="pore_diameter",
        structure_path=structure_path,
        structure_text=structure_text,
        structure_base64=structure_base64,
        filename=filename,
        zeo_args=zeo_args,
        output_files=["result.res"],
        parser=parse_res_from_text,
        response_model=PoreDiameterResponse,
        force_recalculate=force_recalculate,
        ctx=ctx,
    )


@mcp.tool(name="surface_area", description="Calculate accessible surface area using Zeo++ -sa.")
async def tool_surface_area(
    structure_path: str | None = None,
    structure_text: str | None = None,
    structure_base64: str | None = None,
    filename: str | None = None,
    chan_radius: float = 1.21,
    probe_radius: float = 1.21,
    samples: int = 2000,
    ha: bool = True,
    force_recalculate: bool = False,
    ctx: Context = None,
) -> Dict[str, Any]:
    try:
        _validate_positive("chan_radius", chan_radius)
        _validate_positive("probe_radius", probe_radius)
        if samples <= 0:
            raise ValueError("samples must be greater than 0")
        if probe_radius > chan_radius:
            raise ValueError(
                f"Invalid radii: probe_radius ({probe_radius}) cannot be greater than chan_radius ({chan_radius})."
            )
    except ValueError as exc:
        return _error("surface_area", str(exc), code="INPUT_VALIDATION_ERROR")

    zeo_args = ["-sa", str(chan_radius), str(probe_radius), str(samples), "result.sa"]
    if ha:
        zeo_args.insert(0, "-ha")
    return await _execute_analysis(
        tool_name="surface_area",
        task_name="surface_area",
        structure_path=structure_path,
        structure_text=structure_text,
        structure_base64=structure_base64,
        filename=filename,
        zeo_args=zeo_args,
        output_files=["result.sa"],
        parser=parse_sa_from_text,
        response_model=SurfaceAreaResponse,
        force_recalculate=force_recalculate,
        ctx=ctx,
    )


@mcp.tool(name="accessible_volume", description="Calculate accessible volume using Zeo++ -vol.")
async def tool_accessible_volume(
    structure_path: str | None = None,
    structure_text: str | None = None,
    structure_base64: str | None = None,
    filename: str | None = None,
    chan_radius: float = 1.21,
    probe_radius: float = 1.21,
    samples: int = 50000,
    ha: bool = True,
    force_recalculate: bool = False,
    ctx: Context = None,
) -> Dict[str, Any]:
    try:
        _validate_positive("chan_radius", chan_radius)
        _validate_positive("probe_radius", probe_radius)
        if samples <= 0:
            raise ValueError("samples must be greater than 0")
        if probe_radius > chan_radius:
            raise ValueError(
                f"Invalid radii: probe_radius ({probe_radius}) cannot be greater than chan_radius ({chan_radius})."
            )
    except ValueError as exc:
        return _error("accessible_volume", str(exc), code="INPUT_VALIDATION_ERROR")

    zeo_args = ["-vol", str(chan_radius), str(probe_radius), str(samples), "result.vol"]
    if ha:
        zeo_args.insert(0, "-ha")
    return await _execute_analysis(
        tool_name="accessible_volume",
        task_name="accessible_volume",
        structure_path=structure_path,
        structure_text=structure_text,
        structure_base64=structure_base64,
        filename=filename,
        zeo_args=zeo_args,
        output_files=["result.vol"],
        parser=parse_vol_from_text,
        response_model=AccessibleVolumeResponse,
        force_recalculate=force_recalculate,
        ctx=ctx,
    )


@mcp.tool(name="probe_volume", description="Calculate probe-occupiable volume using Zeo++ -volpo.")
async def tool_probe_volume(
    structure_path: str | None = None,
    structure_text: str | None = None,
    structure_base64: str | None = None,
    filename: str | None = None,
    chan_radius: float = 1.21,
    probe_radius: float = 1.21,
    samples: int = 50000,
    ha: bool = True,
    force_recalculate: bool = False,
    ctx: Context = None,
) -> Dict[str, Any]:
    try:
        _validate_positive("chan_radius", chan_radius)
        _validate_positive("probe_radius", probe_radius)
        if samples <= 0:
            raise ValueError("samples must be greater than 0")
        if probe_radius > chan_radius:
            raise ValueError(
                f"Invalid radii: probe_radius ({probe_radius}) cannot be greater than chan_radius ({chan_radius})."
            )
    except ValueError as exc:
        return _error("probe_volume", str(exc), code="INPUT_VALIDATION_ERROR")

    zeo_args = ["-volpo", str(chan_radius), str(probe_radius), str(samples), "result.volpo"]
    if ha:
        zeo_args.insert(0, "-ha")
    return await _execute_analysis(
        tool_name="probe_volume",
        task_name="probe_volume",
        structure_path=structure_path,
        structure_text=structure_text,
        structure_base64=structure_base64,
        filename=filename,
        zeo_args=zeo_args,
        output_files=["result.volpo"],
        parser=parse_volpo_from_text,
        response_model=ProbeVolumeResponse,
        force_recalculate=force_recalculate,
        ctx=ctx,
    )


@mcp.tool(name="channel_analysis", description="Analyze channel dimensionality using Zeo++ -chan.")
async def tool_channel_analysis(
    structure_path: str | None = None,
    structure_text: str | None = None,
    structure_base64: str | None = None,
    filename: str | None = None,
    probe_radius: float = 1.21,
    ha: bool = True,
    force_recalculate: bool = False,
    ctx: Context = None,
) -> Dict[str, Any]:
    try:
        _validate_positive("probe_radius", probe_radius)
    except ValueError as exc:
        return _error("channel_analysis", str(exc), code="INPUT_VALIDATION_ERROR")

    zeo_args = ["-chan", str(probe_radius), "result.chan"]
    if ha:
        zeo_args.insert(0, "-ha")
    return await _execute_analysis(
        tool_name="channel_analysis",
        task_name="channel_analysis",
        structure_path=structure_path,
        structure_text=structure_text,
        structure_base64=structure_base64,
        filename=filename,
        zeo_args=zeo_args,
        output_files=["result.chan"],
        parser=parse_chan_from_text,
        response_model=ChannelAnalysisResponse,
        force_recalculate=force_recalculate,
        ctx=ctx,
    )


@mcp.tool(name="framework_info", description="Get framework information using Zeo++ -strinfo.")
async def tool_framework_info(
    structure_path: str | None = None,
    structure_text: str | None = None,
    structure_base64: str | None = None,
    filename: str | None = None,
    ha: bool = True,
    force_recalculate: bool = False,
    ctx: Context = None,
) -> Dict[str, Any]:
    zeo_args = ["-strinfo", "result.strinfo"]
    if ha:
        zeo_args.insert(0, "-ha")
    return await _execute_analysis(
        tool_name="framework_info",
        task_name="framework_info",
        structure_path=structure_path,
        structure_text=structure_text,
        structure_base64=structure_base64,
        filename=filename,
        zeo_args=zeo_args,
        output_files=["result.strinfo"],
        parser=parse_strinfo_from_text,
        response_model=FrameworkInfoResponse,
        force_recalculate=force_recalculate,
        ctx=ctx,
    )


@mcp.tool(name="open_metal_sites", description="Count open metal sites using Zeo++ -oms.")
async def tool_open_metal_sites(
    structure_path: str | None = None,
    structure_text: str | None = None,
    structure_base64: str | None = None,
    filename: str | None = None,
    ha: bool = True,
    force_recalculate: bool = False,
    ctx: Context = None,
) -> Dict[str, Any]:
    zeo_args = ["-oms", "result.oms"]
    if ha:
        zeo_args.insert(0, "-ha")
    return await _execute_analysis(
        tool_name="open_metal_sites",
        task_name="open_metal_sites",
        structure_path=structure_path,
        structure_text=structure_text,
        structure_base64=structure_base64,
        filename=filename,
        zeo_args=zeo_args,
        output_files=["result.oms"],
        parser=parse_oms_from_text,
        response_model=OpenMetalSitesResponse,
        force_recalculate=force_recalculate,
        ctx=ctx,
    )


@mcp.tool(name="blocking_spheres", description="Generate blocking sphere summary using Zeo++ -block.")
async def tool_blocking_spheres(
    structure_path: str | None = None,
    structure_text: str | None = None,
    structure_base64: str | None = None,
    filename: str | None = None,
    probe_radius: float = 1.86,
    samples: int = 50000,
    ha: bool = True,
    force_recalculate: bool = False,
    ctx: Context = None,
) -> Dict[str, Any]:
    try:
        _validate_positive("probe_radius", probe_radius)
        if samples <= 0:
            raise ValueError("samples must be greater than 0")
    except ValueError as exc:
        return _error("blocking_spheres", str(exc), code="INPUT_VALIDATION_ERROR")

    zeo_args = ["-block", str(probe_radius), str(samples), "result.block"]
    if ha:
        zeo_args.insert(0, "-ha")
    return await _execute_analysis(
        tool_name="blocking_spheres",
        task_name="blocking_spheres",
        structure_path=structure_path,
        structure_text=structure_text,
        structure_base64=structure_base64,
        filename=filename,
        zeo_args=zeo_args,
        output_files=["result.block"],
        parser=parse_block_from_text,
        response_model=BlockingSpheresResponse,
        force_recalculate=force_recalculate,
        ctx=ctx,
    )


@mcp.tool(name="pore_size_dist_summary", description="Calculate pore size distribution and return histogram summary.")
async def tool_pore_size_dist_summary(
    structure_path: str | None = None,
    structure_text: str | None = None,
    structure_base64: str | None = None,
    filename: str | None = None,
    probe_radius: float = 1.21,
    chan_radius: float | None = None,
    samples: int = 50000,
    ha: bool = True,
    force_recalculate: bool = False,
    preview_lines: int = 20,
    ctx: Context = None,
) -> Dict[str, Any]:
    async def _progress(step: int) -> None:
        if ctx is not None:
            try:
                await ctx.report_progress(step, 4)
            except Exception:
                pass

    try:
        _validate_positive("probe_radius", probe_radius)
        if chan_radius is not None:
            _validate_positive("chan_radius", chan_radius)
        if samples <= 0:
            raise ValueError("samples must be greater than 0")
        if preview_lines <= 0:
            raise ValueError("preview_lines must be greater than 0")
    except ValueError as exc:
        return _error("pore_size_dist_summary", str(exc), code="INPUT_VALIDATION_ERROR")

    effective_chan_radius = chan_radius if chan_radius is not None else probe_radius
    if probe_radius > effective_chan_radius:
        return _error(
            "pore_size_dist_summary",
            f"Invalid radii: probe_radius ({probe_radius}) cannot be greater than chan_radius ({effective_chan_radius}).",
            code="INPUT_VALIDATION_ERROR",
        )

    await _progress(1)
    try:
        prepared = _prepare_structure(
            task_name="pore_size_dist_summary",
            structure_path=structure_path,
            structure_text=structure_text,
            structure_base64=structure_base64,
            filename=filename,
        )
    except ValueError as exc:
        return _error("pore_size_dist_summary", str(exc), code="INPUT_VALIDATION_ERROR")

    await _progress(2)
    try:
        output_filename = f"{prepared.input_path.stem}.psd_histo"
        zeo_args = ["-psd", str(effective_chan_radius), str(probe_radius), str(samples)]
        if ha:
            zeo_args.insert(0, "-ha")
        final_args = zeo_args + [prepared.input_path.name]

        execution = await runner.run_command_async(
            structure_file=prepared.input_path,
            zeo_args=final_args,
            output_files=[output_filename],
            extra_identifier="pore_size_dist_summary",
            skip_cache=force_recalculate,
        )
        await _progress(3)

        if not execution.get("success"):
            return _error(
                "pore_size_dist_summary",
                "Zeo++ execution failed",
                code="ZEOPP_EXECUTION_FAILED",
                details={
                    "exit_code": execution.get("exit_code"),
                    "stderr": execution.get("stderr", ""),
                },
            )

        hist_text = execution.get("output_data", {}).get(output_filename)
        if hist_text is None:
            return _error(
                "pore_size_dist_summary",
                f"Expected output file not found: {output_filename}",
                code="OUTPUT_NOT_FOUND",
            )

        try:
            summary = _summarize_psd_histogram(hist_text)
        except Exception as exc:
            return _error(
                "pore_size_dist_summary",
                f"Failed to parse .psd_histo output: {exc}",
                code="PARSING_FAILED",
            )

        preview = "\n".join(hist_text.splitlines()[:preview_lines])
        result_payload = {
            "cached": bool(execution.get("cached", False)),
            "output_filename": output_filename,
            "summary": summary,
            "histogram_preview": _truncate_text(preview),
        }
        await _progress(4)
        return _ok(
            "pore_size_dist_summary",
            result_payload,
            cached=bool(execution.get("cached", False)),
            meta={
                "source": prepared.source,
                "filename": prepared.filename,
                "input_size_bytes": prepared.size_bytes,
            },
        )
    finally:
        cleanup_temp_directory(prepared.task_dir)
