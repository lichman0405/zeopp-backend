# Zeo++ API Complete Documentation

**Version**: v0.3.1  
**Base URL**: `http://localhost:9876`  
**API Prefix**: `/api/v1`

---

## Table of Contents

1. [System Endpoints](#1-system-endpoints)
2. [Core Analysis Endpoints](#2-core-analysis-endpoints)
   - [Pore Diameter](#21-pore-diameter-pore_diameter)
   - [Surface Area](#22-surface-area-surface_area)
   - [Accessible Volume](#23-accessible-volume-accessible_volume)
   - [Probe-Occupiable Volume](#24-probe-occupiable-volume-probe_volume)
   - [Channel Analysis](#25-channel-analysis-channel_analysis)
   - [Pore Size Distribution](#26-pore-size-distribution-pore_size_dist)
   - [Blocking Spheres](#27-blocking-spheres-blocking_spheres)
3. [Structure Information Endpoints](#3-structure-information-endpoints)
   - [Framework Info](#31-framework-info-framework_info)
   - [Open Metal Sites](#32-open-metal-sites-open_metal_sites)
4. [Cache Management Endpoints](#4-cache-management-endpoints)
5. [Monitoring Endpoints](#5-monitoring-endpoints)
6. [Common Parameters](#6-common-parameters)
7. [Error Response Format](#7-error-response-format)

---

## 1. System Endpoints

### 1.1 Health Check

**Endpoint**: `GET /health`

**Description**: Basic health check to verify the service is running.

**Response Example**:
```json
{
  "status": "healthy",
  "message": "Zeo++ API is running"
}
```

---

### 1.2 Detailed Health Check

**Endpoint**: `GET /health/detailed`

**Description**: Detailed health check including system information and Zeo++ availability.

**Response Example**:
```json
{
  "status": "healthy",
  "zeopp_available": true,
  "zeopp_version": "0.3",
  "system": {
    "platform": "Linux",
    "python_version": "3.12.0"
  }
}
```

---

### 1.3 Version Information

**Endpoint**: `GET /version`

**Description**: Get API version information.

**Response Example**:
```json
{
  "version": "0.3.1",
  "api_version": "v1"
}
```

---

## 2. Core Analysis Endpoints

> **General Note**: All analysis endpoints use `POST` method, require a structure file upload, and parameters are sent as `multipart/form-data`.

---

### 2.1 Pore Diameter (pore_diameter)

**Endpoint**: `POST /api/v1/pore_diameter`

**Zeo++ Command**: `-res`

**Description**: Calculate the largest included sphere diameter (Di), largest free sphere diameter (Df), and included sphere along free path.

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `structure_file` | File | ✅ | - | Structure file (.cif, .cssr, .v1, .arc) |
| `ha` | boolean | ❌ | `true` | Enable high accuracy mode |

#### Response Format

```json
{
  "included_diameter": 4.89082,
  "free_diameter": 3.03868,
  "included_along_free": 4.81969,
  "cached": false
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `included_diameter` | float | Largest included sphere diameter Di (Å) |
| `free_diameter` | float | Largest free sphere diameter Df (Å) |
| `included_along_free` | float | Included sphere along free path Dif (Å) |
| `cached` | boolean | Whether result was served from cache |

#### cURL Example

```bash
curl -X POST "http://localhost:9876/api/v1/pore_diameter" \
  -H "Content-Type: multipart/form-data" \
  -F "structure_file=@/path/to/structure.cif" \
  -F "ha=true"
```

---

### 2.2 Surface Area (surface_area)

**Endpoint**: `POST /api/v1/surface_area`

**Zeo++ Command**: `-sa`

**Description**: Calculate accessible surface area (ASA) and non-accessible surface area (NASA) using Monte Carlo sampling.

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `structure_file` | File | ✅ | - | Structure file (.cif, .cssr, .v1, .arc) |
| `chan_radius` | float | ❌ | `1.21` | Channel radius (Å) for accessibility determination |
| `probe_radius` | float | ❌ | `1.21` | Probe radius (Å) for Monte Carlo sampling |
| `samples` | integer | ❌ | `2000` | Number of Monte Carlo samples |
| `ha` | boolean | ❌ | `true` | Enable high accuracy mode |

> ⚠️ **Constraint**: `probe_radius` must be ≤ `chan_radius`

#### Response Format

```json
{
  "asa_unitcell": 60.7713,
  "asa_volume": 1976.4,
  "asa_mass": 1218.21,
  "nasa_unitcell": 0.0,
  "nasa_volume": 0.0,
  "nasa_mass": 0.0,
  "cached": false
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `asa_unitcell` | float | Accessible surface area (Å²/unit cell) |
| `asa_volume` | float | Accessible surface area (m²/cm³) |
| `asa_mass` | float | Accessible surface area (m²/g) |
| `nasa_unitcell` | float | Non-accessible surface area (Å²/unit cell) |
| `nasa_volume` | float | Non-accessible surface area (m²/cm³) |
| `nasa_mass` | float | Non-accessible surface area (m²/g) |
| `cached` | boolean | Whether result was served from cache |

#### cURL Example

```bash
curl -X POST "http://localhost:9876/api/v1/surface_area" \
  -H "Content-Type: multipart/form-data" \
  -F "structure_file=@/path/to/structure.cif" \
  -F "chan_radius=1.82" \
  -F "probe_radius=1.82" \
  -F "samples=2000" \
  -F "ha=true"
```

---

### 2.3 Accessible Volume (accessible_volume)

**Endpoint**: `POST /api/v1/accessible_volume`

**Zeo++ Command**: `-vol`

**Description**: Calculate accessible volume (AV) and non-accessible volume (NAV) using Monte Carlo sampling.

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `structure_file` | File | ✅ | - | Structure file (.cif, .cssr, .v1, .arc) |
| `chan_radius` | float | ❌ | `1.21` | Channel radius (Å) |
| `probe_radius` | float | ❌ | `1.21` | Probe radius (Å) |
| `samples` | integer | ❌ | `50000` | Number of Monte Carlo samples (recommended: 50000) |
| `ha` | boolean | ❌ | `true` | Enable high accuracy mode |

> ⚠️ **Constraint**: `probe_radius` must be ≤ `chan_radius`

#### Response Format

```json
{
  "unitcell_volume": 307.484,
  "density": 1.62239,
  "av": {
    "unitcell": 22.6493,
    "fraction": 0.07366,
    "mass": 0.0454022
  },
  "nav": {
    "unitcell": 0.0,
    "fraction": 0.0,
    "mass": 0.0
  },
  "cached": false
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `unitcell_volume` | float | Unit cell volume (Å³) |
| `density` | float | Density (g/cm³) |
| `av.unitcell` | float | Accessible volume (Å³) |
| `av.fraction` | float | Accessible volume fraction |
| `av.mass` | float | Accessible volume (cm³/g) |
| `nav.unitcell` | float | Non-accessible volume (Å³) |
| `nav.fraction` | float | Non-accessible volume fraction |
| `nav.mass` | float | Non-accessible volume (cm³/g) |
| `cached` | boolean | Whether result was served from cache |

---

### 2.4 Probe-Occupiable Volume (probe_volume)

**Endpoint**: `POST /api/v1/probe_volume`

**Zeo++ Command**: `-volpo`

**Description**: Calculate probe-occupiable volume (POAV) and probe non-occupiable volume (PONAV).

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `structure_file` | File | ✅ | - | Structure file (.cif, .cssr, .v1, .arc) |
| `chan_radius` | float | ❌ | `1.21` | Channel radius (Å) |
| `probe_radius` | float | ❌ | `1.21` | Probe radius (Å) |
| `samples` | integer | ❌ | `50000` | Number of Monte Carlo samples |
| `ha` | boolean | ❌ | `true` | Enable high accuracy mode |

> ⚠️ **Constraint**: `probe_radius` must be ≤ `chan_radius`

#### Response Format

```json
{
  "poav_unitcell": 131.284,
  "poav_fraction": 0.42696,
  "poav_mass": 0.263168,
  "ponav_unitcell": 0.0,
  "ponav_fraction": 0.0,
  "ponav_mass": 0.0,
  "cached": false
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `poav_unitcell` | float | Probe-occupiable volume (Å³) |
| `poav_fraction` | float | Probe-occupiable volume fraction |
| `poav_mass` | float | Probe-occupiable volume (cm³/g) |
| `ponav_unitcell` | float | Probe non-occupiable volume (Å³) |
| `ponav_fraction` | float | Probe non-occupiable volume fraction |
| `ponav_mass` | float | Probe non-occupiable volume (cm³/g) |
| `cached` | boolean | Whether result was served from cache |

---

### 2.5 Channel Analysis (channel_analysis)

**Endpoint**: `POST /api/v1/channel_analysis`

**Zeo++ Command**: `-chan`

**Description**: Analyze channel systems in the framework, identifying dimensionality and geometric properties.

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `structure_file` | File | ✅ | - | Structure file (.cif, .cssr, .v1, .arc) |
| `probe_radius` | float | ❌ | `1.21` | Probe radius (Å) |
| `ha` | boolean | ❌ | `true` | Enable high accuracy mode |

#### Response Format

```json
{
  "dimension": 3,
  "included_diameter": 4.89082,
  "free_diameter": 3.03868,
  "included_along_free": 4.89082,
  "cached": false
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `dimension` | integer | Channel dimensionality (0=isolated, 1=1D, 2=2D, 3=3D) |
| `included_diameter` | float | Channel included sphere diameter (Å) |
| `free_diameter` | float | Channel free sphere diameter (Å) |
| `included_along_free` | float | Included sphere along free path (Å) |
| `cached` | boolean | Whether result was served from cache |

---

### 2.6 Pore Size Distribution (pore_size_dist)

**Endpoint**: `POST /api/v1/pore_size_dist/download`

**Zeo++ Command**: `-psd`

**Description**: Calculate pore size distribution histogram and download the data file.

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `structure_file` | File | ✅ | - | Structure file (.cif, .cssr, .v1, .arc) |
| `probe_radius` | float | ❌ | `1.21` | Probe radius (Å) |
| `chan_radius` | float | ❌ | `null` | Channel radius (Å), defaults to probe_radius |
| `samples` | integer | ❌ | `50000` | Number of Monte Carlo samples |
| `ha` | boolean | ❌ | `true` | Enable high accuracy mode |

#### Response Format

Returns `.psd_histo` file download, Content-Type: `text/plain`

#### cURL Example

```bash
curl -X POST "http://localhost:9876/api/v1/pore_size_dist/download" \
  -H "Content-Type: multipart/form-data" \
  -F "structure_file=@/path/to/structure.cif" \
  -F "samples=50000" \
  -o psd_histogram.txt
```

---

### 2.7 Blocking Spheres (blocking_spheres)

**Endpoint**: `POST /api/v1/blocking_spheres`

**Zeo++ Command**: `-block`

**Description**: Identify inaccessible regions and generate blocking spheres for molecular simulations (e.g., RASPA).

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `structure_file` | File | ✅ | - | Structure file (.cif, .cssr, .v1, .arc) |
| `probe_radius` | float | ❌ | `1.86` | Probe radius (Å), defaults to methane radius |
| `samples` | integer | ❌ | `50000` | Number of Monte Carlo samples |
| `ha` | boolean | ❌ | `true` | Enable high accuracy mode |

#### Response Format

```json
{
  "channels": 1,
  "pockets": 2,
  "nodes_assigned": 139,
  "raw": "Identified 1 channels and 2 pockets\n139 nodes assigned to pores.",
  "cached": false
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `channels` | integer | Number of channels identified |
| `pockets` | integer | Number of pockets identified |
| `nodes_assigned` | integer | Number of nodes assigned to pores |
| `raw` | string | Raw output text |
| `cached` | boolean | Whether result was served from cache |

---

## 3. Structure Information Endpoints

### 3.1 Framework Info (framework_info)

**Endpoint**: `POST /api/v1/framework_info`

**Zeo++ Command**: `-strinfo`

**Description**: Identify the number of frameworks and their dimensionalities in the structure.

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `structure_file` | File | ✅ | - | Structure file (.cif, .cssr) |
| `ha` | boolean | ❌ | `true` | Enable high accuracy mode |

#### Response Format

```json
{
  "filename": "structure.strinfo",
  "formula": "Si4O10",
  "segments": 4,
  "number_of_frameworks": 1,
  "number_of_molecules": 0,
  "frameworks": [
    {
      "framework_id": 0,
      "dimensionality": 3
    }
  ],
  "cached": false
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `filename` | string | Output filename |
| `formula` | string | Chemical formula |
| `segments` | integer | Number of structure segments |
| `number_of_frameworks` | integer | Number of frameworks |
| `number_of_molecules` | integer | Number of molecules |
| `frameworks` | array | Framework details list |
| `frameworks[].framework_id` | integer | Framework ID |
| `frameworks[].dimensionality` | integer | Framework dimensionality (1D/2D/3D) |
| `cached` | boolean | Whether result was served from cache |

---

### 3.2 Open Metal Sites (open_metal_sites)

**Endpoint**: `POST /api/v1/open_metal_sites`

**Zeo++ Command**: `-oms`

**Description**: Automatically detect and count open metal sites in the structure.

#### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `structure_file` | File | ✅ | - | Structure file (.cif, .cssr) |
| `ha` | boolean | ❌ | `true` | Enable high accuracy mode |

#### Response Format

```json
{
  "open_metal_sites_count": 4,
  "cached": false
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `open_metal_sites_count` | integer | Number of open metal sites |
| `cached` | boolean | Whether result was served from cache |

---

## 4. Cache Management Endpoints

### 4.1 Cache Statistics

**Endpoint**: `GET /api/v1/cache/stats`

**Description**: Get current cache usage statistics.

**Response Example**:
```json
{
  "temp_files": 15,
  "cache_entries": 42,
  "total_size_mb": 12.5
}
```

---

### 4.2 Cleanup Temporary Files

**Endpoint**: `POST /api/v1/cache/cleanup`

**Description**: Clean up expired temporary files.

**Response Example**:
```json
{
  "message": "Cleanup completed",
  "files_removed": 8
}
```

---

### 4.3 Clear All Cache

**Endpoint**: `DELETE /api/v1/cache/clear`

**Description**: Clear all cached data.

**Response Example**:
```json
{
  "message": "All cache cleared",
  "entries_removed": 42
}
```

---

## 5. Monitoring Endpoints

### 5.1 Prometheus Metrics

**Endpoint**: `GET /metrics`

**Description**: Prometheus-formatted metrics for monitoring system scraping.

**Response Format**: `text/plain`

```
# HELP zeopp_uptime_seconds Service uptime in seconds
# TYPE zeopp_uptime_seconds gauge
zeopp_uptime_seconds 3600.00

# HELP zeopp_requests_total Total number of requests
# TYPE zeopp_requests_total counter
zeopp_requests_total 1234
```

---

### 5.2 Metrics Summary

**Endpoint**: `GET /api/v1/metrics/summary`

**Description**: JSON-formatted metrics summary.

**Response Example**:
```json
{
  "uptime_seconds": 3600.0,
  "total_requests": 1234,
  "active_requests": 2,
  "requests_by_status": {
    "2xx": 1200,
    "4xx": 30,
    "5xx": 4
  },
  "latency": {
    "avg_ms": 125.5,
    "p50_ms": 100.0,
    "p90_ms": 250.0,
    "p99_ms": 500.0
  },
  "errors": {}
}
```

---

## 6. Common Parameters

### 6.1 High Accuracy Mode (`ha`)

| Value | Description |
|-------|-------------|
| `true` | Enable high accuracy mode with exact geometric calculations (recommended) |
| `false` | Use approximate calculations, faster but slightly less accurate |

**Recommendation**: Always use `ha=true` for complex materials like MOFs and zeolites.

---

### 6.2 Probe Radius Reference

Choose appropriate probe radius based on the molecule of interest:

| Molecule | Radius (Å) | Common Use Case |
|----------|------------|-----------------|
| Helium (He) | 1.29 | Theoretical maximum porosity |
| Hydrogen (H₂) | 1.45 | Hydrogen storage |
| Carbon Dioxide (CO₂) | 1.65 | Carbon capture |
| Nitrogen (N₂) | 1.82 | BET surface area comparison |
| Methane (CH₄) | 1.86 | Natural gas storage |
| Water (H₂O) | 1.40 | Hydrophilicity studies |

---

### 6.3 Sample Count Recommendations

| Analysis Type | Quick Preview | Production | High Precision |
|---------------|---------------|------------|----------------|
| Surface Area (`-sa`) | 500-1000 | **2000** | 5000+ |
| Volume (`-vol`, `-volpo`) | 10000 | **50000** | 100000+ |
| Pore Size Dist (`-psd`) | 10000 | **50000** | 100000+ |
| Blocking Spheres (`-block`) | 10000 | **50000** | 100000+ |

---

### 6.4 Supported File Formats

| Extension | Format | Description |
|-----------|--------|-------------|
| `.cif` | Crystallographic Information File | Most common crystal structure format |
| `.cssr` | Cambridge Structural Search and Retrieval | Cambridge database format |
| `.v1` | Zeo++ V1 format | Native Zeo++ format |
| `.arc` | Accelrys Archive | Materials Studio format |
| `.pdb` | Protein Data Bank | Protein database format |
| `.xyz` | XYZ Coordinate File | Simple Cartesian coordinate format |

---

## 7. Error Response Format

All error responses follow a unified format:

```json
{
  "detail": "Error description message",
  "error_code": "ERROR_TYPE"
}
```

### Common Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `VALIDATION_ERROR` | Request parameter validation failed |
| 422 | `VALIDATION_ERROR` | Parameter constraint not satisfied (e.g., probe_radius > chan_radius) |
| 429 | `RATE_LIMIT_ERROR` | Request rate limit exceeded |
| 500 | `EXECUTION_ERROR` | Zeo++ execution failed |
| 500 | `PARSE_ERROR` | Output parsing failed |
| 500 | `TIMEOUT_ERROR` | Calculation timeout |

---

## Appendix: Response Headers

All responses include the following custom headers:

| Header | Description |
|--------|-------------|
| `X-Request-ID` | Unique request identifier for tracing and debugging |
| `X-Process-Time` | Request processing time (e.g., `125.5ms`) |

---

*Documentation Updated: 2025-12-31*  
*API Version: v0.3.1*
