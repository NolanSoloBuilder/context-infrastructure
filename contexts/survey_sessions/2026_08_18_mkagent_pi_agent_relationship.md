# MkAgent、Pi Agent 与 Craft Agents 的关系

日期：2026-08-18

## 结论

`mkagent.app` 写的是 **Pi-powered**。因此，这里的 `PAgent` 应该是指 **Pi Agent / Pi Agent Harness**。

它们的关系可以压缩成一句话：**Pi 是 Agent 引擎，MkAgent 是围绕这个引擎做出的完整本地工作台；MkAgent 的工作台骨架又主要源自 Craft Agents OSS。**

```text
模型服务 / 本地模型
OpenAI · Anthropic · Google · Ollama · 兼容 API
                    ↑
Pi AI + Pi Agent Core + Pi Coding Agent
模型适配 · agent loop · tool calling · session runtime
                    ↑
MkAgent 的 Pi subprocess 与权限包装
                    ↑
workspace · 持久会话 · Skills · 浏览器 · 文档工具
                    ↑
Desktop / WebUI / CLI
```

另一条来源关系是：

```text
Craft Agents OSS v0.11.2
        ↓ 选择性复用架构、UI 和大量代码
MkAgent：独立 Git 历史、独立品牌、缩小后的产品边界
```

所以，Pi 和 Craft Agents 对 MkAgent 的作用不同：**Pi 提供运行能力，Craft Agents 提供产品骨架。**

## Pi Agent 是干什么的

