"""
Zeo++ API Batch Analysis Script
批量分析脚本

This script processes multiple structure files and exports results to CSV.
"""

import requests
import csv
import sys
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from datetime import datetime

# API 配置
API_BASE_URL = "http://localhost:9876"

# 探针半径（可根据需要调整）
PROBE_RADIUS = 1.82  # N2 探针


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    filename: str
    formula: str = ""
    # 孔径
    Di: float = 0.0  # 最大包含球直径
    Df: float = 0.0  # 最大自由球直径
    Dif: float = 0.0  # 沿自由球路径的包含球直径
    # 表面积
    ASA_m2_g: float = 0.0  # 可及表面积 m²/g
    NASA_m2_g: float = 0.0  # 不可及表面积 m²/g
    # 体积
    density: float = 0.0  # 密度 g/cm³
    AV_fraction: float = 0.0  # 可及体积分数
    AV_cm3_g: float = 0.0  # 可及体积 cm³/g
    # 通道
    channel_dim: int = 0  # 通道维度
    # 状态
    status: str = "success"
    error_message: str = ""


def analyze_structure(file_path: Path) -> AnalysisResult:
    """
    对单个结构文件执行完整分析
    """
    result = AnalysisResult(filename=file_path.name)
    
    try:
        # 1. 孔径计算
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/pore_diameter",
                files={"structure_file": (file_path.name, f)},
                data={"ha": "true"},
                timeout=60
            )
        if response.status_code == 200:
            data = response.json()
            result.Di = data.get("included_diameter", 0)
            result.Df = data.get("free_diameter", 0)
            result.Dif = data.get("included_along_free", 0)
        
        # 2. 表面积计算
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/surface_area",
                files={"structure_file": (file_path.name, f)},
                data={
                    "chan_radius": str(PROBE_RADIUS),
                    "probe_radius": str(PROBE_RADIUS),
                    "samples": "2000",
                    "ha": "true"
                },
                timeout=120
            )
        if response.status_code == 200:
            data = response.json()
            result.ASA_m2_g = data.get("asa_mass", 0)
            result.NASA_m2_g = data.get("nasa_mass", 0)
        
        # 3. 可及体积计算
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/accessible_volume",
                files={"structure_file": (file_path.name, f)},
                data={
                    "chan_radius": str(PROBE_RADIUS),
                    "probe_radius": str(PROBE_RADIUS),
                    "samples": "50000",
                    "ha": "true"
                },
                timeout=180
            )
        if response.status_code == 200:
            data = response.json()
            result.density = data.get("density", 0)
            result.AV_fraction = data.get("av", {}).get("fraction", 0)
            result.AV_cm3_g = data.get("av", {}).get("mass", 0)
        
        # 4. 通道分析
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/channel_analysis",
                files={"structure_file": (file_path.name, f)},
                data={
                    "probe_radius": str(PROBE_RADIUS),
                    "ha": "true"
                },
                timeout=60
            )
        if response.status_code == 200:
            data = response.json()
            result.channel_dim = data.get("dimension", 0)
        
        # 5. 框架信息
        with open(file_path, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/framework_info",
                files={"structure_file": (file_path.name, f)},
                data={"ha": "true"},
                timeout=60
            )
        if response.status_code == 200:
            data = response.json()
            result.formula = data.get("formula", "")
        
    except requests.exceptions.Timeout:
        result.status = "timeout"
        result.error_message = "Request timed out"
    except requests.exceptions.ConnectionError:
        result.status = "connection_error"
        result.error_message = f"Cannot connect to {API_BASE_URL}"
    except Exception as e:
        result.status = "error"
        result.error_message = str(e)
    
    return result


def batch_analyze(
    input_dir: Path,
    output_file: Path,
    max_workers: int = 4,
    extensions: List[str] = None
) -> List[AnalysisResult]:
    """
    批量分析目录中的所有结构文件
    
    Args:
        input_dir: 包含结构文件的目录
        output_file: 输出 CSV 文件路径
        max_workers: 并行处理的最大线程数
        extensions: 要处理的文件扩展名列表
    """
    if extensions is None:
        extensions = [".cif", ".cssr", ".v1", ".pdb", ".xyz"]
    
    # 收集所有结构文件
    structure_files = []
    for ext in extensions:
        structure_files.extend(input_dir.glob(f"*{ext}"))
    
    if not structure_files:
        print(f"在 {input_dir} 中未找到结构文件")
        return []
    
    print(f"找到 {len(structure_files)} 个结构文件")
    print(f"使用探针半径: {PROBE_RADIUS} Å")
    print(f"并行线程数: {max_workers}")
    print("-" * 60)
    
    results = []
    completed = 0
    
    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(analyze_structure, f): f 
            for f in structure_files
        }
        
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
                completed += 1
                status_icon = "✓" if result.status == "success" else "✗"
                print(f"[{completed}/{len(structure_files)}] {status_icon} {file_path.name}")
            except Exception as e:
                completed += 1
                print(f"[{completed}/{len(structure_files)}] ✗ {file_path.name}: {e}")
    
    # 导出到 CSV
    if results:
        fieldnames = list(asdict(results[0]).keys())
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for r in results:
                writer.writerow(asdict(r))
        print("-" * 60)
        print(f"结果已保存到: {output_file}")
    
    # 打印统计
    success_count = sum(1 for r in results if r.status == "success")
    print(f"成功: {success_count}/{len(results)}")
    
    return results


def main():
    """主函数"""
    # 默认使用示例目录
    if len(sys.argv) > 1:
        input_dir = Path(sys.argv[1])
    else:
        input_dir = Path(__file__).parent.parent / "sample_structures"
    
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = Path(f"zeopp_results_{timestamp}.csv")
    
    if not input_dir.exists():
        print(f"错误: 目录不存在 {input_dir}")
        sys.exit(1)
    
    print("=" * 60)
    print("Zeo++ 批量分析工具")
    print("=" * 60)
    print(f"输入目录: {input_dir}")
    print(f"输出文件: {output_file}")
    print()
    
    try:
        batch_analyze(input_dir, output_file)
    except requests.exceptions.ConnectionError:
        print(f"错误: 无法连接到 API 服务 {API_BASE_URL}")
        print("请确保 Zeo++ API 服务已启动:")
        print("  docker-compose up -d")
        sys.exit(1)


if __name__ == "__main__":
    main()
