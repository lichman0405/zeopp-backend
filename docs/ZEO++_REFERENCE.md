# Zeo++ 官方功能参考指南 (ZEO++ Reference Guide)

本文件基于 Zeo++ 官方文档 (http://www.zeoplusplus.org/) 整理，旨在为 Zeo++ API 服务提供详尽的后台功能参考。

---

## 1. 核心概念与全局参数

### 1.1 Voronoi 分解与高精度模式 (`-ha`)
Zeo++ 的核心算法基于 Voronoi 分解。默认情况下，程序使用 **Radical Approximation**（根式近似）来处理原子半径。
- **问题**：当系统中存在半径差异较大的原子（如沸石中的 Si 和 O）时，默认近似可能导致孔径和可达性分析出现误差。
- **解决方案**：强烈建议使用 **`-ha` (High Accuracy)** 标志。它能将最大预期误差降低到 **0.1 Å** 以下。

### 1.2 原子半径与质量 (`-r`, `-mass`)
- **默认值**：Zeo++ 内置了 CCDC（剑桥晶体学数据中心）的原子半径和质量表。
- **自定义半径 (`-r <file>`)**：提供一个包含两列（原子类型、半径）的文件。
- **自定义质量 (`-mass <file>`)**：提供一个包含两列（原子类型、质量）的文件。
- **禁用半径 (`-nor`)**：将所有原子视为点粒子（半径为 0）。
- **禁用质量 (`-nomass`)**：不使用质量信息。

---

## 2. 核心分析功能详解

### 2.1 孔径分析 (Pore Diameters)
**命令**：`-res [output_file]`
**输出内容**：
- **Di (Largest Included Sphere)**：材料中可以容纳的最大球体直径。
- **Df (Largest Free Sphere)**：能够穿过材料通道的最大球体直径。
- **Dif (Largest Included Sphere along Free Sphere Path)**：在最大自由球路径上能容纳的最大球体直径。

### 2.2 表面积计算 (Surface Area)
**命令**：`-sa chan_radius probe_radius num_samples [output_file]`
- **chan_radius**：用于确定孔隙可达性的探针半径。
- **probe_radius**：用于 Monte Carlo 采样的探针半径（建议 `probe_radius = chan_radius`）。
- **num_samples**：每个原子的采样点数（推荐值：**2000**）。
**输出内容**：
- **ASA (Accessible Surface Area)**：可达表面积。
- **NASA (Non-accessible Surface Area)**：不可达（封闭孔隙）表面积。

### 2.3 可达体积计算 (Accessible Volume)
**命令**：`-vol chan_radius probe_radius num_samples [output_file]`
- **参数含义**：同表面积计算。
- **num_samples**：每个单元格的采样总数（推荐值：**50000**）。
**输出内容**：
- **AV (Accessible Volume)**：可达体积。
- **NAV (Non-accessible Volume)**：不可达体积。
- 提供单位：Å³、体积占比、cm³/g。

### 2.4 探针占据体积 (Probe-occupiable Volume)
**命令**：`-volpo chan_radius probe_radius num_samples [output_file]`
- **定义**：与 AV 不同，POAV 定义为材料中能容纳整个探针体积的空间。
- **参数建议**：`chan_radius = probe_radius`，`num_samples = 50000`。

### 2.5 通道识别与维度分析 (Channel Analysis)
**命令**：`-chan probe_radius [output_file]`
- **功能**：识别在给定探针半径下，材料内部的通道系统及其空间维度（0D, 1D, 2D, 3D）。
- **输出**：每个通道系统的 Di, Df, Dif。

### 2.6 孔径尺寸分布 (Pore Size Distribution - PSD)
**命令**：`-psd chan_radius probe_radius num_samples [output_file]`
- **功能**：计算可达体积随探针尺寸变化的分布直方图。
- **注意**：默认直方图包含 1000 个 bin，步长为 0.1 Å。

### 2.7 阻塞球分析 (Blocking Spheres)
**命令**：`-block probe_radius num_samples [output_file]`
- **功能**：识别不可达区域并生成“阻塞球”，常用于分子模拟（如 RASPA）以排除不可达空间。

### 2.8 结构分析 (Structure Info & OMS)
- **`-strinfo`**：分析原子连接矩阵，识别框架维度和分子数量。
- **`-oms`**：自动检测并计数 MOF 结构中的 **Open Metal Sites (开放金属位点)**。

---

## 3. 输入文件格式支持

Zeo++ 支持多种常见的晶体结构格式，但要求必须是 **P1 对称性**（即包含完整的单元格）：

- **CSSR** (.cssr)：最常用的格式，包含单元格定义和原子分数坐标。
- **CIF** (.cif)：支持读取，但如果包含对称性操作，Zeo++ 会尝试构建完整单元格。
- **V1** (.v1)：Zeo++ 自定义格式，包含单元格矢量和笛卡尔坐标。
- **CUC** (.cuc)：Zeo++ 自定义格式，简化版的 CSSR。
- **其他**：支持 .xyz, .pdb, .car, .arc (MOPAC) 等。

---

## 4. 最佳实践建议

1. **始终开启 `-ha`**：除非对计算速度有极高要求且原子半径统一，否则应默认开启高精度模式。
2. **探针半径选择**：
   - 模拟 $CO_2$：建议半径约 1.65 Å。
   - 模拟 $N_2$：建议半径约 1.82 Å。
   - 模拟 $H_2$：建议半径约 1.45 Å。
3. **采样点数**：
   - 对于生产环境，`-sa` 的 `num_samples` 不应低于 2000。
   - 对于 `-vol` 和 `-psd`，`num_samples` 建议在 50000 到 100000 之间以获得稳定的统计结果。
4. **原子名称清理**：如果输入文件来自模拟软件（如 `O_12`），建议使用 `-stripatomnames` 标志以正确匹配内置半径表。

---
*文档更新日期：2025-12-31*
