# Zeo++ Bootstrap - Auto-detect and install Zeo++ before starting MCP server
# -*- coding: utf-8 -*-
# Author: Shibo Li
# Date: 2026-03-02
# Version: 0.3.2

"""
Bootstrap module for Zeo++ stdio MCP server.

Responsibilities:
  1. Check system dependencies (gcc, g++, make, wget/curl)
  2. Check if Zeo++ 'network' binary is available
  3. If not, automatically download, compile, and install it
  4. Update ZEO_EXEC_PATH so the MCP server can find it

This module is called before the MCP server starts, ensuring Zeo++ is ready.
"""

import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


# ── Constants ───────────────────────────────────────────────────────────────
ZEO_VERSION = "0.3"
ZEO_FILENAME = f"zeo++-{ZEO_VERSION}.tar.gz"
ZEO_URL = f"http://www.zeoplusplus.org/{ZEO_FILENAME}"
DEFAULT_INSTALL_PREFIX = Path.home() / ".local"
BINARY_NAME = "network"


class BootstrapError(RuntimeError):
    """Raised when bootstrap cannot complete successfully."""


# ── Coloured console output (works on most terminals) ──────────────────────
def _green(msg: str) -> str:
    return f"\033[0;32m{msg}\033[0m"


def _yellow(msg: str) -> str:
    return f"\033[0;33m{msg}\033[0m"


def _red(msg: str) -> str:
    return f"\033[0;31m{msg}\033[0m"


def _info(msg: str) -> None:
    print(_green("[bootstrap]") + f" {msg}", file=sys.stderr, flush=True)


def _warn(msg: str) -> None:
    print(_yellow("[bootstrap]") + f" {msg}", file=sys.stderr, flush=True)


def _error(msg: str) -> None:
    print(_red("[bootstrap]") + f" {msg}", file=sys.stderr, flush=True)


# ── Tool detection ──────────────────────────────────────────────────────────
def _which(name: str) -> str | None:
    """Find an executable on PATH, returning its full path or None."""
    return shutil.which(name)


def check_system_dependencies() -> dict[str, str | None]:
    """
    Check that required build tools are available.

    Returns a dict mapping tool name → path (or None if missing).
    """
    tools = {
        "gcc": _which("gcc"),
        "g++": _which("g++"),
        "make": _which("make"),
        "wget": _which("wget"),
        "curl": _which("curl"),
    }
    return tools


def ensure_system_dependencies() -> None:
    """
    Verify required system dependencies are present.
    Raises BootstrapError with install instructions if something is missing.
    """
    tools = check_system_dependencies()

    missing_build: list[str] = []
    for name in ("gcc", "g++", "make"):
        if tools[name] is None:
            missing_build.append(name)

    has_downloader = tools["wget"] is not None or tools["curl"] is not None

    problems: list[str] = []
    if missing_build:
        problems.append(f"Missing build tools: {', '.join(missing_build)}")
    if not has_downloader:
        problems.append("Missing download tool: need at least 'wget' or 'curl'")

    if problems:
        msg = (
            "System dependency check failed:\n"
            + "\n".join(f"  • {p}" for p in problems)
            + "\n\nOn Ubuntu/Debian, install with:\n"
            "  sudo apt-get update && sudo apt-get install -y build-essential wget curl\n"
        )
        raise BootstrapError(msg)

    _info("System dependencies OK:")
    _info(f"  gcc:  {tools['gcc']}")
    _info(f"  g++:  {tools['g++']}")
    _info(f"  make: {tools['make']}")
    downloader = tools["wget"] or tools["curl"]
    _info(f"  downloader: {downloader}")


# ── Zeo++ detection ────────────────────────────────────────────────────────
def find_network_binary(extra_search_paths: list[str] | None = None) -> str | None:
    """
    Look for the Zeo++ 'network' binary.

    Search order:
      1. ZEO_EXEC_PATH environment variable
      2. Explicit extra_search_paths
      3. ~/.local/bin/network
      4. System PATH
    """
    # 1. Env var
    env_path = os.environ.get("ZEO_EXEC_PATH", "").strip()
    if env_path:
        p = Path(env_path).expanduser().resolve()
        if p.is_file() and os.access(p, os.X_OK):
            return str(p)

    # 2. Extra search paths
    for candidate in (extra_search_paths or []):
        p = Path(candidate).expanduser().resolve()
        if p.is_file() and os.access(p, os.X_OK):
            return str(p)

    # 3. Default install location
    default_bin = DEFAULT_INSTALL_PREFIX / "bin" / BINARY_NAME
    if default_bin.is_file() and os.access(default_bin, os.X_OK):
        return str(default_bin)

    # 4. System PATH
    found = _which(BINARY_NAME)
    if found:
        return found

    return None


