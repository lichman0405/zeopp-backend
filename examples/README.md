# Examples 示例目录

本目录包含 Zeo++ API 的完整使用示例。

## 目录结构

```
examples/
├── README.md               # 本文件
├── sample_structures/      # 示例结构文件
│   └── EDI.cif            # EDI 沸石结构
├── python/                 # Python 示例
│   ├── basic_usage.py     # 基础 API 调用
│   ├── batch_analysis.py  # 批量分析脚本
│   └── requirements.txt   # Python 依赖
└── curl/                   # cURL 示例
    ├── api_examples.sh    # Linux/Mac 脚本
    └── api_examples.bat   # Windows 批处理
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

### sample_structures/EDI.cif

EDI（Edingtonite）沸石结构，晶系为四方晶系，包含 Si 和 O 原子。

结构特征：
- 晶胞参数: a=b=9.550Å, c=6.520Å
- 空间群: P-421m
- 适合测试所有 API 端点

## 注意事项

- 确保 Zeo++ API 服务已启动（默认 http://localhost:9876）
- 如果使用不同端口，请修改脚本中的 `API_BASE_URL`
- 批量分析脚本支持 `.cif`, `.cssr`, `.v1`, `.pdb`, `.xyz` 格式
