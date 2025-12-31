# Zeo++ API 完整接口文档

**版本**: v0.3.1  
**基础 URL**: `http://localhost:9876`  
**API 前缀**: `/api/v1`

---

## 目录

1. [系统端点](#1-系统端点)
2. [核心分析端点](#2-核心分析端点)
   - [孔径计算](#21-孔径计算-pore_diameter)
   - [表面积计算](#22-表面积计算-surface_area)
   - [可及体积计算](#23-可及体积计算-accessible_volume)
   - [探针占据体积计算](#24-探针占据体积计算-probe_volume)
   - [通道分析](#25-通道分析-channel_analysis)
   - [孔径分布](#26-孔径分布-pore_size_dist)
   - [阻塞球生成](#27-阻塞球生成-blocking_spheres)
3. [结构信息端点](#3-结构信息端点)
   - [框架信息](#31-框架信息-framework_info)
   - [开放金属位点](#32-开放金属位点-open_metal_sites)
4. [缓存管理端点](#4-缓存管理端点)
5. [监控端点](#5-监控端点)
6. [通用参数说明](#6-通用参数说明)
7. [错误响应格式](#7-错误响应格式)

---

## 1. 系统端点

### 1.1 健康检查

**端点**: `GET /health`

**描述**: 基本健康检查，验证服务是否正常运行。

**响应示例**:
```json
{
  "status": "healthy",
  "message": "Zeo++ API is running"
}
```

---

### 1.2 详细健康检查

**端点**: `GET /health/detailed`

**描述**: 详细健康检查，包含系统信息和 Zeo++ 可用性检测。

**响应示例**:
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

### 1.3 版本信息

**端点**: `GET /version`

**描述**: 获取 API 版本信息。

**响应示例**:
```json
{
  "version": "0.3.1",
  "api_version": "v1"
}
```

---

## 2. 核心分析端点

> **通用说明**: 所有分析端点均使用 `POST` 方法，需上传结构文件，参数以 `multipart/form-data` 格式发送。

---

### 2.1 孔径计算 (pore_diameter)

**端点**: `POST /api/v1/pore_diameter`

**Zeo++ 命令**: `-res`

**描述**: 计算框架中最大包含球直径 (Di)、最大自由球直径 (Df) 和沿自由球路径的包含球直径。

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `structure_file` | File | ✅ | - | 结构文件 (.cif, .cssr, .v1, .arc) |
| `ha` | boolean | ❌ | `true` | 是否启用高精度模式 |
| `force_recalculate` | boolean | ❌ | `false` | 强制重新计算，跳过缓存 |

#### 响应格式

```json
{
  "included_diameter": 4.89082,
  "free_diameter": 3.03868,
  "included_along_free": 4.81969,
  "cached": false
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `included_diameter` | float | 最大包含球直径 Di (Å)，指结构中可容纳的最大球体 |
| `free_diameter` | float | 最大自由球直径 Df (Å)，指可沿通道自由移动的最大球体 |
| `included_along_free` | float | 沿自由球路径的包含球直径 Dif (Å) |
| `cached` | boolean | 结果是否来自缓存 |

#### cURL 示例

```bash
curl -X POST "http://localhost:9876/api/v1/pore_diameter" \
  -H "Content-Type: multipart/form-data" \
  -F "structure_file=@/path/to/structure.cif" \
  -F "ha=true"
```

---

### 2.2 表面积计算 (surface_area)

**端点**: `POST /api/v1/surface_area`

**Zeo++ 命令**: `-sa`

**描述**: 使用蒙特卡洛采样方法计算可及表面积 (ASA) 和不可及表面积 (NASA)。

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `structure_file` | File | ✅ | - | 结构文件 (.cif, .cssr, .v1, .arc) |
| `chan_radius` | float | ❌ | `1.21` | 通道半径 (Å)，用于确定空间可及性 |
| `probe_radius` | float | ❌ | `1.21` | 探针半径 (Å)，用于蒙特卡洛采样 |
| `samples` | integer | ❌ | `2000` | 蒙特卡洛采样点数 |
| `ha` | boolean | ❌ | `true` | 是否启用高精度模式 |
| `force_recalculate` | boolean | ❌ | `false` | 强制重新计算，跳过缓存 |

> ⚠️ **约束**: `probe_radius` 必须 ≤ `chan_radius`

#### 响应格式

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

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `asa_unitcell` | float | 可及表面积 (Å²/单胞) |
| `asa_volume` | float | 可及表面积 (m²/cm³) |
| `asa_mass` | float | 可及表面积 (m²/g) |
| `nasa_unitcell` | float | 不可及表面积 (Å²/单胞) |
| `nasa_volume` | float | 不可及表面积 (m²/cm³) |
| `nasa_mass` | float | 不可及表面积 (m²/g) |
| `cached` | boolean | 结果是否来自缓存 |

#### cURL 示例

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

### 2.3 可及体积计算 (accessible_volume)

**端点**: `POST /api/v1/accessible_volume`

**Zeo++ 命令**: `-vol`

**描述**: 使用蒙特卡洛采样计算可及体积 (AV) 和不可及体积 (NAV)。

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `structure_file` | File | ✅ | - | 结构文件 (.cif, .cssr, .v1, .arc) |
| `chan_radius` | float | ❌ | `1.21` | 通道半径 (Å) |
| `probe_radius` | float | ❌ | `1.21` | 探针半径 (Å) |
| `samples` | integer | ❌ | `50000` | 蒙特卡洛采样点数（推荐 50000） |
| `ha` | boolean | ❌ | `true` | 是否启用高精度模式 |
| `force_recalculate` | boolean | ❌ | `false` | 强制重新计算，跳过缓存 |

> ⚠️ **约束**: `probe_radius` 必须 ≤ `chan_radius`

#### 响应格式

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

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `unitcell_volume` | float | 单胞体积 (Å³) |
| `density` | float | 密度 (g/cm³) |
| `av.unitcell` | float | 可及体积 (Å³) |
| `av.fraction` | float | 可及体积分数 |
| `av.mass` | float | 可及体积 (cm³/g) |
| `nav.unitcell` | float | 不可及体积 (Å³) |
| `nav.fraction` | float | 不可及体积分数 |
| `nav.mass` | float | 不可及体积 (cm³/g) |
| `cached` | boolean | 结果是否来自缓存 |

#### cURL 示例

```bash
curl -X POST "http://localhost:9876/api/v1/accessible_volume" \
  -H "Content-Type: multipart/form-data" \
  -F "structure_file=@/path/to/structure.cif" \
  -F "chan_radius=1.82" \
  -F "probe_radius=1.82" \
  -F "samples=50000" \
  -F "ha=true"
```

---

### 2.4 探针占据体积计算 (probe_volume)

**端点**: `POST /api/v1/probe_volume`

**Zeo++ 命令**: `-volpo`

**描述**: 计算探针可占据体积 (POAV) 和探针不可占据体积 (PONAV)。

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `structure_file` | File | ✅ | - | 结构文件 (.cif, .cssr, .v1, .arc) |
| `chan_radius` | float | ❌ | `1.21` | 通道半径 (Å) |
| `probe_radius` | float | ❌ | `1.21` | 探针半径 (Å) |
| `samples` | integer | ❌ | `50000` | 蒙特卡洛采样点数 |
| `ha` | boolean | ❌ | `true` | 是否启用高精度模式 |
| `force_recalculate` | boolean | ❌ | `false` | 强制重新计算，跳过缓存 |

> ⚠️ **约束**: `probe_radius` 必须 ≤ `chan_radius`

#### 响应格式

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

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `poav_unitcell` | float | 探针可占据体积 (Å³) |
| `poav_fraction` | float | 探针可占据体积分数 |
| `poav_mass` | float | 探针可占据体积 (cm³/g) |
| `ponav_unitcell` | float | 探针不可占据体积 (Å³) |
| `ponav_fraction` | float | 探针不可占据体积分数 |
| `ponav_mass` | float | 探针不可占据体积 (cm³/g) |
| `cached` | boolean | 结果是否来自缓存 |

---

### 2.5 通道分析 (channel_analysis)

**端点**: `POST /api/v1/channel_analysis`

**Zeo++ 命令**: `-chan`

**描述**: 分析框架中的通道系统，识别通道维度和几何特性。

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `structure_file` | File | ✅ | - | 结构文件 (.cif, .cssr, .v1, .arc) |
| `probe_radius` | float | ❌ | `1.21` | 探针半径 (Å) |
| `ha` | boolean | ❌ | `true` | 是否启用高精度模式 |
| `force_recalculate` | boolean | ❌ | `false` | 强制重新计算，跳过缓存 |

#### 响应格式

```json
{
  "dimension": 3,
  "included_diameter": 4.89082,
  "free_diameter": 3.03868,
  "included_along_free": 4.89082,
  "cached": false
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `dimension` | integer | 通道维度 (0=孤立孔, 1=1D通道, 2=2D层状, 3=3D互连) |
| `included_diameter` | float | 通道包含球直径 (Å) |
| `free_diameter` | float | 通道自由球直径 (Å) |
| `included_along_free` | float | 沿自由球路径的包含球直径 (Å) |
| `cached` | boolean | 结果是否来自缓存 |

---

### 2.6 孔径分布 (pore_size_dist)

**端点**: `POST /api/v1/pore_size_dist/download`

**Zeo++ 命令**: `-psd`

**描述**: 计算孔径分布直方图并下载数据文件。

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `structure_file` | File | ✅ | - | 结构文件 (.cif, .cssr, .v1, .arc) |
| `probe_radius` | float | ❌ | `1.21` | 探针半径 (Å) |
| `chan_radius` | float | ❌ | `null` | 通道半径 (Å)，默认等于 probe_radius |
| `samples` | integer | ❌ | `50000` | 蒙特卡洛采样点数 |
| `ha` | boolean | ❌ | `true` | 是否启用高精度模式 |
| `force_recalculate` | boolean | ❌ | `false` | 强制重新计算，跳过缓存 |

#### 响应格式

返回 `.psd_histo` 文件下载，Content-Type: `text/plain`

#### cURL 示例

```bash
curl -X POST "http://localhost:9876/api/v1/pore_size_dist/download" \
  -H "Content-Type: multipart/form-data" \
  -F "structure_file=@/path/to/structure.cif" \
  -F "samples=50000" \
  -o psd_histogram.txt
```

---

### 2.7 阻塞球生成 (blocking_spheres)

**端点**: `POST /api/v1/blocking_spheres`

**Zeo++ 命令**: `-block`

**描述**: 识别不可及区域并生成用于分子模拟（如 RASPA）的阻塞球。

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `structure_file` | File | ✅ | - | 结构文件 (.cif, .cssr, .v1, .arc) |
| `probe_radius` | float | ❌ | `1.86` | 探针半径 (Å)，默认为甲烷半径 |
| `samples` | integer | ❌ | `50000` | 蒙特卡洛采样点数 |
| `ha` | boolean | ❌ | `true` | 是否启用高精度模式 |
| `force_recalculate` | boolean | ❌ | `false` | 强制重新计算，跳过缓存 |

#### 响应格式

```json
{
  "channels": 1,
  "pockets": 2,
  "nodes_assigned": 139,
  "raw": "Identified 1 channels and 2 pockets\n139 nodes assigned to pores.",
  "cached": false
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `channels` | integer | 识别到的通道数量 |
| `pockets` | integer | 识别到的孔穴数量 |
| `nodes_assigned` | integer | 分配给孔隙的节点数 |
| `raw` | string | 原始输出文本 |
| `cached` | boolean | 结果是否来自缓存 |

---

## 3. 结构信息端点

### 3.1 框架信息 (framework_info)

**端点**: `POST /api/v1/framework_info`

**Zeo++ 命令**: `-strinfo`

**描述**: 识别结构中框架的数量及其维度信息。

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `structure_file` | File | ✅ | - | 结构文件 (.cif, .cssr) |
| `ha` | boolean | ❌ | `true` | 是否启用高精度模式 |
| `force_recalculate` | boolean | ❌ | `false` | 强制重新计算，跳过缓存 |

#### 响应格式

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

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `filename` | string | 输出文件名 |
| `formula` | string | 化学式 |
| `segments` | integer | 结构段数 |
| `number_of_frameworks` | integer | 框架数量 |
| `number_of_molecules` | integer | 分子数量 |
| `frameworks` | array | 框架详细信息列表 |
| `frameworks[].framework_id` | integer | 框架 ID |
| `frameworks[].dimensionality` | integer | 框架维度 (1D/2D/3D) |
| `cached` | boolean | 结果是否来自缓存 |

---

### 3.2 开放金属位点 (open_metal_sites)

**端点**: `POST /api/v1/open_metal_sites`

**Zeo++ 命令**: `-oms`

**描述**: 自动检测并计算结构中的开放金属位点数量。

#### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 描述 |
|------|------|------|--------|------|
| `structure_file` | File | ✅ | - | 结构文件 (.cif, .cssr) |
| `ha` | boolean | ❌ | `true` | 是否启用高精度模式 |
| `force_recalculate` | boolean | ❌ | `false` | 强制重新计算，跳过缓存 |

#### 响应格式

```json
{
  "open_metal_sites_count": 4,
  "cached": false
}
```

#### 响应字段说明

| 字段 | 类型 | 描述 |
|------|------|------|
| `open_metal_sites_count` | integer | 开放金属位点数量 |
| `cached` | boolean | 结果是否来自缓存 |

---

## 4. 缓存管理端点

### 4.1 缓存统计

**端点**: `GET /api/v1/cache/stats`

**描述**: 获取当前缓存使用统计信息。

**响应示例**:
```json
{
  "temp_files": 15,
  "cache_entries": 42,
  "total_size_mb": 12.5
}
```

---

### 4.2 清理临时文件

**端点**: `POST /api/v1/cache/cleanup`

**描述**: 清理过期的临时文件。

**响应示例**:
```json
{
  "message": "Cleanup completed",
  "files_removed": 8
}
```

---

### 4.3 清除所有缓存

**端点**: `DELETE /api/v1/cache/clear`

**描述**: 清除所有缓存数据。

**响应示例**:
```json
{
  "message": "All cache cleared",
  "entries_removed": 42
}
```

---

## 5. 监控端点

### 5.1 Prometheus 指标

**端点**: `GET /metrics`

**描述**: Prometheus 格式的监控指标，用于监控系统抓取。

**响应格式**: `text/plain`

```
# HELP zeopp_uptime_seconds Service uptime in seconds
# TYPE zeopp_uptime_seconds gauge
zeopp_uptime_seconds 3600.00

# HELP zeopp_requests_total Total number of requests
# TYPE zeopp_requests_total counter
zeopp_requests_total 1234
```

---

### 5.2 指标摘要

**端点**: `GET /api/v1/metrics/summary`

**描述**: JSON 格式的指标摘要。

**响应示例**:
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

## 6. 通用参数说明

### 6.1 高精度模式 (`ha`)

| 值 | 描述 |
|---|---|
| `true` | 启用高精度模式，使用精确几何计算（推荐） |
| `false` | 使用近似计算，速度更快但精度略低 |

**建议**: 对于 MOF/沸石等复杂材料，始终使用 `ha=true`。

---

### 6.2 强制重新计算 (`force_recalculate`)

| 值 | 描述 |
|---|---|
| `false` | 默认值，如果缓存中存在相同结构和参数的结果，直接返回缓存 |
| `true` | 跳过缓存检查，强制执行 Zeo++ 计算并更新缓存 |

**使用场景**:
- 当需要确保获取最新计算结果时
- 调试或测试时需要完整运行 Zeo++
- 怀疑缓存结果可能不正确时

**示例**:
```bash
curl -X POST "http://localhost:9876/api/v1/pore_diameter" \
  -F "structure_file=@HKUST-1.cif" \
  -F "force_recalculate=true"
```

---

### 6.4 探针半径参考

根据研究的分子选择合适的探针半径：

| 分子 | 半径 (Å) | 常用场景 |
|------|----------|----------|
| 氦气 (He) | 1.29 | 理论最大孔隙率 |
| 氢气 (H₂) | 1.45 | 储氢研究 |
| 二氧化碳 (CO₂) | 1.65 | 碳捕获 |
| 氮气 (N₂) | 1.82 | BET 表面积对比 |
| 甲烷 (CH₄) | 1.86 | 天然气储存 |
| 水 (H₂O) | 1.40 | 亲水性研究 |

---

### 6.5 采样点数建议

| 分析类型 | 快速预览 | 生产精度 | 高精度研究 |
|----------|----------|----------|------------|
| 表面积 (`-sa`) | 500-1000 | **2000** | 5000+ |
| 体积 (`-vol`, `-volpo`) | 10000 | **50000** | 100000+ |
| 孔径分布 (`-psd`) | 10000 | **50000** | 100000+ |
| 阻塞球 (`-block`) | 10000 | **50000** | 100000+ |

---

### 6.6 支持的文件格式

| 扩展名 | 格式 | 描述 |
|--------|------|------|
| `.cif` | Crystallographic Information File | 最常用的晶体结构格式 |
| `.cssr` | Cambridge Structural Search and Retrieval | 剑桥结构数据库格式 |
| `.v1` | Zeo++ V1 格式 | Zeo++ 原生格式 |
| `.arc` | Accelrys Archive | Materials Studio 格式 |
| `.pdb` | Protein Data Bank | 蛋白质数据库格式 |
| `.xyz` | XYZ 坐标文件 | 简单笛卡尔坐标格式 |

---

## 7. 错误响应格式

所有错误响应遵循统一格式：

```json
{
  "detail": "错误描述信息",
  "error_code": "ERROR_TYPE"
}
```

### 常见错误码

| HTTP 状态码 | 错误码 | 描述 |
|-------------|--------|------|
| 400 | `VALIDATION_ERROR` | 请求参数验证失败 |
| 422 | `VALIDATION_ERROR` | 参数约束不满足（如 probe_radius > chan_radius） |
| 429 | `RATE_LIMIT_ERROR` | 请求频率超限 |
| 500 | `EXECUTION_ERROR` | Zeo++ 执行失败 |
| 500 | `PARSE_ERROR` | 输出解析失败 |
| 500 | `TIMEOUT_ERROR` | 计算超时 |

---

## 附录：响应头

所有响应包含以下自定义头：

| 头部 | 描述 |
|------|------|
| `X-Request-ID` | 唯一请求标识符，用于追踪和调试 |
| `X-Process-Time` | 请求处理时间（如 `125.5ms`） |

---

*文档更新日期：2025-12-31*  
*API 版本：v0.3.1*