[Pi 官方仓库](https://github.com/earendil-works/pi)把自己定义为 Agent Harness，并分成三层：

| 组件 | 职责 |
|---|---|
| `pi-ai` | 对接 OpenAI、Anthropic、Google 等不同模型与传输协议 |
| `pi-agent-core` | 运行 agent loop、维护状态、处理 tool calling |
| `pi-coding-agent` | 提供可直接使用的 coding session、文件读写、Shell、搜索、会话恢复等能力 |

Pi 解决的是“怎样让模型持续执行任务”的问题。它负责把用户消息交给模型、接收工具调用、执行工具、把结果送回模型，再持续循环到任务完成。Pi 自己也可以作为 CLI coding agent 使用，或者作为 SDK 嵌进其他产品。

它不负责 MkAgent 那套完整桌面产品。Pi 官方 README 还明确写明，Pi 本身没有用于限制文件、进程、网络和凭据访问的内建权限系统；要么由宿主产品增加权限控制，要么放入容器或 sandbox。

## MkAgent 是干什么的

[MkAgent README](https://github.com/MkThingsHQ/mkagent)把产品定位为 local-first Agent workspace。它使用 `@earendil-works/pi-coding-agent` 创建真正执行任务的 session，再增加产品层能力：

- Electron Desktop、WebUI 和 CLI，共用同一个本地 server 与 workspace；
- 持久化 workspace、JSONL session、分支与恢复；
- OS Keychain / Credential Vault 保存模型凭据；
- `safe`、`allow-all` 和 plan workflow 的权限控制；
- 浏览器、Web 搜索与抓取、PDF/DOCX/XLSX/PPTX 等文档工具；
- Skills、计划、子 session、follow-up 与多窗口。

[MkAgent 架构文档](https://github.com/MkThingsHQ/mkagent/blob/main/docs/architecture.md)显示，只有 `pi` 一个 Agent backend 被注册。Claude、OpenAI、Google、Ollama 等属于 Pi 下方的模型连接；它们并不代表 MkAgent 同时运行多个独立 Agent 引擎。MkAgent 把 Pi 放在独立 Bun subprocess 中，通过 JSONL 与主进程通信，主进程再处理 workspace、RPC 和权限。

这意味着 MkAgent 比 Pi CLI 更适合以下场景：

- 想用 GUI 同时管理多个长期会话；
- 希望同一个 Agent 可从 Desktop、浏览器和 CLI 进入；
- 工作包含代码、网页和办公文档，而不只是终端编程；
- 想基于 Apache-2.0 代码继续做自己的桌面 Agent 产品。

## MkAgent 与 Craft Agents 的关系

MkAgent 的 GitHub 仓库不是 GitHub 平台上的 fork，也没有继承 Craft 的 commit ancestry，但代码来源关系很直接。[项目 README 的 lineage 声明](https://github.com/MkThingsHQ/mkagent#project-lineage)和 [`NOTICE`](https://github.com/MkThingsHQ/mkagent/blob/main/NOTICE)都写明：MkAgent 从 Craft Agents OSS `v0.11.2`、commit [`a60ebc1a5a7c`](https://github.com/craft-ai-agents/craft-agents-oss/commit/a60ebc1a5a7cb0a6af7a77d5eed0512c5fc07658) 的部分架构和代码起步，然后建立独立 Git 历史。

更准确的说法是：**MkAgent 是 Craft Agents 的独立轻量衍生版，保留它的 workspace/renderer/server/Pi 主干，再主动删除一批产品面。** [项目自己的对比审计](https://github.com/MkThingsHQ/mkagent/blob/main/docs/comparison-with-craft.md)列出的主要删减包括：

- Claude Agent SDK 第二后端；
- 通用 Sources 与 MCP 接入；
- Slack、Teams、Lark、WhatsApp 等消息网关；
- 公开分享、Viewer、远端 workspace；
- 产品自动化、scheduler、Projects/Kanban；
- 图片生成、标签和自定义状态。

因此，MkAgent 的优势是边界更小、Pi-only、代码更容易理解和改造；代价是外部系统集成、团队协作和自动化能力明显少于 Craft Agents。

## `local-first` 需要怎样理解

MkAgent 的 workspace、会话、设置和文件主要留在本机，这部分符合 local-first。**模型推理是否本地取决于你选择的模型连接。**

- 选择 ChatGPT、Claude 或其他云 API 时，prompt 和必要上下文仍会发送到对应 provider。
- 选择本地 Ollama 时，才可以把模型推理也留在本机。
- MkAgent 在 Pi 工具调用外层增加了权限引擎；Pi 本身没有这层 sandbox。

所以，“local-first”应理解成“本地拥有状态和工作区”，不能等同于“所有数据永不离开设备”。连接和凭据细节见 [MkAgent connections 文档](https://github.com/MkThingsHQ/mkagent/blob/main/docs/connections.md)，工具权限边界见 [permissions 文档](https://github.com/MkThingsHQ/mkagent/blob/main/docs/permissions.md)。

## 当前成熟度

截至 2026-08-18，MkAgent 仍处于非常早期：仓库创建于 2026-08-09，首个正式版 [`v0.1.0`](https://github.com/MkThingsHQ/mkagent/releases/tag/v0.1.0) 发布于 2026-08-10；GitHub API 当日计入 1 位 contributor、103 stars、27 forks 和 2 个 open items，两个 open items 都是维护者自己的 draft PR。Web 搜索没有找到独立第三方评测、生产迁移记录或长期使用报告。

还有三个实际信号：MkAgent 固定使用 Pi `0.80.6`，而 npm 当日最新版本为 `0.84.2`；`v0.1.0` 的 [release trust 文件](https://github.com/MkThingsHQ/mkagent/releases/download/v0.1.0/SIGNING_STATUS.txt)写明 macOS 仅 ad-hoc 签名、Windows 未签名，安装时可能遇到 Gatekeeper 或 SmartScreen 提示；27 个 forks 中只有少量发生后续提交，能找到的一个明确二开样本是 [`iBigQiang/OpcAgent`](https://github.com/iBigQiang/OpcAgent)，这能证明 rebrand 路径可行，还不能说明已经形成用户生态。

因此，我对它的判断是：

- **研究和二次开发价值较高**：架构边界清楚，Pi runtime、workspace shell 和权限层分开，Apache-2.0 也允许商业修改。
- **作为日常主力工具仍需真实试用**：功能面已经不小，但项目历史、维护者数量、签名和独立使用证据都不足。
- **如果你关注的是“做自己的 Agent 产品”**，MkAgent 比直接从 Pi 开始更接近成品；如果只想要一个轻量、可扩展的终端 Agent，直接使用 Pi 更合理；如果需要大量 SaaS/MCP、消息渠道、远程协作和自动化，Craft Agents 更接近目标。

## 证据边界

本轮完成了官网、GitHub API、npm metadata、README、架构/权限/连接文档和关键源码 import 的交叉核对，没有安装运行 MkAgent。项目宣称的完整测试通过率、源码复用比例和安装包体积对比来自 MkAgent 自己的审计文档，本轮没有重新构建两个仓库验证，因此没有把这些数字作为核心结论。
