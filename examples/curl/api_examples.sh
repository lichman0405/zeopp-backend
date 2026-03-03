#!/bin/bash
# Zeo++ API cURL Examples
# cURL command-line examples

# API base URL
API_BASE="http://localhost:9876"

# Sample file path (modify as needed)
SAMPLE_FILE="../sample_structures/EDI.cif"

echo "=============================================="
echo "Zeo++ API cURL Examples"
echo "=============================================="
echo ""

# 1. Health Check
echo "1. Health Check"
echo "-------------------------------------------"
curl -s "${API_BASE}/health" | python -m json.tool
echo ""

# 2. Pore Diameter
echo "2. Pore Diameter"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/pore_diameter" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 3. Surface Area
echo "3. Surface Area"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/surface_area" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "chan_radius=1.82" \
    -F "probe_radius=1.82" \
    -F "samples=2000" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 4. Accessible Volume
echo "4. Accessible Volume"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/accessible_volume" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "chan_radius=1.82" \
    -F "probe_radius=1.82" \
    -F "samples=50000" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 5. Channel Analysis
echo "5. Channel Analysis"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/channel_analysis" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "probe_radius=1.82" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 6. Framework Info
echo "6. Framework Info"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/framework_info" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 7. Pore Size Distribution (File Download)
echo "7. Pore Size Distribution (File Download)"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/pore_size_dist/download" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "chan_radius=1.82" \
    -F "probe_radius=1.82" \
    -F "samples=50000" \
    -F "ha=true" \
    -o psd_result.txt
echo "Saved to psd_result.txt"
echo ""

# 8. Probe Volume
echo "8. Probe Volume"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/probe_volume" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "probe_radius=0.0" \
    -F "samples=50000" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 9. Blocking Spheres
echo "9. Blocking Spheres"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/blocking_spheres" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "probe_radius=1.82" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 10. Open Metal Sites
echo "10. Open Metal Sites"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/open_metal_sites" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "ha=true" \
    | python -m json.tool
echo ""

echo "=============================================="
echo "All examples completed"
echo "=============================================="

# Extra example: Force recalculation (skip cache)
echo ""
echo "=============================================="
echo "Extra example: Force recalculation (force_recalculate=true)"
echo "=============================================="
echo "This parameter skips cache and forces Zeo++ computation:"
echo 'curl -X POST "${API_BASE}/api/v1/pore_diameter" \'
echo '    -F "structure_file=@structure.cif" \'
echo '    -F "force_recalculate=true"'
echo ""
