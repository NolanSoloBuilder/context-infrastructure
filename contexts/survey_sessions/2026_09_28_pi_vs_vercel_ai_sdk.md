# Pi 与 Vercel AI SDK Agent 的区别

核验日期：2026-09-28。用户明确比较 Vercel AI SDK 开发框架，不是 Vercel Agent 代码审查与运维产品。

## 结论

Pi 更强调围绕工作目录持续工作的 Agent 会话，提供工具、上下文压缩、会话恢复与分支、扩展及 CLI/SDK 接入。Vercel AI SDK 更强调在 TypeScript 应用里组合模型、工具循环、结构化结果和流式交互。

这个区别主要适用于 Pi 完整 SDK 与 AI SDK 的 `ToolLoopAgent`。当前 AI SDK 同时有 `HarnessAgent`，可以直接接入 Pi，因此两者既能作为不同开发起点，也能组合使用。

## 能力对照

| 维度 | Pi 完整 SDK / Harness | AI SDK `ToolLoopAgent` |
| --- | --- | --- |
| 开发入口 | `createAgentSession()`，创建有工作目录、模型、工具和上下文的会话 | `new ToolLoopAgent()`，定义可复用的模型、指令与工具配置 |
| 模型与工具循环 | 提供模型调用、工具执行、事件与运行状态控制 | 提供多步工具循环、`stopWhen`、`prepareStep`、生命周期回调 |
| 默认工具 | 工作目录中的文件读取、编辑、写入、命令执行等能力，可定制工具集 | 应用定义或接入业务工具；工具执行环境由应用配置 |
| 会话历史 | SDK 默认持久化；`SessionManager` 管理记录树、活动分支及恢复 | 一次调用使用传入的消息；跨请求存取消息由应用实现 |
| 长上下文 | 会话整合压缩状态与自动恢复行为 | 可在 `prepareStep` 中调整消息，配合 `pruneMessages` 或自定义压缩 |
| 运行中交互 | 会话直接提供 `steer()`、`followUp()`、`abort()` 与事件订阅 | 提供调用生命周期、取消、工具审批；持续会话交互由应用编排 |
| 产品接入 | CLI、JSON、RPC、TypeScript SDK；适合围绕完整执行会话构建产品 | 模型接口、结构化输出、`useChat` 和流式 UI 集成较完整 |

