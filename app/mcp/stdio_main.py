# MCP stdio transport entry point for Zeo++ backend
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2026-03-02
# Version: 0.3.2
#
# Usage (direct):
#   uv run python -m app.mcp.stdio_main
#
# Usage (MCP client config, with uv-managed project):
#   {
#     "zeopp": {
#       "command": "uv",
#       "args": ["run", "--project", "/path/to/zeopp-backend", "python", "-m", "app.mcp.stdio_main"]
#     }
#   }

import os
import sys
from pathlib import Path


def _setup_environment() -> None:
    """
    Set up environment variables for stdio mode BEFORE importing app modules.

    In stdio mode we run locally, so:
    - MCP_ALLOWED_PATH_ROOTS should include the user's home and /tmp
    - Workspace defaults to a local directory
    """
    # Ensure project root is on sys.path so `app.*` imports work
    project_root = str(Path(__file__).resolve().parent.parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Set broader allowed path roots for local stdio mode (unless already set)
    if not os.environ.get("MCP_ALLOWED_PATH_ROOTS"):
        home = str(Path.home())
        os.environ["MCP_ALLOWED_PATH_ROOTS"] = f"{home},/tmp,/shared"

    # Default workspace to a local directory (unless already set)
    if not os.environ.get("ZEO_WORKSPACE"):
        default_workspace = Path(project_root) / "workspace"
        default_workspace.mkdir(parents=True, exist_ok=True)
        os.environ["ZEO_WORKSPACE"] = str(default_workspace)


def main() -> None:
    """Bootstrap Zeo++ and start the MCP server with stdio transport."""
    # 1. Setup environment FIRST (before any app.* imports)
    _setup_environment()

    # 2. Bootstrap: check / install Zeo++
    from app.mcp.bootstrap import BootstrapError, bootstrap

    try:
        zeo_path = bootstrap()
    except BootstrapError as exc:
        print(f"\033[0;31m[FATAL]\033[0m {exc}", file=sys.stderr, flush=True)
        sys.exit(1)

    # Set the exec path so config picks it up
    os.environ["ZEO_EXEC_PATH"] = zeo_path

    # 3. Now import the MCP tools (which triggers config loading)
    from app.mcp.tools import mcp  # noqa: E402

    # 4. Run MCP server with stdio transport
    print(
        f"\033[0;32m[zeopp-mcp]\033[0m Starting stdio transport "
        f"(Zeo++ binary: {zeo_path})",
        file=sys.stderr,
        flush=True,
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
