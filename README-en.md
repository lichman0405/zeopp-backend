<div align="center">
  <a href="https://github.com/lichman0405/zeopp-backend.git">
    <img src="assets/edit_logo.png" alt="Logo" width="200px">
  </a>
  
  <h1 align="center">Zeo++ API Service</h1>
  
  <p align="center">
    A production-ready FastAPI service that wraps the powerful Zeo++ structural analysis capabilities into modern, containerized HTTP endpoints.
    <br>
    <a href="./README-en.md"><strong>English</strong></a>
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

- ✅ **Modern API**: Access Zeo++ core analysis functions via HTTP endpoints.
- 🧠 **Smart Caching**: Automatically cache computation results for identical inputs, returning results instantly to avoid redundant calculations.
- 📂 **Structured Output**: Responses are returned in clear, easy-to-process JSON format.
- ⚙️ **Flexible Configuration**: Easily configure Zeo++ path and working directory via a `.env` file.
- 🐳 **Docker Ready**: Use Docker and docker-compose to launch the service with one command; automatically handles Zeo++ download and compilation.
- 🎨 **Rich Logging**: Beautiful and informative console logs for easy debugging and monitoring.

## ⚡ Quick Start

### Requirements

- Docker and Docker Compose  
  or
- Python 3.9+

### Method 1: Using Docker (Recommended)

#### Create Configuration File

Copy `.env.example` (or create one if it does not exist) to `.env`. Usually, you don't need to change the default settings.

```ini
# .env
ZEO_EXEC_PATH=network
ZEO_WORKSPACE=workspace
ENABLE_CACHE=true
```

#### Launch with One Command

In the project root directory, run:

```bash
docker-compose up --build
```

Docker will automatically build the image (including downloading and compiling Zeo++) and start the service at [http://localhost:8000](http://localhost:8000).

### Method 2: Local Development (Without Docker)

#### Install Zeo++

Ensure you have installed Zeo++ following the official instructions and can invoke it using the `network` command in your terminal.

#### Install Dependencies

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Configure Environment

Create a `.env` file and ensure `ZEO_EXEC_PATH` points to your Zeo++ (or `network`) executable.

#### Run the Service

```bash
uvicorn app.main:app --reload
```

## 📋 Usage Example

Once the project is running, you can call the API using any HTTP client. Example using `curl` to compute pore diameter:

```bash
curl -X 'POST' \
  'http://localhost:8000/api/pore_diameter' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'structure_file=@/path/to/your/file.cif' \
  -F 'ha=true'
```

Replace `/path/to/your/file.cif` with the actual path to your local structure file. Parameters (e.g., `ha=true`) are sent as form fields using `-F`. The interactive API documentation (Swagger UI) is available at [http://localhost:8000/docs](http://localhost:8000/docs).

## 📚 API Reference

All endpoints require a `structure_file` uploaded as a file.

### Core Geometry Analysis

| Path | Function |
| --- | --- |
| `/api/pore_diameter` → Zeo++ `-res` | Compute the largest included sphere (Di) and largest free sphere (Df) diameters |
| `/api/surface_area` → Zeo++ `-sa` | Compute accessible surface area using Monte Carlo sampling |
| `/api/accessible_volume` → Zeo++ `-vol` | Compute the accessible volume for a given probe |
| `/api/probe_volume` → Zeo++ `-volpo` | Compute the probe-occupiable volume for a specific point or region |
| `/api/channel_analysis` → Zeo++ `-chan` | Identify and analyze channels |
| `/api/pore_size_dist/download` → Zeo++ `-psd` | Download pore size distribution histogram data file |
| `/api/blocking_spheres` → Zeo++ `-block` | Identify inaccessible regions and generate blocking spheres |

### Structural Information Analysis

| Path | Function |
| --- | --- |
| `/api/framework_info` → Zeo++ `-strinfo` | Identify the number of frameworks and their dimensionality |
| `/api/open_metal_sites` → Zeo++ `-oms` | Compute the number of open metal sites |

## 📜 License

MIT © Shibo Li, 2025
