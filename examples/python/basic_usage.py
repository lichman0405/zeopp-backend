"""
Zeo++ API Basic Usage Examples
基础 API 调用示例

This script demonstrates how to call various Zeo++ API endpoints.
"""

import requests
from pathlib import Path

# API 配置
API_BASE_URL = "http://localhost:9876"

# 示例结构文件路径
SAMPLE_FILE = Path(__file__).parent.parent / "sample_structures" / "EDI.cif"


def check_health():
    """检查 API 服务状态"""
    print("=" * 60)
    print("1. 健康检查 (Health Check)")
    print("=" * 60)
    
    # 基本健康检查
    response = requests.get(f"{API_BASE_URL}/health")
    print(f"Basic Health: {response.json()}")
    
    # 详细健康检查
    response = requests.get(f"{API_BASE_URL}/health/detailed")
    print(f"Detailed Health: {response.json()}")
    
    # 版本信息
    response = requests.get(f"{API_BASE_URL}/version")
    print(f"Version: {response.json()}")
    print()


def calculate_pore_diameter(file_path: Path, force_recalculate: bool = False):
    """计算孔径 (Pore Diameter)"""
    print("=" * 60)
    print("2. 孔径计算 (Pore Diameter)")
    print("=" * 60)
    
    with open(file_path, "rb") as f:
        files = {"structure_file": (file_path.name, f)}
        data = {"ha": "true"}
        
        # 添加 force_recalculate 参数（可选）
        if force_recalculate:
            data["force_recalculate"] = "true"
            print("⚡ 强制重新计算模式 (跳过缓存)")
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/pore_diameter",
            files=files,
            data=data
        )
    
    result = response.json()
    print(f"最大包含球直径 (Di): {result['included_diameter']:.4f} Å")
    print(f"最大自由球直径 (Df): {result['free_diameter']:.4f} Å")
    print(f"沿自由球路径的包含球直径 (Dif): {result['included_along_free']:.4f} Å")
    print(f"来自缓存: {result['cached']}")
    print()
    return result


def calculate_surface_area(file_path: Path, probe_radius: float = 1.82):
    """计算表面积 (Surface Area)"""
    print("=" * 60)
    print(f"3. 表面积计算 (probe_radius={probe_radius} Å)")
    print("=" * 60)
    
    with open(file_path, "rb") as f:
        files = {"structure_file": (file_path.name, f)}
        data = {
            "chan_radius": str(probe_radius),
            "probe_radius": str(probe_radius),
            "samples": "2000",
            "ha": "true"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/surface_area",
            files=files,
            data=data
        )
    
    result = response.json()
    print(f"可及表面积 (ASA): {result['asa_mass']:.2f} m²/g")
    print(f"可及表面积 (体积): {result['asa_volume']:.2f} m²/cm³")
    print(f"不可及表面积 (NASA): {result['nasa_mass']:.2f} m²/g")
    print()
    return result


def calculate_volume(file_path: Path, probe_radius: float = 1.82):
    """计算可及体积 (Accessible Volume)"""
    print("=" * 60)
    print(f"4. 可及体积计算 (probe_radius={probe_radius} Å)")
    print("=" * 60)
    
    with open(file_path, "rb") as f:
        files = {"structure_file": (file_path.name, f)}
        data = {
            "chan_radius": str(probe_radius),
            "probe_radius": str(probe_radius),
            "samples": "50000",
            "ha": "true"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/accessible_volume",
            files=files,
            data=data
        )
    
    result = response.json()
    print(f"单胞体积: {result['unitcell_volume']:.2f} Å³")
    print(f"密度: {result['density']:.4f} g/cm³")
    print(f"可及体积: {result['av']['mass']:.4f} cm³/g ({result['av']['fraction']*100:.2f}%)")
    print(f"不可及体积: {result['nav']['mass']:.4f} cm³/g")
    print()
    return result


def calculate_channel(file_path: Path, probe_radius: float = 1.82):
    """通道分析 (Channel Analysis)"""
    print("=" * 60)
    print(f"5. 通道分析 (probe_radius={probe_radius} Å)")
    print("=" * 60)
    
    with open(file_path, "rb") as f:
        files = {"structure_file": (file_path.name, f)}
        data = {
            "probe_radius": str(probe_radius),
            "ha": "true"
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/channel_analysis",
            files=files,
            data=data
        )
    
    result = response.json()
    dim_names = {0: "孤立孔", 1: "1D通道", 2: "2D层状", 3: "3D互连"}
    print(f"通道维度: {result['dimension']} ({dim_names.get(result['dimension'], '未知')})")
    print(f"通道包含球直径: {result['included_diameter']:.4f} Å")
    print(f"通道自由球直径: {result['free_diameter']:.4f} Å")
    print()
    return result


def get_framework_info(file_path: Path):
    """获取框架信息 (Framework Info)"""
    print("=" * 60)
    print("6. 框架信息 (Framework Info)")
    print("=" * 60)
    
    with open(file_path, "rb") as f:
        files = {"structure_file": (file_path.name, f)}
        data = {"ha": "true"}
        
        response = requests.post(
            f"{API_BASE_URL}/api/v1/framework_info",
            files=files,
            data=data
        )
    
    result = response.json()
    print(f"化学式: {result['formula']}")
    print(f"框架数量: {result['number_of_frameworks']}")
    print(f"分子数量: {result['number_of_molecules']}")
    for fw in result['frameworks']:
        print(f"  - 框架 {fw['framework_id']}: {fw['dimensionality']}D")
    print()
    return result


def full_analysis(file_path: Path):
    """完整分析流程"""
    print("\n" + "=" * 60)
    print("完整 Zeo++ 分析报告")
    print(f"结构文件: {file_path.name}")
    print("=" * 60 + "\n")
    
    # 执行所有分析
    check_health()
    pore = calculate_pore_diameter(file_path)
    sa = calculate_surface_area(file_path)
    vol = calculate_volume(file_path)
    chan = calculate_channel(file_path)
    fw = get_framework_info(file_path)
    
    # 打印汇总
    print("=" * 60)
    print("分析汇总 (Summary)")
    print("=" * 60)
    print(f"化学式: {fw['formula']}")
    print(f"最大自由球直径 (Df): {pore['free_diameter']:.4f} Å")
    print(f"最大包含球直径 (Di): {pore['included_diameter']:.4f} Å")
    print(f"可及表面积: {sa['asa_mass']:.2f} m²/g")
    print(f"可及体积分数: {vol['av']['fraction']*100:.2f}%")
    print(f"通道维度: {chan['dimension']}D")
    print()


if __name__ == "__main__":
    # 检查示例文件是否存在
    if not SAMPLE_FILE.exists():
        print(f"错误: 找不到示例文件 {SAMPLE_FILE}")
        print("请确保在正确的目录下运行此脚本")
        exit(1)
    
    # 运行完整分析
    try:
        full_analysis(SAMPLE_FILE)
        
        # 演示 force_recalculate 参数
        print("=" * 60)
        print("额外示例: 强制重新计算 (force_recalculate)")
        print("=" * 60)
        print("使用 force_recalculate=True 可以跳过缓存，强制执行 Zeo++ 计算：")
        print()
        calculate_pore_diameter(SAMPLE_FILE, force_recalculate=True)
        
    except requests.exceptions.ConnectionError:
        print(f"错误: 无法连接到 API 服务 {API_BASE_URL}")
        print("请确保 Zeo++ API 服务已启动:")
        print("  docker-compose up -d")
        exit(1)
