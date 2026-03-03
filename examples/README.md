# Examples

This directory contains complete usage examples for Zeo++ API.

## Directory Structure

```
examples/
├── README.md                         # This file
├── sample_structures/                # Example structure files
│   ├── EDI.cif                      # EDI zeolite structure
│   └── HKUST-1.cif                  # HKUST-1 MOF structure
├── python/                           # Python examples
│   ├── basic_usage.py               # Basic API calls
│   ├── batch_analysis.py            # Batch analysis script
│   ├── hkust1_acetylene_analysis.py # ⭐ MOF acetylene adsorption case study
│   └── requirements.txt             # Python dependencies
└── curl/                             # cURL examples
    ├── api_examples.sh              # Linux/Mac script
    └── api_examples.bat             # Windows batch file
```

## Quick Start

### 1. Ensure API Service is Running

```bash
# In project root directory
docker-compose up -d

# Check service status
curl http://localhost:9876/health
```

### 2. Python Examples

```bash
cd examples/python
pip install -r requirements.txt

# Basic example - demonstrates all API endpoints
python basic_usage.py

# Batch analysis - process multiple structure files
python batch_analysis.py ../sample_structures output.csv
```

### 3. cURL Examples

**Linux/Mac:**
```bash
cd examples/curl
chmod +x api_examples.sh
./api_examples.sh
```

**Windows:**
```cmd
cd examples\curl
api_examples.bat
```

## Example Files Description

### Python Examples

| File | Description |
|------|-------------|
| `basic_usage.py` | Contains examples of all API endpoint calls, suitable for learning API usage |
| `batch_analysis.py` | Batch process multiple structure files, supports concurrent requests, export CSV results |
| `hkust1_acetylene_analysis.py` | ⭐ **Complete case study**: Analyze acetylene adsorption performance using HKUST-1 MOF |

### ⭐ Featured Case: HKUST-1 Acetylene Adsorption Analysis

`python/hkust1_acetylene_analysis.py` is a complete application example demonstrating how to use Zeo++ API to analyze MOF material's acetylene (C₂H₂) adsorption performance.

**Run:**
```bash
cd examples/python
python hkust1_acetylene_analysis.py
```

**Covered API Functions:**
1. `/api/v1/framework_info` - Get framework basic information
2. `/api/v1/pore_diameter` - Analyze pore diameter, determine acetylene accessibility
3. `/api/v1/surface_area` - Calculate acetylene accessible surface area (probe radius 1.65Å)
4. `/api/v1/surface_area` - Calculate nitrogen accessible surface area (BET comparison)
5. `/api/v1/accessible_volume` - Calculate acetylene accessible volume, estimate adsorption capacity
6. `/api/v1/channel_analysis` - Analyze channel dimensions and connectivity
7. `/api/v1/open_metal_sites` - Detect open metal sites (Cu²⁺)
8. `/api/v1/pore_size_dist/download` - Analyze pore size distribution (returns file)
9. `/api/v1/blocking_spheres` - Detect blocking regions

**Output Example:**
```
╔══════════════════════════════════════════════════════════════════════╗
║     HKUST-1 MOF Acetylene (C₂H₂) Adsorption Performance Analysis     ║
╚══════════════════════════════════════════════════════════════════════╝

======================================================================
  1. Framework Basic Information (Framework Info)
======================================================================
  Material Name: HKUST-1 (Cu-BTC, MOF-199)
  Chemical Formula: C18 H6 Cu3 O12
  ...

======================================================================
  5. Acetylene Accessible Volume (C2H2 Accessible Volume)
======================================================================
  Probe Radius (C2H2): 1.65 Å
  C2H2 Accessible Volume: 0.75 cm³/g
  
  📊 Estimated Acetylene Adsorption Capacity (theoretical maximum):
     Estimated Uptake: 200 cc(STP)/g
```

### Example Structure Files

#### sample_structures/EDI.cif

EDI (Edingtonite) zeolite structure, tetragonal crystal system, contains Si and O atoms.

Structural characteristics:
- Unit cell parameters: a=b=9.550Å, c=6.520Å
- Space group: P-421m
- Typical pore diameter: ~3Å
- Suitable for testing all API endpoints

#### sample_structures/HKUST-1.cif

HKUST-1 (also known as Cu-BTC, MOF-199) is a classic metal-organic framework (MOF) material.

**Application Scenarios:**
- 🔹 **Acetylene (C₂H₂) Adsorption & Separation** - HKUST-1 has excellent selective adsorption capacity for acetylene
- 🔹 **CO₂ Capture** - Open metal sites enhance CO₂ adsorption
- 🔹 **H₂ Storage** - High specific surface area benefits hydrogen storage
- 🔹 **Natural Gas Purification** - Separation of CH₄ and impurity gases
- 🔹 **Catalytic Reactions** - Cu²⁺ open sites can serve as catalytic active centers

**Structural Characteristics:**
- Chemical Formula: Cu₃(BTC)₂ (BTC = benzene-1,3,5-tricarboxylic acid)
- Unit Cell Parameters: a=b=c=26.343Å (cubic crystal system)
- Space Group: Fm-3m
- BET Specific Surface Area: ~1500-2000 m²/g
- Pore Volume: ~0.75 cm³/g
- Contains Open Metal Sites

**References:**
- Chui, S. S.-Y. et al., Science 1999, 283, 1148-1150
- COD ID: 2300380

## Notes

- Ensure Zeo++ API service is running (default http://localhost:9876)
- If using a different port, modify `API_BASE_URL` in scripts
- Batch analysis script supports `.cif`, `.cssr`, `.v1`, `.arc`, `.xyz`, `.pdb`, `.cuc` formats

## Advanced Features

### Force Recalculation (Skip Cache)

All API endpoints support the `force_recalculate` parameter to skip cache:

```bash
# Normal call (use cache)
curl -X POST "http://localhost:9876/api/v1/pore_diameter" \
    -F "structure_file=@HKUST-1.cif"

# Force recalculation (skip cache)
curl -X POST "http://localhost:9876/api/v1/pore_diameter" \
    -F "structure_file=@HKUST-1.cif" \
    -F "force_recalculate=true"
```

Use Cases:
- Need to verify Zeo++ output during debugging
- Suspect cached results are incorrect
- Need to ensure getting latest calculation results
