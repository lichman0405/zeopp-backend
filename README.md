<div align="center">
  <a href="https://github.com/lichman0405/zeopp-backend.git">
    <img src="assets/edit_logo.png" alt="Logo" width="200px">
  </a>
  
  <h1 align="center">Zeo++ API & MCP Service</h1>
  
  <p align="center">
    A production-ready Zeo++ structural analysis service supporting both HTTP API and stdio MCP modes for seamless Agent integration.
    <br>
    <a href="./README.md"><strong>English</strong></a>
    ·
    <a href="https://github.com/lichman0405/zeopp-backend.git/issues">Report Bug</a>
    ·
    <a href="https://github.com/lichman0405/zeopp-backend.git/issues">New Feature</a>
  </p>
</div>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker)
[![GitHub issues](https://img.shields.io/github/issues/lichman0405/zeopp-backend.svg)](https://github.com/lichman0405/zeopp-backend/issues)
[![GitHub stars](https://img.shields.io/github/stars/lichman0405/zeopp-backend.svg?style=social)](https://github.com/lichman0405/zeopp-backend.git])

</div>

This project addresses the pain points of using Zeo++ directly: it transforms complex command-line operations into simple API calls and provides automatic caching, structured output, and a containerized environment for easy deployment.

## 🚀 Key Features

- ✅ **Modern API**: Access Zeo++ core analysis functions via HTTP endpoints
- 🧠 **Smart Caching**: Automatically cache computation results, instant response for identical inputs (with `force_recalculate` option)
- 📂 **Structured Output**: Clear, easy-to-process JSON responses
- ⚙️ **Type-Safe Configuration**: Pydantic Settings for validated environment configuration
- 🐳 **Docker Ready**: Multi-stage build with automatic Zeo++ compilation
- 🎨 **Rich Logging**: Beautiful and informative console logs
- 🔒 **Security Hardened**: Rate limiting, file validation, request tracking
- 📊 **Observability**: Prometheus metrics endpoint for monitoring
- 🧪 **Test Coverage**: Comprehensive unit and integration test suite
- 🤖 **Dual MCP Transport**: Supports both **stdio** (recommended) and Streamable HTTP, for agent integration (featherflow / nanobot-style runtimes)

## 📚 Documentation

For detailed usage, please refer to:

- [**API Documentation**](./docs/API_DOCUMENTATION_EN.md): Complete API reference with parameters and examples
- [**Usage Examples**](./examples/): Python and cURL examples with sample structure files

## ⚡ Quick Start

### Requirements

- Docker and Docker Compose  
  or
- Python 3.10+ and [uv](https://docs.astral.sh/uv/) (recommended)
  or
- Python 3.10+ and pip

### Method 1: Using Docker (Recommended)

#### Create Configuration File

Copy `.env.example` to `.env` and modify as needed:

```bash
cp .env.example .env
```

For Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Common configuration options:

```ini
# .env

# Service port (external access port)
HOST_PORT=9876
MCP_HOST_PORT=9877

# Application settings
ENABLE_CACHE=true
LOG_LEVEL=INFO
CORS_ORIGINS=*
RATE_LIMIT_REQUESTS=100
MAX_UPLOAD_SIZE_MB=50
# Performance configuration
UVICORN_WORKERS=2           # Worker processes, recommended to set to CPU cores
MAX_CONCURRENT_TASKS=4      # Maximum concurrent Zeo++ tasks
# MCP settings
MCP_AUTH_TOKEN=             # Strongly recommended in production
MCP_STREAMABLE_HTTP_PATH=/mcp
MCP_ALLOWED_PATH_ROOTS=/app/workspace,/shared
# Resource limits
CPU_LIMIT=2
MEMORY_LIMIT=2G
```

> 💡 **Tip**: All configuration options are documented in `.env.example`. No need to modify `docker-compose.yml`.

#### Launch with One Command

In the project root directory, run:

```bash
docker-compose up --build -d
```

Docker will automatically build the image (including downloading and compiling Zeo++) and start the service at `http://localhost:${HOST_PORT}` (default: 9876).

### Method 2: Local Development with uv (Recommended)

[uv](https://docs.astral.sh/uv/) is an ultra-fast Python package manager written in Rust. One command handles virtual environment creation and dependency installation.

#### Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Clone and Install

```bash
git clone https://github.com/lichman0405/zeopp-backend.git
cd zeopp-backend
uv sync
```

> `uv sync` automatically creates a `.venv` virtual environment and installs all dependencies. No manual `python -m venv` needed.

#### Configure Environment

Create a `.env` file and ensure `ZEO_EXEC_PATH` points to your Zeo++ executable (or use stdio mode for automatic compilation).

#### Run API Service

```bash
uv run uvicorn app.main:app --reload
```

#### Run stdio MCP Service

The stdio mode will **automatically detect and compile Zeo++** on first launch (requires `gcc`, `g++`, `make`, `wget`/`curl`):

```bash
uv run python -m app.mcp.stdio_main
```

### Method 3: Local Development with pip

#### Install Zeo++

Ensure you have installed Zeo++ following the official instructions and can invoke it using the `network` command in your terminal.

#### Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### Configure Environment

Create a `.env` file and ensure `ZEO_EXEC_PATH` points to your Zeo++ (or `network`) executable.

#### Run the Service

```bash
uvicorn app.main:app --reload
```

## 📋 Usage Example

Once the project is running, you can call the API using any HTTP client.

### Test Health Checks

```bash
# Basic health check
curl http://localhost:9876/health

# Detailed health check
curl http://localhost:9876/health/detailed

# Get version information
curl http://localhost:9876/version
```

### Call Analysis Endpoints

Example: compute pore diameter using `curl`

```bash
curl -X 'POST' \
  'http://localhost:9876/api/v1/pore_diameter' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'structure_file=@/path/to/your/file.cif' \
  -F 'ha=true'
```

Replace `/path/to/your/file.cif` with the actual path to your local structure file. Parameters (e.g., `ha=true`) are sent as form fields using `-F`.

### MCP (for agent callers)

#### Option A: stdio Mode (Recommended)

stdio MCP runs as a subprocess — no Docker required. Zeo++ is automatically compiled on first launch.

**featherflow integration** (`~/.featherflow/config.json`):

```json
{
  "tools": {
    "mcpServers": {
      "zeopp": {
        "command": "uv",
        "args": ["run", "--project", "/path/to/zeopp-backend", "python", "-m", "app.mcp.stdio_main"],
        "toolTimeout": 300,
        "progressIntervalSeconds": 15
      }
    }
  }
}
```

> **Config notes**:
> - Replace `/path/to/zeopp-backend` with the actual project path
> - `toolTimeout`: seconds before a tool call is cancelled (Zeo++ on large structures can be slow; recommended 300–600)
> - `progressIntervalSeconds`: heartbeat interval during long-running calls (default 15s, 0 = off)
>
> **stdio advantage**: the MCP process runs on the host, so `structure_path` accepts local file paths directly (e.g. `/home/user/structures/MOF.cif`) — no need to pass file content via `structure_text`.
>
> **On first launch**, bootstrap will automatically:
> 1. Check that `gcc`, `g++`, `make`, `wget`/`curl` are available
> 2. Detect whether the Zeo++ `network` binary exists
> 3. If not found, download, compile, and install to `~/.local/bin/`
>
> System dependency install (Ubuntu): `sudo apt-get install -y build-essential wget curl`

<details>
<summary>Other MCP clients (Cursor, etc.) config format</summary>

```json
{
  "mcpServers": {
    "zeopp": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/zeopp-backend", "python", "-m", "app.mcp.stdio_main"]
    }
  }
}
```

</details>

**Or use the one-shot setup script** (compiles Zeo++ then registers it in featherflow):

```bash
# Run from the project root; --lazy spawns the process only on first tool call
bash scripts/add_to_featherflow.sh --lazy

# With a custom timeout
bash scripts/add_to_featherflow.sh --timeout 600 --lazy
```

The script runs two steps internally:
1. `uv run python -m app.mcp.bootstrap` — detects and compiles Zeo++ (skipped if already installed)
2. `featherflow config mcp add zeopp ...` — writes the entry to `~/.featherflow/config.json`

<details>
<summary>Manual two-step equivalent</summary>

```bash
# Step 1: compile/install Zeo++ (instant if already present)
uv run python -m app.mcp.bootstrap

# Step 2: register the MCP server
featherflow config mcp add zeopp \
  --command uv \
  --arg run --arg --project --arg /path/to/zeopp-backend \
  --arg python --arg -m --arg app.mcp.stdio_main \
  --timeout 300 \
  --lazy \
  --description "Zeo++ porous material analysis: pore diameter, surface area, channel analysis, OMS"

# Verify (the Lazy column shows yes/no)
featherflow config mcp list
```

> `--lazy`: deferred-start mode — the process is only spawned when a zeopp tool is first called, so it does not affect agent startup time. Recommended for on-demand services like Zeo++.

</details>

#### Option B: HTTP Mode (Docker)

Launch MCP service (already included as `zeopp-mcp` in Docker Compose):

```bash
docker-compose up -d zeopp-mcp
```

Default MCP endpoint: `http://localhost:9877/mcp`

featherflow config (`~/.featherflow/config.json`):

```json
{
  "tools": {
    "mcpServers": {
      "zeopp": {
        "url": "http://localhost:9877/mcp",
        "headers": {
          "Authorization": "Bearer <MCP_AUTH_TOKEN>"
        },
        "toolTimeout": 300,
        "progressIntervalSeconds": 15
      }
    }
  }
}
```

> **Note**: In HTTP mode the MCP server runs inside a Docker container and cannot access the host filesystem. Use `structure_text` (pass file content) instead of `structure_path` when calling tools.

#### stdio vs HTTP Comparison

| Feature | stdio (Recommended) | HTTP (Docker) |
|---------|-------------------|---------------|
| Transport | Subprocess stdin/stdout | HTTP requests |
| Deployment | No Docker needed, uv one-liner | Requires Docker |
| File Access | ✅ Direct host filesystem (`structure_path`) | ❌ Must pass `structure_text` content |
| Zeo++ Install | Auto-compiled on first run | Auto-compiled inside Docker |
| featherflow Integration | `command` + `args` | `url` + `headers` |
| Best For | Agent integration (featherflow recommended) | Standalone HTTP service, multi-user sharing |

### Interactive Documentation

Visit the Swagger UI for interactive testing: [http://localhost:9876/docs](http://localhost:9876/docs)

## 📚 API Reference

### System Endpoints

| Path | Function |
| --- | --- |
| `/` | Root endpoint returning service name, version, and docs entry |
| `/health` | Basic health check to verify the service is running |
| `/health/detailed` | Detailed health check with system information and Zeo++ availability |
| `/version` | Get API version information |
| `/metrics` | Prometheus metrics endpoint for monitoring systems |
| `/api/v1/metrics/summary` | JSON format metrics summary |
| `/api/v1/cache/stats` | Cache statistics |
| `/api/v1/cache/cleanup` | Clean up old temporary files |
| `/api/v1/cache/clear` | Clear all cache |
| `MCP service: /mcp` | Streamable HTTP MCP endpoint (default on port 9877) |
| `MCP stdio` | stdio transport MCP (via `python -m app.mcp.stdio_main`) |

### Core Geometry Analysis (v1 API)

All endpoints require a `structure_file` uploaded as a file.

| Path | Function |
| --- | --- |
| `/api/v1/pore_diameter` → Zeo++ `-res` | Compute the largest included sphere (Di) and largest free sphere (Df) diameters |
| `/api/v1/surface_area` → Zeo++ `-sa` | Compute accessible surface area using Monte Carlo sampling |
| `/api/v1/accessible_volume` → Zeo++ `-vol` | Compute the accessible volume for a given probe |
| `/api/v1/probe_volume` → Zeo++ `-volpo` | Compute the probe-occupiable volume for a specific point or region |
| `/api/v1/channel_analysis` → Zeo++ `-chan` | Identify and analyze channels |
| `/api/v1/pore_size_dist/download` → Zeo++ `-psd` | Download pore size distribution histogram data file |
| `/api/v1/blocking_spheres` → Zeo++ `-block` | Identify inaccessible regions and generate blocking spheres |

### Structural Information Analysis (v1 API)

| Path | Function |
| --- | --- |
| `/api/v1/framework_info` → Zeo++ `-strinfo` | Identify the number of frameworks and their dimensionality |
| `/api/v1/open_metal_sites` → Zeo++ `-oms` | Compute the number of open metal sites |

## 🔄 Version Information

**Current Version: v0.3.2**

### New Features (v0.3.2)
- 🔌 **stdio MCP Transport**: New stdio mode, unifying interaction pattern with other MCP services
- 🛠️ **Zeo++ Auto-Install**: Automatic system dependency check, download, and compilation on first launch
- 📦 **uv Support**: Recommended `uv` for virtual environment and dependency management (significantly faster)
- 🧩 **MCP Code Refactor**: Tools decoupled from transport; HTTP and stdio share the same tool codebase

### v0.3.1 Features
- 🔒 **Security Enhancements**: Rate limiting (slowapi), file upload validation, request ID tracking
- 📊 **Prometheus Monitoring**: `/metrics` endpoint for monitoring system scraping
- 🗂️ **Cache Management API**: View stats, cleanup temp files, clear cache
- 🧪 **Test Suite**: Complete pytest unit tests and API integration tests
- 🐳 **Docker Optimization**: Multi-stage build, non-root user, health checks
- 📝 **Complete Documentation**: Zeo++ command reference and API mapping guide
- 🤖 **MCP Service**: Streamable HTTP MCP endpoint and integration documentation

### v0.3.0 Features
- ✅ API Versioning: All analysis endpoints use `/api/v1/` prefix
- ✅ Health Check Endpoints: `/health` and `/health/detailed`
- ✅ Improved Error Handling: Custom exception types with detailed error messages

## 🧪 Development & Testing

### Run Tests
```bash
# Using uv
uv sync --group dev
uv run pytest tests/ -v

# Or using pip
pip install -r requirements-dev.txt
pytest tests/ -v
```

### Development Mode
```bash
# Local API service
uv run uvicorn app.main:app --reload

# Local stdio MCP (auto-compiles Zeo++)
uv run python -m app.mcp.stdio_main

# Docker development mode
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 📜 License

MIT © Shibo Li, 2025