# ── Compilation ─────────────────────────────────────────────────────────────
def _run_cmd(cmd: list[str], cwd: Path, label: str) -> None:
    """Run a command, raising BootstrapError on failure."""
    _info(f"{label}: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise BootstrapError(
            f"{label} failed (exit {result.returncode}):\n"
            f"  stdout: {result.stdout[-500:]}\n"
            f"  stderr: {result.stderr[-500:]}"
        )


def download_and_compile(install_prefix: Path | None = None) -> str:
    """
    Download Zeo++ source, compile voro++ and zeo++, install the network binary.

    Args:
        install_prefix: Where to install (default ~/.local). Binary goes to prefix/bin/network.

    Returns:
        Absolute path to the installed 'network' binary.
    """
    if platform.system() == "Windows":
        raise BootstrapError(
            "Automatic Zeo++ compilation is only supported on Linux/macOS. "
            "On Windows, please use the Docker-based deployment."
        )

    prefix = (install_prefix or DEFAULT_INSTALL_PREFIX).expanduser().resolve()
    bin_dir = prefix / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)

    tools = check_system_dependencies()
    has_wget = tools["wget"] is not None

    build_dir = Path(tempfile.mkdtemp(prefix="zeopp-build-"))
    _info(f"Build directory: {build_dir}")

    try:
        # Download
        _info(f"Downloading Zeo++ v{ZEO_VERSION} from {ZEO_URL} ...")
        archive = build_dir / ZEO_FILENAME
        if has_wget:
            _run_cmd(["wget", "-q", "-O", str(archive), ZEO_URL], build_dir, "Download (wget)")
        else:
            _run_cmd(["curl", "-fSL", "-o", str(archive), ZEO_URL], build_dir, "Download (curl)")

        # Extract
        _info("Extracting archive ...")
        _run_cmd(["tar", "-xzf", str(archive)], build_dir, "Extract")

        zeo_src = build_dir / f"zeo++-{ZEO_VERSION}"
        if not zeo_src.is_dir():
            raise BootstrapError(f"Expected source directory not found: {zeo_src}")

        # Compile voro++
        _info("Compiling Voro++ ...")
        nproc = str(os.cpu_count() or 1)
        _run_cmd(["make", f"-j{nproc}"], zeo_src / "voro++" / "src", "Compile Voro++")

        # Compile Zeo++
        _info("Compiling Zeo++ ...")
        _run_cmd(["make", f"-j{nproc}"], zeo_src, "Compile Zeo++")

        # Verify
        compiled_binary = zeo_src / BINARY_NAME
        if not compiled_binary.is_file():
            raise BootstrapError(f"Compilation succeeded but binary not found at {compiled_binary}")

        # Install
        dest = bin_dir / BINARY_NAME
        shutil.copy2(str(compiled_binary), str(dest))
        dest.chmod(0o755)
        _info(f"Installed Zeo++ binary to: {dest}")

        return str(dest)

    finally:
        # Cleanup build directory
        _info("Cleaning up build directory ...")
        shutil.rmtree(build_dir, ignore_errors=True)


# ── Main bootstrap entry point ──────────────────────────────────────────────
def bootstrap(
    install_prefix: Path | None = None,
    extra_search_paths: list[str] | None = None,
) -> str:
    """
    Ensure Zeo++ is available. If not found, check system deps, compile, and install.

    Args:
        install_prefix: Installation prefix (default: ~/.local)
        extra_search_paths: Additional paths to search for the 'network' binary

    Returns:
        Absolute path to the 'network' binary.

    Raises:
        BootstrapError: If system dependencies are missing or compilation fails.
    """
    _info("Checking for Zeo++ 'network' binary ...")

    binary_path = find_network_binary(extra_search_paths)
    if binary_path:
        _info(f"Found Zeo++ binary: {binary_path}")
        # Verify it actually runs
        try:
            result = subprocess.run(
                [binary_path],
                capture_output=True,
                text=True,
                timeout=10,
            )
            # network with no args typically returns non-zero but prints usage — that's fine
            _info(f"Binary responds (exit code {result.returncode}). Zeo++ is ready.")
        except FileNotFoundError:
            _warn(f"Binary at {binary_path} exists but is not executable. Will recompile.")
            binary_path = None
        except Exception as exc:
            _warn(f"Binary verification failed: {exc}. Will recompile.")
            binary_path = None

    if binary_path:
        os.environ["ZEO_EXEC_PATH"] = binary_path
        return binary_path

    # Not found → compile
    _info("Zeo++ binary not found. Starting automatic installation ...")
    ensure_system_dependencies()
    binary_path = download_and_compile(install_prefix)
    os.environ["ZEO_EXEC_PATH"] = binary_path
    _info("Bootstrap complete.")
    return binary_path


if __name__ == "__main__":
    try:
        path = bootstrap()
        print(f"Zeo++ ready: {path}")
    except BootstrapError as exc:
        _error(str(exc))
        sys.exit(1)
