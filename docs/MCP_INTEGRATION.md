# Zeo++ MCP 集成指南

本文说明如何把 `zeopp-backend` 作为 MCP 工具服务接入 Agent（尤其是 featherflow）。

## 1. 架构与端口

- HTTP API 服务：`zeopp-api`（默认 `9876`）
- MCP 服务：`zeopp-mcp`（默认 `9877`）
- MCP 传输协议：**Streamable HTTP**
- MCP 端点路径：`/mcp`（可通过 `MCP_STREAMABLE_HTTP_PATH` 修改）

默认完整地址：

```text
http://localhost:9877/mcp
```

## 2. 启动 MCP 服务

```bash
docker-compose up -d zeopp-mcp
```

若需要 API + MCP 一起跑：

```bash
docker-compose up -d zeopp-api zeopp-mcp
```

## 3. MCP 关键配置（.env）

```ini
MCP_HOST_PORT=9877
MCP_AUTH_TOKEN=
MCP_STREAMABLE_HTTP_PATH=/mcp
MCP_ALLOWED_PATH_ROOTS=/app/workspace,/shared
MCP_MAX_RESULT_CHARS=12000
```

- `MCP_AUTH_TOKEN` 为空时不鉴权；生产环境建议必须设置。
- `MCP_ALLOWED_PATH_ROOTS` 只控制 `structure_path` 读取范围，不影响 `structure_text` / `structure_base64`。

## 4. 输入方式（所有分析工具通用）

每次调用必须且只能提供一种结构输入：

- `structure_path`：服务端文件路径（需位于 `MCP_ALLOWED_PATH_ROOTS`）
- `structure_text`：结构文本内容（如 CIF 文本）
- `structure_base64`：结构文件的 base64 字符串

可选：

- `filename`：当使用 `structure_text` / `structure_base64` 时建议传入，带有效后缀（如 `.cif`）

支持后缀与 HTTP API 一致：`.cif`, `.cssr`, `.v1`, `.arc`, `.xyz`, `.pdb`, `.cuc`。

## 5. 工具列表

系统工具：

- `health`
- `version`
- `cache_stats`
- `cache_cleanup`
- `cache_clear`

分析工具：

- `pore_diameter`
- `surface_area`
- `accessible_volume`
- `probe_volume`
- `channel_analysis`
- `framework_info`
- `open_metal_sites`
- `blocking_spheres`
- `pore_size_dist_summary`

说明：

- 参数语义与现有 HTTP API 对齐（`ha`, `force_recalculate`, `samples`, `probe_radius`, `chan_radius` 等）。
- 工具返回统一 JSON 结构（`ok`, `tool`, `timestamp`, `result`, `cached`, `meta`）。

## 6. featherflow 对接示例

在 `~/.featherflow/config.json` 配置：

```json
{
  "tools": {
    "mcpServers": {
      "zeopp": {
        "url": "http://localhost:9877/mcp",
        "headers": {
          "Authorization": "Bearer <MCP_AUTH_TOKEN>"
        },
        "toolTimeout": 120
      }
    }
  }
}
```

注意：

- featherflow 使用 `mcpServers`（或 `mcp_servers`）字段。
- `tools.mcp` 字段不会被读取。

## 7. 与 featherflow 容器共享结构文件（可选）

如果希望 Agent 用 `structure_path` 直接引用文件，建议把同一个卷挂到两个服务（示例）：

```yaml
services:
  featherflow:
    volumes:
      - zeopp-shared:/shared
  zeopp-mcp:
    volumes:
      - zeopp-shared:/shared
volumes:
  zeopp-shared:
    external: true
```

然后在工具参数中使用 `/shared/...` 路径。

## 8. 安全建议

- 生产环境开启 `MCP_AUTH_TOKEN`。
- 将 `MCP_ALLOWED_PATH_ROOTS` 收紧到最小目录集合。
- 对外暴露时建议经由反向代理并限制来源网段。

## 9. 常见问题

1. `401 Unauthorized`
- 未传 `Authorization: Bearer <token>`，或 token 不匹配。

2. `structure_path is outside MCP_ALLOWED_PATH_ROOTS`
- 路径不在白名单根目录内，调整 `MCP_ALLOWED_PATH_ROOTS` 或改用 `structure_text/base64`。

3. 返回内容被截断
- 调大 `MCP_MAX_RESULT_CHARS`。
