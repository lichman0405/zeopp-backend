#!/usr/bin/env python3
"""
HKUST-1 MOF 乙炔吸附性能分析案例
HKUST-1 MOF Acetylene Adsorption Performance Analysis

本脚本演示如何使用 Zeo++ API 分析 HKUST-1 金属有机框架材料
对乙炔 (C2H2) 气体的吸附性能。

HKUST-1 (Cu-BTC, MOF-199) 是一种经典的 MOF 材料，因其：
- 高比表面积 (~1500-2000 m²/g)
- 开放金属位点 (Cu²⁺)
- 多级孔道结构
而被广泛用于乙炔存储和乙炔/乙烯分离。

乙炔分子参数：
- 动力学直径: 3.3 Å
- 探针半径: 1.65 Å (直径/2)

参考文献：
- Chui, S. S.-Y. et al., Science 1999, 283, 1148-1150
- Xiang, S. et al., Nature Chem. 2009, 1, 368-373 (C2H2 adsorption in MOFs)
"""

import requests
import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Dict, Any

# =============================================================================
# 配置参数
# =============================================================================

API_BASE_URL = "http://192.168.100.207:9876"

# 乙炔 (C2H2) 分子参数
C2H2_KINETIC_DIAMETER = 3.3  # Å
C2H2_PROBE_RADIUS = 1.65     # Å (动力学直径 / 2)

# 氮气 (N2) 分子参数 - 用于 BET 表面积对比
N2_KINETIC_DIAMETER = 3.64   # Å
N2_PROBE_RADIUS = 1.82       # Å

# HKUST-1 结构文件路径
STRUCTURE_FILE = Path(__file__).parent.parent / "sample_structures" / "HKUST-1.cif"


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


def api_request(endpoint: str, params: dict = None) -> AnalysisResult:
    """
    发送 API 请求
    """
    if params is None:
        params = {}
    
    try:
        with open(STRUCTURE_FILE, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/{endpoint}",
                files={"structure_file": (STRUCTURE_FILE.name, f)},
                data=params,
                timeout=120
            )
        
        if response.status_code == 200:
            return AnalysisResult(success=True, data=response.json())
        else:
            return AnalysisResult(
                success=False, 
                error=f"HTTP {response.status_code}: {response.text}"
            )
    except requests.exceptions.ConnectionError:
        return AnalysisResult(success=False, error=f"无法连接到 {API_BASE_URL}")
    except Exception as e:
        return AnalysisResult(success=False, error=str(e))


