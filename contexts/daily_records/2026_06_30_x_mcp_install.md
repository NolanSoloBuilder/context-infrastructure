# 2026-06-30 X MCP 安装记录

来源：[X MCP Servers](https://docs.x.com/tools/mcp)

## 本机状态

- 已将 `@xdevplatform/xurl` 安装到全局 node 环境，当前版本：`1.2.2`
- `/opt/homebrew/bin/xurl` 当前指向 npm global 安装：`../lib/node_modules/@xdevplatform/xurl/cli.js`
- 旧的 Homebrew cask `xurl 1.0.3` 缺少 `mcp` 子命令，因此由 npm global 版本覆盖入口 symlink

## 已启用

- Codex：`~/.codex/config.toml` 已添加 `x-docs`
- OpenCode：`~/.config/opencode/opencode.json` 已添加 `x-docs`
- MCP endpoint：`https://docs.x.com/mcp`

协议级 smoke test：

```text
initialize: HTTP 200, serverInfo.name = X, version = 1.0.0, protocolVersion = 2025-06-18
tools/list: HTTP 200, tools = search_x, query_docs_filesystem_x
```

## 待配置

`xapi` 指向 `https://api.x.com/mcp`，需要 X Developer app 的 OAuth 2.0 `CLIENT_ID` 和 `CLIENT_SECRET`。官方要求在 app 中注册 redirect URI：

```text
http://localhost:8080/callback
```

等凭据就绪后，可以把 `xapi` 加到 Codex / OpenCode：

```toml
[mcp_servers.xapi]
command = "/opt/homebrew/bin/xurl"
args = ["mcp", "https://api.x.com/mcp"]
enabled = true
startup_timeout_sec = 300

[mcp_servers.xapi.env]
CLIENT_ID = "..."
CLIENT_SECRET = "..."
```
