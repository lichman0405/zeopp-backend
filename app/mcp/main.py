# MCP server for Zeo++ backend (Streamable HTTP transport)
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2026-02-26
# Updated: 2026-03-02 - Refactored: tools extracted to tools.py, this file is HTTP-only
# Version: 0.3.2
#
# This module provides the HTTP (Streamable HTTP) transport for the MCP server.
# For stdio transport, use stdio_main.py instead.
#
# Usage:
#   uvicorn app.mcp.main:app --host 0.0.0.0 --port 8000

from datetime import datetime, timezone
from typing import Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.api.health import _check_zeopp_available
from app.core.config import settings

# Import the shared MCP instance (with all tools already registered)
from app.mcp.tools import MCP_PATH, mcp  # noqa: F401


# ── HTTP transport setup ────────────────────────────────────────────────────

# Configure HTTP-specific settings on the mcp instance
mcp._host = "0.0.0.0"
mcp._streamable_http_path = MCP_PATH

app = mcp.streamable_http_app()


# ── HTTP middleware ─────────────────────────────────────────────────────────

class MCPAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Response:
        token = settings.mcp_auth_token.strip()
        if token and _is_mcp_transport_path(request.url.path):
            header = request.headers.get("authorization", "")
            if header != f"Bearer {token}":
                return JSONResponse(
                    {"ok": False, "error_code": "UNAUTHORIZED", "message": "Missing or invalid bearer token"},
                    status_code=401,
                    headers={"WWW-Authenticate": "Bearer"},
                )
        return await call_next(request)


def _is_mcp_transport_path(path: str) -> bool:
    if MCP_PATH == "/":
        return path not in {"/health", "/version", "/"}
    return path == MCP_PATH or path.startswith(MCP_PATH + "/")


app.add_middleware(MCPAuthMiddleware)


# ── HTTP routes (health, version, root) ─────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _root(_: Request) -> Response:
    return JSONResponse(
        {
            "service": "Zeo++ MCP Server",
            "version": settings.version,
            "mcp_path": MCP_PATH,
            "health": "/health",
        }
    )


async def _health(_: Request) -> Response:
    return JSONResponse(
        {
            "status": "healthy" if _check_zeopp_available() else "degraded",
            "version": settings.version,
            "timestamp": _now_iso(),
            "mcp_path": MCP_PATH,
            "auth_enabled": bool(settings.mcp_auth_token.strip()),
            "zeopp_available": _check_zeopp_available(),
            "cache_enabled": settings.enable_cache,
        }
    )


async def _version(_: Request) -> Response:
    return JSONResponse(
        {
            "service": "Zeo++ MCP Server",
            "version": settings.version,
            "api_version": "v1",
            "transport": "streamable_http",
            "mcp_path": MCP_PATH,
        }
    )


app.add_route("/", _root, methods=["GET"])
app.add_route("/health", _health, methods=["GET"])
app.add_route("/version", _version, methods=["GET"])
