@echo off
REM Zeo++ API cURL Examples for Windows
REM Windows 批处理脚本示例

SET API_BASE=http://localhost:9876
SET SAMPLE_FILE=..\sample_structures\EDI.cif

echo ==============================================
echo Zeo++ API cURL Examples (Windows)
echo ==============================================
echo.

REM 1. 健康检查
echo 1. 健康检查 (Health Check)
echo -------------------------------------------
curl -s "%API_BASE%/health"
echo.
echo.

REM 2. 孔径计算
echo 2. 孔径计算 (Pore Diameter)
echo -------------------------------------------
curl -s -X POST "%API_BASE%/api/v1/pore_diameter" -F "structure_file=@%SAMPLE_FILE%" -F "ha=true"
echo.
echo.

REM 3. 表面积计算
echo 3. 表面积计算 (Surface Area)
echo -------------------------------------------
curl -s -X POST "%API_BASE%/api/v1/surface_area" -F "structure_file=@%SAMPLE_FILE%" -F "chan_radius=1.82" -F "probe_radius=1.82" -F "samples=2000" -F "ha=true"
echo.
echo.

REM 4. 可及体积计算
echo 4. 可及体积计算 (Accessible Volume)
echo -------------------------------------------
curl -s -X POST "%API_BASE%/api/v1/accessible_volume" -F "structure_file=@%SAMPLE_FILE%" -F "chan_radius=1.82" -F "probe_radius=1.82" -F "samples=50000" -F "ha=true"
echo.
echo.

REM 5. 通道分析
echo 5. 通道分析 (Channel Analysis)
echo -------------------------------------------
curl -s -X POST "%API_BASE%/api/v1/channel_analysis" -F "structure_file=@%SAMPLE_FILE%" -F "probe_radius=1.82" -F "ha=true"
echo.
echo.

REM 6. 框架信息
echo 6. 框架信息 (Framework Info)
echo -------------------------------------------
curl -s -X POST "%API_BASE%/api/v1/framework_info" -F "structure_file=@%SAMPLE_FILE%" -F "ha=true"
echo.
echo.

echo ==============================================
echo 示例执行完成
echo ==============================================
pause