依据：[Pi SDK](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sdk.md)、[AI SDK Building Agents](https://ai-sdk.dev/docs/agents/building-agents)、[Loop Control](https://ai-sdk.dev/docs/agents/loop-control)、[消息持久化](https://ai-sdk.dev/docs/ai-sdk-ui/chatbot-message-persistence)。

这些是默认抽象和现成能力的差别，不构成“Pi 只能做编程”“AI SDK 只能做聊天或 Web”的限制。Pi 官方列出研究、写作、数据文件等用途；AI SDK 也有 Terminal UI。两者都不能仅凭 SDK 名称比较智能水平，效果仍取决于模型、工具、上下文与任务评测。

## 当前已经可以组合

AI SDK 官方提供实验性的 `@ai-sdk/harness-pi`，通过 `HarnessAgent` 使用 `@earendil-works/pi-coding-agent`：

```text
应用 / AI SDK UI
       ↓
HarnessAgent + @ai-sdk/harness-pi
       ↓
Pi 会话、上下文与执行循环
       ↓
模型 + 工具 / 执行环境
```

Pi 适配器在宿主 Node.js 进程运行，用 sandbox 执行文件与 shell 操作。官方列出 Vercel sandbox 和本地 just-bash 接入路径。接入现有 Pi 时，应理解适配器边界：默认关闭文件系统扩展发现、主题和 prompt templates，可显式传入可信 inline extensions；当前 Pi 适配器不支持 `HarnessAgent` 的 `output` 结构化输出选项。Harness 包仍标为 experimental，API 可能变化。

依据：[Pi Harness](https://ai-sdk.dev/providers/ai-sdk-harnesses/pi)、[HarnessAgent](https://ai-sdk.dev/docs/ai-sdk-harnesses/harness-agent)。

## 持久化与执行边界

会话历史可恢复，不自动等于任意工具副作用可以安全重试。AI SDK 的普通 `ToolLoopAgent` 在内存运行；官方另提供 `WorkflowAgent`，结合 Workflow 实现跨进程持久执行，文档当前要求 Workflow 5 beta。应分别评估会话记录、流重连、任务恢复及外部写入幂等性。

Pi 原生工具及扩展使用 Pi 进程权限。项目资源信任控制并不隔离工具执行。部署为多人产品时，身份、业务授权、数据隔离、执行环境和审计仍需在宿主产品落实。

依据：[WorkflowAgent](https://ai-sdk.dev/docs/agents/workflow-agent)、[Pi Security](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/security.md)。

## 选型判断

- 给现有 SaaS 加业务 Agent，例如查订单、搜索知识、分析数据并输出结构化结果：优先评估 `ToolLoopAgent`，直接复用业务 API 和前端接口。
- 做围绕工作目录的执行型助手，例如文件研究、修改工程、持续任务与会话分支：优先评估 Pi SDK，减少自行实现会话设施的工作。
- 同时需要 Pi 执行能力与 AI SDK 应用接口：评估 `HarnessAgent + Pi`，重点验证实验性接口稳定性和适配器限制。

### 拼构 / BeamJoin 的具体判断

按 2026-09-28 的当前 checkout，拼构应继续以 AI SDK `ToolLoopAgent` 作为内置设计助手，暂不迁移到 Pi。`apps/api/src/modules/agent/routes.ts` 已经将 `design_read`、`catalog_search`、`design_preview`、`design_amend` 四项领域工具接入 `ToolLoopAgent`，用 `isStepCount(12)` 限定在线运行；提案、消息和步骤由自身 PostgreSQL 服务持久化。`apps/web/src/agent/AgentPanel.tsx` 使用 `useChat` 展示流式回复和提案。外部 Agent 则通过 `apps/api/src/mcp/` 的 MCP 工具操作同一个设计服务。

拼构的关键合同是模型只能读设计与目录、提出和修正候选；服务端领域内核生成差异、BOM 和诊断，用户审阅后由独立提交路径写入修订。Pi 默认文件和 shell 工具及其会话格式不替代这个合同，引入完整 Pi 会增加会话状态映射、工具权限和执行环境的集成工作。目前需要优先补齐的是多用户身份与授权、候选目标和修订冲突处理、真实模型与图片/多轮质量验收，以及后续后台运行需求的边界；这些不是替换 Agent 循环包即可获得的能力。

如果未来要做一个能长期运行、跨项目搜索资料并操作多种外部工具的独立工作者，再单独评估 Pi 或 `HarnessAgent + Pi`。仍应只通过拼构受限的领域工具提交设计候选，而不是让文件、shell 或数据库操作直接改设计事实。长任务的中断续跑需单独评估持久工作流；选择 Pi 本身也不等于工具副作用具备幂等重试。

代码与约束：[拼构当前架构](/Users/xuhao/Documents/Other/agent-native-aluminum-platform/docs/architecture_current.md)、[Agent 器材操作接口](/Users/xuhao/Documents/Other/agent-native-aluminum-platform/docs/agent_interface.md)、[内置 Agent 路由](/Users/xuhao/Documents/Other/agent-native-aluminum-platform/apps/api/src/modules/agent/routes.ts)、[Web Agent 面板](/Users/xuhao/Documents/Other/agent-native-aluminum-platform/apps/web/src/agent/AgentPanel.tsx)。

以上为基于能力边界的工程判断，未做性能或任务完成率对照实验，也未改变现有项目依赖。

## 核验记录

- 查阅当前官方在线 Markdown 文档和 Pi 官方仓库 `main` 文档。
- 本机全局 `ai` 为 `7.0.107`，读取了其 `ToolLoopAgent` 源码及 Agent、消息持久化文档；npm 查询当日 `ai` latest 为 `7.0.118`，`@ai-sdk/harness-pi` latest 为 `1.0.130`。这些版本是当日快照。
- 在线搜索存在较旧的 AI SDK 6 文档摘要；涉及当前 API 时以实时文档和本地 7.x 源码为准。
- Pi 内部包边界正在演进，本文以完整 SDK 的公开合同为比较依据，不将早期 `pi-ai → pi-agent-core → pi-coding-agent` 的层次描述当成当前完整实现图。
