# Examples 示例目录

本目录包含 Zeo++ API 的完整使用示例。

## 目录结构

```
examples/
├── README.md                         # 本文件
├── sample_structures/                # 示例结构文件
│   ├── EDI.cif                      # EDI 沸石结构
│   └── HKUST-1.cif                  # HKUST-1 MOF 结构
├── python/                           # Python 示例
│   ├── basic_usage.py               # 基础 API 调用
│   ├── batch_analysis.py            # 批量分析脚本
│   ├── hkust1_acetylene_analysis.py # ⭐ MOF 乙炔吸附案例
│   └── requirements.txt             # Python 依赖
└── curl/                             # cURL 示例
    ├── api_examples.sh              # Linux/Mac 脚本
    └── api_examples.bat             # Windows 批处理
```

## 快速开始

### 1. 确保 API 服务已启动

```bash
# 在项目根目录
docker-compose up -d

# 检查服务状态
curl http://localhost:9876/health
```

### 2. Python 示例

```bash
cd examples/python
pip install -r requirements.txt

# 基础示例 - 演示所有 API 端点
python basic_usage.py

# 批量分析 - 处理多个结构文件
python batch_analysis.py ../sample_structures output.csv
```

### 3. cURL 示例

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

## 示例文件说明

### Python 示例

| 文件 | 说明 |
|------|------|
| `basic_usage.py` | 包含所有 API 端点的调用示例，适合学习 API 用法 |
| `batch_analysis.py` | 批量处理多个结构文件，支持并发请求，导出 CSV 结果 |
| `hkust1_acetylene_analysis.py` | ⭐ **完整案例**：用 HKUST-1 MOF 分析乙炔吸附性能 |

### ⭐ 重点案例：HKUST-1 乙炔吸附分析

`python/hkust1_acetylene_analysis.py` 是一个完整的应用案例，演示如何使用 Zeo++ API 分析 MOF 材料对乙炔 (C₂H₂) 的吸附性能。

**运行方式：**
```bash
cd examples/python
python hkust1_acetylene_analysis.py
```

**案例涵盖的 API 功能：**
1. `/api/v1/framework_info` - 获取框架基本信息
2. `/api/v1/pore_diameter` - 分析孔径，判断乙炔可及性
3. `/api/v1/surface_area` - 计算乙炔可及表面积（探针半径 1.65Å）
4. `/api/v1/surface_area` - 计算氮气可及表面积（对比 BET）
5. `/api/v1/accessible_volume` - 计算乙炔可及体积，估算吸附量
6. `/api/v1/channel_analysis` - 分析通道维度和连通性
7. `/api/v1/open_metal_sites` - 检测开放金属位点 (Cu²⁺)
8. `/api/v1/pore_size_dist/download` - 分析孔径分布（返回文件）
9. `/api/v1/blocking_spheres` - 检测阻塞区域

**输出示例：**
```
╔══════════════════════════════════════════════════════════════════════╗
║     HKUST-1 MOF 乙炔 (C₂H₂) 吸附性能分析                              ║
╚══════════════════════════════════════════════════════════════════════╝

======================================================================
  1. 框架基本信息 (Framework Info)
======================================================================
  材料名称: HKUST-1 (Cu-BTC, MOF-199)
  化学式: C18 H6 Cu3 O12
  ...

======================================================================
  5. 乙炔可及体积 (C2H2 Accessible Volume)
======================================================================
  探针半径 (C2H2): 1.65 Å
  C2H2 可及体积: 0.75 cm³/g
  
  📊 乙炔吸附能力估算 (理论最大值):
     估算吸附量: 200 cc(STP)/g
```

### 示例结构文件

#### sample_structures/EDI.cif

EDI（Edingtonite）沸石结构，晶系为四方晶系，包含 Si 和 O 原子。

结构特征：
- 晶胞参数: a=b=9.550Å, c=6.520Å
- 空间群: P-421m
- 典型孔径: ~3Å
- 适合测试所有 API 端点

#### sample_structures/HKUST-1.cif

HKUST-1（又称 Cu-BTC、MOF-199）是一种经典的金属有机框架（MOF）材料。

**应用场景：**
- 🔹 **乙炔 (C₂H₂) 吸附与分离** - HKUST-1 对乙炔有优异的选择性吸附能力
- 🔹 **CO₂ 捕获** - 开放金属位点增强 CO₂ 吸附
- 🔹 **H₂ 存储** - 高比表面积有利于氢气存储
- 🔹 **天然气纯化** - 分离 CH₄ 和杂质气体
- 🔹 **催化反应** - Cu²⁺ 开放位点可作为催化活性中心

**结构特征：**
- 化学式: Cu₃(BTC)₂ (BTC = 苯-1,3,5-三羧酸)
- 晶胞参数: a=b=c=26.343Å（立方晶系）
- 空间群: Fm-3m
- BET 比表面积: ~1500-2000 m²/g
- 孔体积: ~0.75 cm³/g
- 包含开放金属位点 (Open Metal Sites)

**参考文献：**
- Chui, S. S.-Y. et al., Science 1999, 283, 1148-1150
- COD ID: 2300380

## 注意事项

- 确保 Zeo++ API 服务已启动（默认 http://localhost:9876）
- 如果使用不同端口，请修改脚本中的 `API_BASE_URL`
- 批量分析脚本支持 `.cif`, `.cssr`, `.v1`, `.pdb`, `.xyz` 格式