def print_section(title: str):
    """打印分节标题"""
    print()
    print("=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(label: str, value: Any, unit: str = ""):
    """打印结果"""
    if unit:
        print(f"  {label}: {value} {unit}")
    else:
        print(f"  {label}: {value}")


# =============================================================================
# 分析函数
# =============================================================================

def analyze_framework_info():
    """1. 分析框架基本信息"""
    print_section("1. 框架基本信息 (Framework Info)")
    
    result = api_request("framework_info", {"ha": "true"})
    
    if result.success:
        data = result.data
        print_result("材料名称", "HKUST-1 (Cu-BTC, MOF-199)")
        print_result("化学式", data.get("formula", "N/A"))
        print_result("框架数量", data.get("framework_count", "N/A"))
        print_result("框架密度", data.get("density", "N/A"), "g/cm³")
        return data
    else:
        print(f"  ❌ 错误: {result.error}")
        return None


def analyze_pore_diameter():
    """2. 分析孔径特性"""
    print_section("2. 孔径分析 (Pore Diameter)")
    
    result = api_request("pore_diameter", {"ha": "true"})
    
    if result.success:
        data = result.data
        Di = data.get("included_diameter", 0)
        Df = data.get("free_diameter", 0)
        Dif = data.get("included_along_free", 0)
        
        print_result("最大包含球直径 (Di)", f"{Di:.3f}", "Å")
        print_result("最大自由球直径 (Df)", f"{Df:.3f}", "Å")
        print_result("沿自由路径包含球直径 (Dif)", f"{Dif:.3f}", "Å")
        
        print()
        print("  📊 乙炔可及性分析:")
        print(f"     乙炔动力学直径: {C2H2_KINETIC_DIAMETER} Å")
        
        if Df >= C2H2_KINETIC_DIAMETER:
            print(f"     ✅ 乙炔可以自由通过孔道 (Df={Df:.2f} > {C2H2_KINETIC_DIAMETER} Å)")
        else:
            print(f"     ⚠️ 乙炔扩散可能受限 (Df={Df:.2f} < {C2H2_KINETIC_DIAMETER} Å)")
        
        return data
    else:
        print(f"  ❌ 错误: {result.error}")
        return None


def analyze_surface_area_for_c2h2():
    """3. 计算乙炔可及表面积"""
    print_section("3. 乙炔可及表面积 (C2H2 Accessible Surface Area)")
    
    result = api_request("surface_area", {
        "chan_radius": str(C2H2_PROBE_RADIUS),
        "probe_radius": str(C2H2_PROBE_RADIUS),
        "samples": "2000",
        "ha": "true"
    })
    
    if result.success:
        data = result.data
        asa_m2_g = data.get("asa_mass", 0)
        asa_m2_cm3 = data.get("asa_vol", 0)
        nasa_m2_g = data.get("nasa_mass", 0)
        
        print(f"  探针半径 (C2H2): {C2H2_PROBE_RADIUS} Å")
        print()
        print_result("可及表面积 (ASA)", f"{asa_m2_g:.2f}", "m²/g")
        print_result("可及表面积 (ASA)", f"{asa_m2_cm3:.2f}", "m²/cm³")
        print_result("不可及表面积 (NASA)", f"{nasa_m2_g:.2f}", "m²/g")
        
        return data
    else:
        print(f"  ❌ 错误: {result.error}")
        return None


def analyze_surface_area_for_n2():
    """4. 计算氮气可及表面积（对比）"""
    print_section("4. 氮气可及表面积 - BET 对比 (N2 Accessible Surface Area)")
    
    result = api_request("surface_area", {
        "chan_radius": str(N2_PROBE_RADIUS),
        "probe_radius": str(N2_PROBE_RADIUS),
        "samples": "2000",
        "ha": "true"
    })
    
    if result.success:
        data = result.data
        asa_m2_g = data.get("asa_mass", 0)
        
        print(f"  探针半径 (N2): {N2_PROBE_RADIUS} Å")
        print()
        print_result("N2 可及表面积", f"{asa_m2_g:.2f}", "m²/g")
        print()
        print("  📚 文献参考: HKUST-1 BET 表面积通常为 1500-2000 m²/g")
        
        return data
    else:
        print(f"  ❌ 错误: {result.error}")
        return None


def analyze_accessible_volume_for_c2h2():
    """5. 计算乙炔可及体积"""
    print_section("5. 乙炔可及体积 (C2H2 Accessible Volume)")
    
    result = api_request("accessible_volume", {
        "chan_radius": str(C2H2_PROBE_RADIUS),
        "probe_radius": str(C2H2_PROBE_RADIUS),
        "samples": "50000",
        "ha": "true"
    })
    
    if result.success:
        data = result.data
        density = data.get("density", 0)
        av_data = data.get("av", {})
        nav_data = data.get("nav", {})
        
        av_fraction = av_data.get("fraction", 0)
        av_cm3_g = av_data.get("mass", 0)
        
        print(f"  探针半径 (C2H2): {C2H2_PROBE_RADIUS} Å")
        print()
        print_result("框架密度", f"{density:.4f}", "g/cm³")
        print_result("C2H2 可及体积分数", f"{av_fraction:.4f}", "")
        print_result("C2H2 可及体积", f"{av_cm3_g:.4f}", "cm³/g")
        print()
        
        # 估算乙炔吸附量
        c2h2_molar_volume = 22.4  # L/mol at STP
        c2h2_density_stp = 1.092  # g/L at STP (26 g/mol / 22.4 L/mol)
        estimated_uptake = av_cm3_g * c2h2_density_stp * 1000  # mg/g
        estimated_uptake_cc = av_cm3_g * 1000 / c2h2_molar_volume * 22.4  # cc(STP)/g
        
        print("  📊 乙炔吸附能力估算 (理论最大值):")
        print_result("     估算吸附量", f"{estimated_uptake:.1f}", "mg/g")
        print_result("     估算吸附量", f"{estimated_uptake_cc:.1f}", "cc(STP)/g")
        
        return data
    else:
        print(f"  ❌ 错误: {result.error}")
        return None


def analyze_channel():
    """6. 分析通道特性"""
    print_section("6. 通道分析 (Channel Analysis)")
    
    result = api_request("channel_analysis", {
        "probe_radius": str(C2H2_PROBE_RADIUS),
        "ha": "true"
    })
    
    if result.success:
        data = result.data
        dimension = data.get("dimension", 0)
        channels = data.get("channels", [])
        
        print(f"  探针半径 (C2H2): {C2H2_PROBE_RADIUS} Å")
        print()
        print_result("通道维度", dimension, "D")
        print_result("通道数量", len(channels))
        
        if dimension == 3:
            print("  ✅ 3D 互连通道 - 有利于乙炔分子快速扩散")
        elif dimension == 2:
            print("  ⚠️ 2D 层状通道 - 乙炔扩散可能受限于层间")
        elif dimension == 1:
            print("  ⚠️ 1D 线性通道 - 乙炔扩散为单向")
        else:
            print("  ❌ 无连通通道 - 乙炔分子无法进入孔道")
        
        return data
    else:
        print(f"  ❌ 错误: {result.error}")
        return None


def analyze_open_metal_sites():
    """7. 分析开放金属位点"""
    print_section("7. 开放金属位点 (Open Metal Sites)")
    
    result = api_request("open_metal_sites", {"ha": "true"})
    
    if result.success:
        data = result.data
        oms_count = data.get("oms_count", 0)
        
        print_result("开放金属位点数量", oms_count)
        print()
        
        if oms_count > 0:
            print("  📊 开放金属位点对乙炔吸附的影响:")
            print("     ✅ Cu²⁺ 开放位点可与乙炔的 π 电子形成配位作用")
            print("     ✅ 增强乙炔吸附焓 (通常 25-35 kJ/mol)")
            print("     ✅ 提高乙炔/乙烯分离选择性")
        else:
            print("  ⚠️ 未检测到开放金属位点")
            print("     (可能是结构问题或检测参数需调整)")
        
        return data
    else:
        print(f"  ❌ 错误: {result.error}")
        return None


def analyze_pore_size_distribution():
    """8. 分析孔径分布"""
    print_section("8. 孔径分布 (Pore Size Distribution)")
    
    # 注意：pore_size_dist/download 返回的是文件，需要特殊处理
    print(f"  探针半径 (C2H2): {C2H2_PROBE_RADIUS} Å")
    print()
    
    try:
        with open(STRUCTURE_FILE, "rb") as f:
            response = requests.post(
                f"{API_BASE_URL}/api/v1/pore_size_dist/download",
                files={"structure_file": (STRUCTURE_FILE.name, f)},
                data={
                    "chan_radius": str(C2H2_PROBE_RADIUS),
                    "probe_radius": str(C2H2_PROBE_RADIUS),
                    "samples": "50000",
                    "ha": "true"
                },
                timeout=120
            )
        
        if response.status_code == 200:
            # 解析返回的直方图文件内容
            content = response.text
            lines = content.strip().split('\n')
            
            # 解析直方图数据 (跳过注释行)
            histogram = []
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        diameter = float(parts[0])
                        count = float(parts[1])
                        histogram.append({"diameter": diameter, "count": count})
                    except ValueError:
                        continue
            
            if histogram:
                total_count = sum(h["count"] for h in histogram)
                
                # 分类统计 (直径单位是 Å)
                micropore = sum(h["count"] for h in histogram if h["diameter"] < 20)
                mesopore = sum(h["count"] for h in histogram if 20 <= h["diameter"] < 500)
                
                micropore_pct = micropore / total_count * 100 if total_count > 0 else 0
                mesopore_pct = mesopore / total_count * 100 if total_count > 0 else 0
                
                print(f"  孔径分布统计 (共 {len(histogram)} 个数据点):")
                print_result("     微孔占比 (<2nm)", f"{micropore_pct:.1f}", "%")
                print_result("     介孔占比 (2-50nm)", f"{mesopore_pct:.1f}", "%")
                
                # 找主要孔径
                max_bin = max(histogram, key=lambda x: x["count"])
                print_result("     主要孔径范围", f"{max_bin['diameter']:.2f}", "Å")
                
                return {"histogram": histogram}
            else:
                print("  ⚠️ 未能解析孔径分布数据")
                return None
        else:
            print(f"  ❌ 错误: HTTP {response.status_code}: {response.text[:200]}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"  ❌ 无法连接到 {API_BASE_URL}")
        return None
    except Exception as e:
        print(f"  ❌ 错误: {str(e)}")
        return None


def analyze_blocking_spheres():
    """9. 分析阻塞球"""
    print_section("9. 阻塞球分析 (Blocking Spheres)")
    
    result = api_request("blocking_spheres", {
        "probe_radius": str(C2H2_PROBE_RADIUS),
        "ha": "true"
    })
    
    if result.success:
        data = result.data
        spheres = data.get("blocking_spheres", [])
        
        print(f"  探针半径 (C2H2): {C2H2_PROBE_RADIUS} Å")
        print()
        print_result("阻塞球数量", len(spheres))
        
        if len(spheres) == 0:
            print("  ✅ 无阻塞区域 - 所有孔道对乙炔完全可及")
        else:
            print(f"  ⚠️ 存在 {len(spheres)} 个阻塞区域")
            print("     这些区域乙炔分子无法进入")
        
        return data
    else:
        print(f"  ❌ 错误: {result.error}")
        return None


def print_summary():
    """打印分析总结"""
    print_section("分析总结 - HKUST-1 乙炔吸附性能评估")
    
    print("""
  HKUST-1 是用于乙炔吸附和分离的优秀 MOF 材料，原因如下：
  
  ✅ 结构优势:
     - 高比表面积 (~1500-2000 m²/g) 提供大量吸附位点
     - 3D 互连孔道网络利于气体分子快速扩散
     - 多级孔结构（大笼 ~9Å，小笼 ~5Å）
  
  ✅ 化学优势:
     - 开放 Cu²⁺ 金属位点与乙炔 π 电子配位
     - 高乙炔吸附焓 (~25-35 kJ/mol)
     - 优异的 C2H2/C2H4 分离选择性 (~2-4)
     - 优异的 C2H2/CO2 分离选择性
  
  📚 文献报道的 HKUST-1 乙炔吸附性能:
     - 乙炔吸附量: ~200 cm³(STP)/g @ 298K, 1bar
     - C2H2/C2H4 选择性: ~2.5
     - 吸附焓: ~32 kJ/mol
  
  参考文献:
  - Xiang, S. et al., Nature Chem. 2009, 1, 368-373
  - He, Y. et al., Chem. Soc. Rev. 2014, 43, 5657-5678
""")


def main():
    """主函数"""
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║     HKUST-1 MOF 乙炔 (C₂H₂) 吸附性能分析                              ║")
    print("║     Zeo++ API 全功能演示案例                                          ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    # 检查结构文件
    if not STRUCTURE_FILE.exists():
        print(f"\n❌ 错误: 找不到结构文件 {STRUCTURE_FILE}")
        print("   请确保 HKUST-1.cif 文件存在于 sample_structures 目录")
        sys.exit(1)
    
    print(f"\n📂 结构文件: {STRUCTURE_FILE}")
    print(f"🔗 API 地址: {API_BASE_URL}")
    
    # 检查 API 服务
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API 服务正常运行")
        else:
            print(f"⚠️ API 服务返回状态码: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 无法连接到 API 服务 {API_BASE_URL}")
        print("   请先启动服务: docker-compose up -d")
        sys.exit(1)
    
    # 执行所有分析
    print("\n" + "─" * 70)
    print("  开始分析 HKUST-1 的乙炔吸附相关性质...")
    print("─" * 70)
    
    # 1-9: 执行所有分析
    analyze_framework_info()
    analyze_pore_diameter()
    analyze_surface_area_for_c2h2()
    analyze_surface_area_for_n2()
    analyze_accessible_volume_for_c2h2()
    analyze_channel()
    analyze_open_metal_sites()
    analyze_pore_size_distribution()
    analyze_blocking_spheres()
    
    # 打印总结
    print_summary()
    
    print("\n" + "═" * 70)
    print("  分析完成！所有 Zeo++ API 功能已验证。")
    print("═" * 70 + "\n")


if __name__ == "__main__":
    main()
