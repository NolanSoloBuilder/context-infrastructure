# MkAgent / Pi Agent 关系调研 Scratchpad

日期：2026-08-18

## 名称消歧

- `mkagent.app` 官网使用的是 `Pi-powered`，没有把其核心运行时称为 `PAgent`。
- 本报告按“Pi Agent 与 MkAgent 的关系”理解用户问题。
- 搜索结果中的 `PAGENT: Learning to Patch Software Engineering Agents`、`pagent.ai`、PurpleMaze Pagent 等均为同名无关项目。

## Claim Extraction

| Claim | 来源层级 | 验证通道 | 验证结果 |
|---|---|---|---|
| MkAgent 是 Pi 驱动的 local-first Agent workspace | Tier 1 官网/README | `package.json`、`packages/pi-agent-server` 源码 | 已验证：固定依赖 `@earendil-works/pi-* 0.80.6`，直接调用 `createAgentSession` |
| MkAgent 可通过 Desktop、WebUI、CLI 使用同一运行时 | Tier 1 README/架构文档 | monorepo 路径与 RPC 架构 | 已验证：三个客户端共用 server-core、workspace 与 session |
| MkAgent 源自 Craft Agents OSS | Tier 1 README/NOTICE | NOTICE、同步文档、文件复用审计、GitHub API | 已验证：以 Craft Agents v0.11.2 / `a60ebc1a5a7c` 为基线，但使用独立 Git 历史 |
| MkAgent 是 local-first | Tier 1 官网 | 存储与 connection 文档 | 有条件成立：应用状态在本地；使用云模型时 prompt 仍发送给所选 provider，只有 Ollama 可本地推理 |
| MkAgent 提供权限保护 | Tier 1 权限文档 | Pi 官方权限说明与 MkAgent permission hook 源码 | 已验证：Pi 本身没有内建权限沙箱，MkAgent 在工具调用外层增加 `safe` / `allow-all` / plan workflow 权限管线 |

## 关键事实

1. Pi 是底层 Agent Harness：`pi-ai` 统一模型 API，`pi-agent-core` 负责 agent loop、工具调用和状态，`pi-coding-agent` 提供 session API 与文件/终端工具。
2. MkAgent 是产品层：在 Pi 外增加 Electron/WebUI/CLI、workspace、JSONL session、凭据、权限、浏览器、文档和 session tools。
3. Craft Agents 是 MkAgent 的产品骨架来源；Pi 是 MkAgent 的运行引擎来源。两条关系不能混为一谈。
4. MkAgent 当前只注册 `pi` backend；Claude、OpenAI、Ollama 等是 Pi 下面的模型连接，不是多个 Agent backend。
5. MkAgent 删去了 Craft Agents 的 Claude Agent SDK backend、Sources/MCP、消息网关、公开分享、远端 workspace、产品自动化、项目/Kanban 和图片生成等能力。
6. 截至 2026-08-18，MkAgent 仓库创建于 2026-08-09，最新正式版为 2026-08-10 的 `v0.1.0`；GitHub API 显示单一 API-listed contributor、103 stars、27 forks、2 个 open items，后两者实际都是维护者自己的 draft PR。没有搜到独立评测或生产迁移案例。
7. `v0.1.0` release 的 `SIGNING_STATUS.txt` 写明：macOS 为 ad-hoc 签名，Windows 未签名；安装时可能出现 Gatekeeper / SmartScreen 警告。
8. MkAgent 固定 Pi `0.80.6`，而 2026-08-18 查询到 npm 最新为 `0.84.2`，说明它没有紧跟 Pi 当前版本。
9. 27 个 forks 中只有少量发生后续提交；`iBigQiang/OpcAgent` 是一个实际 rebrand/二开样本，可证明 MkAgent 的二次开发路径有人走通，但不能证明广泛采用。

## 主要来源

- https://mkagent.app/
- https://github.com/MkThingsHQ/mkagent
- https://github.com/MkThingsHQ/mkagent/blob/main/docs/architecture.md
- https://github.com/MkThingsHQ/mkagent/blob/main/docs/comparison-with-craft.md
- https://github.com/MkThingsHQ/mkagent/blob/main/docs/permissions.md
- https://github.com/MkThingsHQ/mkagent/blob/main/docs/connections.md
- https://github.com/MkThingsHQ/mkagent/blob/main/NOTICE
- https://github.com/earendil-works/pi
- https://github.com/craft-ai-agents/craft-agents-oss
- https://github.com/MkThingsHQ/mkagent/releases/tag/v0.1.0
