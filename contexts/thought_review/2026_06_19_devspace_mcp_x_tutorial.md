# DevSpace MCP 从零调通教程

用途：这份文档用于拆成 X thread 发布。正文按「主帖」和「评论」分段，每段都控制在适合社交媒体阅读的长度内。不要包含 owner password、access token、Cloudflare token 或本机私密路径。

## 主帖

我这两天把 DevSpace 跑通了：本机起 DevSpace MCP server，用 Cloudflare tunnel 和自己的域名做 HTTPS 入口，再让 ChatGPT 通过 MCP 连接到本机项目目录，能 `open_workspace`、`read`，也可以按权限开放 `write`、`edit`、`bash`。

这套方案的关键点不是装一个 npm 包，而是把三层链路都验证清楚：

1. 本地 DevSpace server 正常
2. 公网 HTTPS endpoint 正常
3. MCP client 真的通过协议调用工具

下面是完整从零流程。

## 评论 1：DevSpace 是什么

DevSpace 是一个本地 MCP server。

它把你的本机项目目录暴露成一组 MCP tools：

- `open_workspace`
- `read`
- `write`
- `edit`
- `bash`

ChatGPT 或其他 MCP client 连上之后，可以像 coding agent 一样打开项目、读文件、改文件、跑命令。

这类工具要认真处理安全边界。尤其是 `bash`，本质上就是让远端 client 有能力在你的机器上执行命令。

## 评论 2：安装依赖

需要 Node.js 和一个公网 HTTPS 入口。我这里用的是 Cloudflare tunnel。

安装 DevSpace：

```bash
npm install -g @waishnav/devspace
```

安装 Cloudflare tunnel：

```bash
npm install -g cloudflared
```

然后确认命令可用：

```bash
devspace doctor
cloudflared --version
```

如果 `devspace doctor` 提示缺 OAuth owner token，先跑初始化。

## 评论 3：初始化 DevSpace

初始化：

```bash
devspace init
```

它会生成两个关键文件：

```text
~/.devspace/config.json
~/.devspace/auth.json
```

`auth.json` 里有 owner password。这个密码用于 MCP client 首次授权，不要发给别人，也不要写进公开文档。

配置里至少要确认：

```text
allowedRoots: 只包含你准备给 AI 访问的项目目录
publicBaseUrl: 你的公网 HTTPS base URL
```

## 评论 4：本地启动

本地跑起来：

```bash
devspace serve
```

默认 MCP endpoint 是：

```text
http://127.0.0.1:7676/mcp
```

健康检查：

```bash
curl http://127.0.0.1:7676/healthz
```

这一步只证明本地服务可用，还没有证明公网和 MCP 协议都通。

## 评论 5：临时 tunnel 快速验证

最快的公网验证方式是 Cloudflare quick tunnel：

```bash
cloudflared tunnel --url http://127.0.0.1:7676
```

它会给一个临时域名，例如：

```text
https://example.trycloudflare.com
```

把 DevSpace 的 public URL 临时设成这个域名：

```bash
devspace config set publicBaseUrl https://example.trycloudflare.com
```

最终 MCP URL 是：

```text
https://example.trycloudflare.com/mcp
```

## 评论 6：长期域名方案

临时域名适合 smoke test，不适合长期使用。

长期方案建议：

- 买一个自己的域名
- 用 Cloudflare 托管 DNS
- 创建 named tunnel
- 把 `devspace.your-domain.com` 指到本机 DevSpace
- 后续再加 Cloudflare Access 或其他身份边界

这里的判断很简单：shell-capable MCP endpoint 不应该裸奔在随机公网地址上。

## 评论 7：ChatGPT 连接方式

在 ChatGPT 或支持 MCP 的 client 里填：

```text
https://devspace.your-domain.com/mcp
```

第一次连接会打开 DevSpace 授权页，让你输入 owner password。

授权成功后，client 会走 OAuth token，再通过 MCP Streamable HTTP 访问 `/mcp`。

注意：浏览器 UI 只是产品入口。真正的 MCP 调用发生在 client 和 DevSpace server 之间。

## 评论 8：不要只看 UI，要看协议证据

我踩过一个坑：ChatGPT UI 里的 app chip 有时会显示「点击以重试」，但工具调用其实已经成功。

更可靠的证据是两个：

1. ChatGPT 里的 tool call card，例如 `Workspace ...`、`Read File ...`
2. DevSpace server log 里的 `tool_call`

例如：

```text
tool_call open_workspace ... success:true
tool_call read ... success:true
```

## 评论 9：协议层 smoke test

如果你想排除 UI 干扰，直接写一个 MCP client 测协议层。

完整链路是：

1. 读取 OAuth metadata
2. 动态注册 client
3. 用 owner password 走 authorize
4. 用 authorization code 换 access token
5. `initialize`
6. `tools/list`
7. `open_workspace`
8. `read`

看到 marker 文件内容，才算真的调通。

## 评论 10：最小验证任务

推荐准备一个只读 marker 文件：

```text
adhoc_jobs/devspace_live_gpt_link_test/task_input.md
```

里面放一个唯一 marker：

```text
DEVSPACE_LIVE_GPT_LINK_2026_06_19_1703
```

然后让 MCP client 通过 DevSpace 读取这个文件。

如果结果里返回这个 marker，同时 server log 出现 `tool_call read`，说明链路成立。

## 评论 11：安全建议

上线前至少做这几件事：

- `allowedRoots` 只放必要项目目录
- owner password 不进 repo、不进截图、不进 X
- `bash` 只给可信 client
- DevSpace endpoint 走 HTTPS
- 长期域名优先加 Access 或等价保护
- 先用只读任务验证，再开放写和 shell

MCP 很强，但它不是普通网页 API。它连的是你的本机工作环境。

## 评论 12：最终可用状态

我这边最终验证到的状态是：

```text
endpoint: https://devspace.forgepane.com/mcp
tools: open_workspace, read, write, edit, bash
open_workspace: success
read marker file: success
```

这说明 DevSpace MCP 长期域名链路已经可用。

下一步不是继续证明它能连，而是把安全边界、只读模式、Access、日志和操作习惯固化下来。

## 附：复盘

这次最大的经验是把验证分层：

- 本地 `/healthz` 证明服务活着
- 公网 `/healthz` 证明 tunnel/DNS/HTTPS 通
- OAuth flow 证明授权通
- `tools/list` 证明 MCP capability 暴露成功
- `open_workspace/read` 证明工具真的执行
- server log 证明调用路径可信

只看到 UI 上有 app，不等于 MCP 成功。只看到 `/healthz` 成功，也不等于工具调用成功。
