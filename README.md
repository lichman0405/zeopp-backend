<div align="center">
  <a href="https://github.com/lichman0405/zeopp-backend.git">
    <img src="assets/edit_logo.png" alt="Logo" width="200px">
  </a>
  
  <h1 align="center">Zeo++ API & MCP Service</h1>
  
  <p align="center">
    一个生产级的 Zeo++ 结构分析服务，支持 HTTP API 和 stdio MCP 双模式，可直接接入 Agent 工作流。
    <br>
    <a href="./README-en.md"><strong>English</strong></a>
    ·
    <a href="https://github.com/lichman0405/zeopp-backend.git/issues">报告 Bug</a>
    ·
    <a href="https://github.com/lichman0405/zeopp-backend.git/issues">提出新特性</a>
  </p>
</div>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker)
[![GitHub issues](https://img.shields.io/github/issues/lichman0405/zeopp-backend.svg)](https://github.com/lichman0405/zeopp-backend/issues)
[![GitHub stars](https://img.shields.io/github/stars/lichman0405/zeopp-backend.svg?style=social)](https://github.com/lichman0405/zeopp-backend.git])

</div>

该项目解决了直接使用 Zeo++ 的一些痛点：它将复杂的命令行操作转变为简单的 API 调用，并提供自动缓存、结构化输出及易于部署的容器化环境。

## 🚀 核心功能

- ✅ **现代化的 API**：通过 HTTP 接口访问 Zeo++ 的核心分析功能
- 🧠 **智能缓存**：自动缓存计算结果，相同输入秒回（支持 `force_recalculate` 强制重算）
- 📂 **结构化输出**：返回易处理的 JSON 响应，数据类型清晰
- ⚙️ **配置灵活**：基于 Pydantic Settings 的类型安全配置
- 🐳 **Docker 就绪**：多阶段构建，自动处理 Zeo++ 下载与编译
- 🎨 **丰富的日志**：美观且信息丰富的控制台日志
- 🔒 **安全加固**：请求限流、文件验证、请求追踪
- 📊 **可观测性**：Prometheus 指标端点，请求性能监控
- 🧪 **测试覆盖**：完整的单元测试和集成测试套件
- 🤖 **MCP 双模式**：同时支持 **stdio**（推荐）和 Streamable HTTP 传输，可直接接入 featherflow / nanobot 类 Agent

## 📚 详细文档

为了更好地使用本服务，建议阅读以下详细文档：

- [**API 完整接口文档**](./docs/API_DOCUMENTATION.md)：所有端点的详细参数、请求/响应格式、cURL 示例
- [**API Documentation (English)**](./docs/API_DOCUMENTATION_EN.md)：Complete API reference in English
- [**Zeo++ 功能参考指南**](./docs/ZEO++_REFERENCE.md)：深入了解底层 Zeo++ 的所有命令、参数含义及物理背景
- [**API 映射手册**](./docs/API_MAPPING.md)：API 端点与 Zeo++ 命令的对应关系，以及推荐的参数配置
- [**MCP 集成指南**](./docs/MCP_INTEGRATION.md)：MCP 服务部署、鉴权、工具列表与 featherflow 接入配置
- [**使用示例**](./examples/)：Python 和 cURL 示例代码，包含示例结构文件

## ⚡ 快速上手

### 环境要求

- Docker 和 Docker Compose  
  或
- Python 3.10+ 和 [uv](https://docs.astral.sh/uv/)（推荐）
  或
- Python 3.10+ 和 pip

### 方式一：使用 Docker（推荐）

#### 创建配置文件

复制 `.env.example` 为 `.env` 文件，根据需要修改配置：

```bash
cp .env.example .env
```

Windows PowerShell 可使用：

```powershell
Copy-Item .env.example .env
```

常用配置项：

```ini
# .env

# 服务端口（外部访问端口）
HOST_PORT=9876
MCP_HOST_PORT=9877

# 应用配置
ENABLE_CACHE=true
LOG_LEVEL=INFO
CORS_ORIGINS=*
RATE_LIMIT_REQUESTS=100
MAX_UPLOAD_SIZE_MB=50

# 性能配置
UVICORN_WORKERS=2           # Worker 进程数，建议设为 CPU 核心数
MAX_CONCURRENT_TASKS=4      # 最大并发 Zeo++ 任务数

# MCP 配置
MCP_AUTH_TOKEN=             # 生产环境建议设置
MCP_STREAMABLE_HTTP_PATH=/mcp
MCP_ALLOWED_PATH_ROOTS=/app/workspace,/shared

# 资源限制
CPU_LIMIT=2
MEMORY_LIMIT=2G
```

> 💡 **提示**：所有配置项都在 `.env.example` 中有详细注释，无需修改 `docker-compose.yml`

#### 一键启动

在项目根目录运行：

```bash
docker-compose up --build -d
```

Docker 将自动构建镜像（含 Zeo++ 下载与编译），并启动服务。服务将运行在 `http://localhost:${HOST_PORT}`（默认 9876）。

### 方式二：本地开发（使用 uv，推荐）

[uv](https://docs.astral.sh/uv/) 是 Rust 编写的超快 Python 包管理器，一条命令搞定虚拟环境和依赖。

#### 安装 uv（如尚未安装）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 克隆项目并安装依赖

```bash
git clone https://github.com/lichman0405/zeopp-backend.git
cd zeopp-backend
uv sync
```

> `uv sync` 会自动创建 `.venv` 虚拟环境并安装所有依赖，无需手动 `python -m venv`。

#### 配置环境

创建 `.env` 文件，确保 `ZEO_EXEC_PATH` 指向您的 Zeo++ 可执行文件（或使用 stdio 模式自动编译安装）。

#### 运行 API 服务

```bash
uv run uvicorn app.main:app --reload
```

#### 运行 stdio MCP 服务

stdio 模式启动时会 **自动检测并编译安装 Zeo++**（需要 `gcc`, `g++`, `make`, `wget`/`curl`）：

```bash
uv run python -m app.mcp.stdio_main
```

### 方式三：本地开发（使用 pip）

#### 安装 Zeo++

请确保已根据官方指引安装 Zeo++，并能通过 `network` 命令在终端调用。

#### 安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### 配置环境

创建 `.env` 文件，确保 `ZEO_EXEC_PATH` 指向您的 Zeo++ 可执行文件。

#### 运行服务

```bash
uvicorn app.main:app --reload
```

## 📋 使用示例

项目启动后，可使用任何 HTTP 客户端调用 API。

### 测试健康检查

```bash
# 基本健康检查
curl http://localhost:9876/health

# 详细健康检查
curl http://localhost:9876/health/detailed

# 获取版本信息
curl http://localhost:9876/version
```

### 调用分析端点

示例：使用 curl 计算孔径

```bash
curl -X 'POST' \
  'http://localhost:9876/api/v1/pore_diameter' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'structure_file=@/path/to/your/file.cif' \
  -F 'ha=true'
```

请将 `/path/to/your/file.cif` 替换为本地结构文件路径。参数（如 `ha=true`）以表单字段 `-F` 形式发送。

### MCP（给 Agent 调用）

#### 方式 A：stdio 模式（推荐）

stdio MCP 直接以子进程方式运行，无需 Docker，首次启动自动编译安装 Zeo++。

**featherflow 接入配置**（`~/.featherflow/config.json`）：

```json
{
  "tools": {
    "mcpServers": {
      "zeopp": {
        "command": "uv",
        "args": ["run", "--project", "/path/to/zeopp-backend", "python", "-m", "app.mcp.stdio_main"],
        "toolTimeout": 300,
        "progressIntervalSeconds": 15
      }
    }
  }
}
```

> **配置说明**：
> - 将 `/path/to/zeopp-backend` 替换为项目实际路径
> - `toolTimeout`：单次工具调用超时秒数（Zeo++ 大结构计算可能较慢，建议 300–600）
> - `progressIntervalSeconds`：长时间运行时 featherflow 向用户发送心跳进度的间隔（默认 15s，0 = 关闭）
>
> **stdio 模式优势**：MCP 进程运行在宿主机上，`structure_path` 参数可直接传入本地文件路径（如 `/home/user/structures/MOF.cif`），无需使用 `structure_text` 传递文件内容。
>
> **首次启动 bootstrap 会自动**：
> 1. 检查 `gcc`, `g++`, `make`, `wget`/`curl` 是否可用
> 2. 检测 Zeo++ `network` 二进制是否已存在
> 3. 如不存在，自动下载源码、编译并安装到 `~/.local/bin/`
>
> 系统依赖安装（Ubuntu）：`sudo apt-get install -y build-essential wget curl`

<details>
<summary>其他 MCP 客户端（Cursor 等）配置格式</summary>

```json
{
  "mcpServers": {
    "zeopp": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/zeopp-backend", "python", "-m", "app.mcp.stdio_main"]
    }
  }
}
```

</details>

#### 方式 B：HTTP 模式（Docker）

启动 MCP 服务（Docker Compose 已内置 `zeopp-mcp`）：

```bash
docker-compose up -d zeopp-mcp
```

默认 MCP 地址：`http://localhost:9877/mcp`

featherflow 配置（`~/.featherflow/config.json`）：

```json
{
  "tools": {
    "mcpServers": {
      "zeopp": {
        "url": "http://localhost:9877/mcp",
        "headers": {
          "Authorization": "Bearer <MCP_AUTH_TOKEN>"
        },
        "toolTimeout": 300,
        "progressIntervalSeconds": 15
      }
    }
  }
}
```

> **注意**：HTTP 模式下 MCP 运行在 Docker 容器内，无法访问宿主机文件系统。调用工具时请使用 `structure_text`（传入文件内容）而非 `structure_path`。

#### stdio vs HTTP 模式对比

| 特性 | stdio（推荐） | HTTP（Docker） |
|------|-------------|---------------|
| 传输方式 | 子进程 stdin/stdout | HTTP 请求 |
| 部署 | 无需 Docker，uv 一键启动 | 需要 Docker |
| 文件访问 | ✅ 直接读取宿主机文件（`structure_path`） | ❌ 需传 `structure_text` 内容 |
| Zeo++ 安装 | 自动编译安装 | Docker 内自动编译 |
| featherflow 集成 | `command` + `args` | `url` + `headers` |
| 适用场景 | Agent 集成（featherflow 推荐） | 独立 HTTP 服务、多用户共享 |

### 交互式文档

访问 Swagger UI 进行交互式测试：[http://localhost:9876/docs](http://localhost:9876/docs)

## 📚 API 参考

### 系统端点

| 路径 | 功能 |
| --- | --- |
| `/` | 根端点，返回服务名、版本和文档入口 |
| `/health` | 基本健康检查，验证服务运行状态 |
| `/health/detailed` | 详细健康检查，包含系统信息和 Zeo++ 可用性 |
| `/version` | 获取 API 版本信息 |
| `/metrics` | Prometheus 指标端点（用于监控系统抓取） |
| `/api/v1/metrics/summary` | JSON 格式的指标摘要 |
| `/api/v1/cache/stats` | 缓存统计信息 |
| `/api/v1/cache/cleanup` | 清理过期临时文件 |
| `/api/v1/cache/clear` | 清除所有缓存 |
| `MCP 服务: /mcp` | Streamable HTTP MCP 端点（默认在 9877 端口） |
| `MCP stdio` | stdio 传输 MCP（通过 `python -m app.mcp.stdio_main` 启动） |

### 核心几何学分析（v1 API）

所有端点均需上传 `structure_file` 文件。

| 路径 | 功能 |
| --- | --- |
| `/api/v1/pore_diameter` → Zeo++ `-res` | 计算最大可及球（Di）和最大包含球（Df）直径 |
| `/api/v1/surface_area` → Zeo++ `-sa` | 使用蒙特卡洛采样计算可及表面积 |
| `/api/v1/accessible_volume` → Zeo++ `-vol` | 计算给定探针的可及体积 |
| `/api/v1/probe_volume` → Zeo++ `-volpo` | 计算特定点/区域的探针可占据体积 |
| `/api/v1/channel_analysis` → Zeo++ `-chan` | 识别和分析通道 |
| `/api/v1/pore_size_dist/download` → Zeo++ `-psd` | 下载孔径分布直方图的数据文件 |
| `/api/v1/blocking_spheres` → Zeo++ `-block` | 识别不可及区域并生成阻塞球 |

### 结构信息分析（v1 API）

| 路径 | 功能 |
| --- | --- |
| `/api/v1/framework_info` → Zeo++ `-strinfo` | 识别结构中框架数量及其维度 |
| `/api/v1/open_metal_sites` → Zeo++ `-oms` | 计算开放金属位点数量 |

## 🔄 版本说明

**当前版本：v0.3.2**

### 新增特性（v0.3.2）
- 🔌 **stdio MCP 传输**：新增 stdio 模式，与其他 MCP 服务统一交互方式
- 🛠️ **Zeo++ 自动编译安装**：首次启动自动检测系统依赖、下载并编译 Zeo++
- 📦 **uv 支持**：推荐使用 `uv` 管理虚拟环境和依赖，显著加速安装
- 🧩 **MCP 代码重构**：tools 与 transport 解耦，HTTP 和 stdio 共享同一份 tools 代码

### v0.3.1 特性
- 🔒 **安全增强**：请求限流（slowapi）、文件上传验证、请求 ID 追踪
- 📊 **Prometheus 监控**：`/metrics` 端点支持监控系统抓取
- 🗂️ **缓存管理 API**：查看统计、清理临时文件、清除缓存
- 🧪 **测试套件**：完整的 pytest 单元测试和 API 集成测试
- 🐳 **Docker 优化**：多阶段构建、非 root 用户、健康检查
- 📝 **完整文档**：Zeo++ 命令参考和 API 映射指南
- 🤖 **MCP 服务**：新增 Streamable HTTP MCP 入口与工具集成文档

### v0.3.0 特性
- ✅ API 版本控制：所有分析端点使用 `/api/v1/` 前缀
- ✅ 健康检查端点：`/health` 和 `/health/detailed`
- ✅ 改进的错误处理：自定义异常类型，详细错误信息

## 🧪 开发与测试

### 运行测试
```bash
# 使用 uv
uv sync --group dev
uv run pytest tests/ -v

# 或使用 pip
pip install -r requirements-dev.txt
pytest tests/ -v
```

### 开发模式运行
```bash
# 本地 API 服务
uv run uvicorn app.main:app --reload

# 本地 stdio MCP（自动编译安装 Zeo++）
uv run python -m app.mcp.stdio_main

# Docker 开发模式
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## 📜 许可证

MIT © Shibo Li, 2025
