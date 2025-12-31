#!/bin/bash
# Zeo++ API cURL Examples
# cURL 命令行示例

# API 基础地址
API_BASE="http://localhost:9876"

# 示例文件路径（请根据实际情况修改）
SAMPLE_FILE="../sample_structures/EDI.cif"

echo "=============================================="
echo "Zeo++ API cURL Examples"
echo "=============================================="
echo ""

# 1. 健康检查
echo "1. 健康检查 (Health Check)"
echo "-------------------------------------------"
curl -s "${API_BASE}/health" | python -m json.tool
echo ""

# 2. 孔径计算
echo "2. 孔径计算 (Pore Diameter)"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/pore_diameter" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 3. 表面积计算
echo "3. 表面积计算 (Surface Area)"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/surface_area" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "chan_radius=1.82" \
    -F "probe_radius=1.82" \
    -F "samples=2000" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 4. 可及体积计算
echo "4. 可及体积计算 (Accessible Volume)"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/accessible_volume" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "chan_radius=1.82" \
    -F "probe_radius=1.82" \
    -F "samples=50000" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 5. 通道分析
echo "5. 通道分析 (Channel Analysis)"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/channel_analysis" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "probe_radius=1.82" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 6. 框架信息
echo "6. 框架信息 (Framework Info)"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/framework_info" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 7. 孔径分布
echo "7. 孔径分布 (Pore Size Distribution)"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/pore_size_dist" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "chan_radius=1.82" \
    -F "probe_radius=1.82" \
    -F "samples=50000" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 8. 探测体积
echo "8. 探测体积 (Probe Volume)"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/probe_volume" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "probe_radius=0.0" \
    -F "samples=50000" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 9. 阻塞球
echo "9. 阻塞球 (Blocking Spheres)"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/blocking_spheres" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "probe_radius=1.82" \
    -F "ha=true" \
    | python -m json.tool
echo ""

# 10. 开放金属位点
echo "10. 开放金属位点 (Open Metal Sites)"
echo "-------------------------------------------"
curl -s -X POST "${API_BASE}/api/v1/open_metal_sites" \
    -F "structure_file=@${SAMPLE_FILE}" \
    -F "ha=true" \
    | python -m json.tool
echo ""

echo "=============================================="
echo "所有示例执行完成"
echo "=============================================="
