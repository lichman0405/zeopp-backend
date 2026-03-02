#!/usr/bin/env bash
# add_to_featherflow.sh
# One-shot: compile/install Zeo++ then register zeopp as an MCP server in featherflow.
#
# Usage:
#   bash scripts/add_to_featherflow.sh [--timeout <seconds>] [--lazy]
#
# Examples:
#   bash scripts/add_to_featherflow.sh
#   bash scripts/add_to_featherflow.sh --timeout 600 --lazy

set -euo pipefail

# ── Defaults ────────────────────────────────────────────────────────────────
TIMEOUT=300
LAZY_FLAG=""
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

# ── Argument parsing ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --timeout)
      TIMEOUT="$2"; shift 2 ;;
    --lazy)
      LAZY_FLAG="--lazy"; shift ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Usage: $0 [--timeout <seconds>] [--lazy]" >&2
      exit 1 ;;
  esac
done

echo "============================================"
echo " Step 1: Compile / install Zeo++ (bootstrap)"
echo "============================================"
cd "${PROJECT_DIR}"
uv run python -m app.mcp.bootstrap

echo ""
echo "============================================"
echo " Step 2: Register zeopp in featherflow"
echo "============================================"
featherflow config mcp add zeopp \
  --command uv \
  --arg run --arg --project --arg "${PROJECT_DIR}" \
  --arg python --arg -m --arg app.mcp.stdio_main \
  --timeout "${TIMEOUT}" \
  ${LAZY_FLAG} \
  --description "Zeo++ porous material analysis: pore diameter, surface area, channel analysis, OMS"

echo ""
echo "✅  Done! Verify with:  featherflow config mcp list"
