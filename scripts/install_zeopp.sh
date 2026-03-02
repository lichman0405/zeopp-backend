#!/usr/bin/env bash
# =============================================================================
# Zeo++ Auto-Install Script for Ubuntu/Debian
# =============================================================================
# This script checks system dependencies, downloads, compiles, and installs
# the Zeo++ network binary. Intended to be called by the stdio MCP bootstrap
# or run manually.
#
# Usage:
#   bash scripts/install_zeopp.sh [--prefix PREFIX]
#
# Options:
#   --prefix PREFIX   Installation prefix (default: ~/.local)
#
# The compiled 'network' binary will be placed at PREFIX/bin/network.
# =============================================================================

set -euo pipefail

# ── Defaults ────────────────────────────────────────────────────────────────
ZEO_VERSION="0.3"
ZEO_FILENAME="zeo++-${ZEO_VERSION}.tar.gz"
ZEO_URL="http://www.zeoplusplus.org/${ZEO_FILENAME}"
PREFIX="${HOME}/.local"
BUILD_DIR="/tmp/zeopp-build-$$"

# ── Parse arguments ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --prefix)
            PREFIX="$2"; shift 2 ;;
        --prefix=*)
            PREFIX="${1#*=}"; shift ;;
        *)
            echo "Unknown option: $1"; exit 1 ;;
    esac
done

INSTALL_BIN="${PREFIX}/bin"

# ── Color helpers ───────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'; NC='\033[0m'
info()  { echo -e "${GREEN}[INFO]${NC}  $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; }

# ── 1. Check if network binary already exists ──────────────────────────────
if command -v network &>/dev/null; then
    info "Zeo++ 'network' binary already available: $(command -v network)"
    network 2>&1 | head -1 || true
    info "Skipping installation. Remove it first if you want to reinstall."
    exit 0
fi

if [[ -x "${INSTALL_BIN}/network" ]]; then
    info "Zeo++ 'network' binary found at ${INSTALL_BIN}/network"
    info "Skipping installation. Remove it first if you want to reinstall."
    exit 0
fi

# ── 2. Check system dependencies ───────────────────────────────────────────
info "Checking system dependencies..."

MISSING=()

for cmd in gcc g++ make; do
    if ! command -v "$cmd" &>/dev/null; then
        MISSING+=("$cmd")
    fi
done

# Check for wget or curl (need at least one)
HAS_WGET=false; HAS_CURL=false
command -v wget &>/dev/null && HAS_WGET=true
command -v curl &>/dev/null && HAS_CURL=true

if ! $HAS_WGET && ! $HAS_CURL; then
    MISSING+=("wget or curl")
fi

if [[ ${#MISSING[@]} -gt 0 ]]; then
    error "Missing required tools: ${MISSING[*]}"
    echo ""
    echo "On Ubuntu/Debian, install them with:"
    echo "  sudo apt-get update && sudo apt-get install -y build-essential wget curl"
    echo ""
    exit 1
fi

info "All system dependencies satisfied."
info "  gcc:  $(gcc --version | head -1)"
info "  g++:  $(g++ --version | head -1)"
info "  make: $(make --version | head -1)"

# ── 3. Download Zeo++ source ───────────────────────────────────────────────
info "Creating build directory: ${BUILD_DIR}"
mkdir -p "${BUILD_DIR}"

cleanup() {
    info "Cleaning up build directory..."
    rm -rf "${BUILD_DIR}"
}
trap cleanup EXIT

cd "${BUILD_DIR}"

info "Downloading Zeo++ v${ZEO_VERSION} from ${ZEO_URL} ..."
if $HAS_WGET; then
    wget -q --show-progress -O "${ZEO_FILENAME}" "${ZEO_URL}"
elif $HAS_CURL; then
    curl -fSL -o "${ZEO_FILENAME}" "${ZEO_URL}"
fi

info "Extracting ${ZEO_FILENAME} ..."
tar -xzf "${ZEO_FILENAME}"

# ── 4. Compile Voro++ (dependency) ──────────────────────────────────────────
ZEO_SRC="${BUILD_DIR}/zeo++-${ZEO_VERSION}"

info "Compiling Voro++ ..."
cd "${ZEO_SRC}/voro++/src"
make -j"$(nproc)" 2>&1 | tail -3

# ── 5. Compile Zeo++ ───────────────────────────────────────────────────────
info "Compiling Zeo++ ..."
cd "${ZEO_SRC}"
make -j"$(nproc)" 2>&1 | tail -3

# ── 6. Verify compilation ──────────────────────────────────────────────────
if [[ ! -f "${ZEO_SRC}/network" ]]; then
    error "Compilation failed: '${ZEO_SRC}/network' not found."
    exit 1
fi

info "Compilation successful."

# ── 7. Install binary ──────────────────────────────────────────────────────
mkdir -p "${INSTALL_BIN}"
cp "${ZEO_SRC}/network" "${INSTALL_BIN}/network"
chmod +x "${INSTALL_BIN}/network"

info "Installed Zeo++ 'network' to: ${INSTALL_BIN}/network"

# ── 8. Check PATH ──────────────────────────────────────────────────────────
if ! echo "$PATH" | tr ':' '\n' | grep -qx "${INSTALL_BIN}"; then
    warn "${INSTALL_BIN} is not in your PATH."
    echo ""
    echo "Add the following line to your ~/.bashrc or ~/.profile:"
    echo "  export PATH=\"${INSTALL_BIN}:\$PATH\""
    echo ""
    echo "Or set ZEO_EXEC_PATH in your .env file:"
    echo "  ZEO_EXEC_PATH=${INSTALL_BIN}/network"
    echo ""
fi

info "Zeo++ installation complete!"
echo ""
echo "  Binary:  ${INSTALL_BIN}/network"
echo "  Version: Zeo++ v${ZEO_VERSION}"
echo ""
