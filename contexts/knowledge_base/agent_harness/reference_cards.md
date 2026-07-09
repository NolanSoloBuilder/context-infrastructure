# Agent Harness Reference Cards

日期：2026-07-06

这些卡片来自 `contexts/survey_sessions/2026_07_06_agent_harness_reference_materials.md` 的资料筛选。每张卡片只保存理解后的索引，不保存外部原文。

## 资料选择标准

资料必须能回答至少一个 Harness 层问题：

- Agent loop 如何运行，何时继续，何时停止
- 工具如何定义、注册、执行、截断和返回错误
- 状态如何持久化，长任务如何 pause / resume
- 权限、guardrails、human review、sandbox 如何介入
- 记忆和上下文如何注入、检索和更新
- 观测、trace、evaluation、repair loop 如何形成闭环

## 卡片

### Anthropic: Effective harnesses for long-running agents

- URL: https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents
- 类型：工程文章 + quickstart
- 入库等级：A
- 核心问题：单个 agent 跨多个 context window 做长任务时，为什么 compaction 不够，Harness 还要做什么。
- Harness 贡献：提出 initializer agent / coding agent 两段式结构。initializer 负责初始环境、任务分解和交接材料；coding agent 每个 session 只做增量推进，并留下 artifact，让下一轮不需要重新猜测状态。
- 可复用原语：`initializer_agent`、`progress_artifact`、`clean_state`、`session_handoff`、`incremental_progress`
- 适用场景：Workspace Harness、长任务 coding agent、跨会话任务续跑、context checkpoint 设计。
- 对应 OpenBook：Chapter 5（上下文窗口管理）、Chapter 14（任务系统）、Chapter 21（Dream）、Part IX（OpenHarness）。
- 使用提醒：这篇文章解决的是长任务工程组织，不是通用多 Agent 架构理论。不要把 initializer / coding agent 机械套到所有任务。

### Anthropic: Building effective agents

- URL: https://www.anthropic.com/engineering/building-effective-agents
- 类型：工程原则文章
- 入库等级：A
- 核心问题：什么时候该用 workflow，什么时候该用 agent，什么时候不该增加 agentic complexity。
- Harness 贡献：把 Agent-Computer Interface 放到核心位置。工具不是函数列表，而是模型和计算机之间的交互协议；工具文档、工具结果、错误语义和测试都会影响模型行为。
- 可复用原语：`agent_computer_interface`、`workflow_vs_agent`、`tool_documentation`、`transparent_planning`
- 适用场景：决定是否上 agent、设计工具返回、控制系统复杂度、做 agent 产品方案审查。
- 对应 OpenBook：Chapter 1-2（Harness 心智模型）、Chapter 6-8（工具系统）、Chapter 22（设计哲学）。
- 使用提醒：它更强调少做复杂系统。遇到“能不能多加几个 agent”这类方案时，先用这篇文章压一遍复杂度必要性。

### OpenAI Agents SDK

- URL: https://openai.github.io/openai-agents-python/
- URL: https://developers.openai.com/api/docs/guides/agents
- 类型：官方 SDK / 平台文档
- 入库等级：A
- 核心问题：一个可落地 Agent SDK 的最小 primitives 应该包含什么。
- Harness 贡献：把 Agent、tools、handoffs / agents-as-tools、guardrails、tracing、state、sandbox、human review 放到同一运行时表面。它适合作为我们自研 Harness 的功能 checklist。
- 可复用原语：`agent_definition`、`tool_invocation_loop`、`handoff_ownership`、`guardrail`、`run_state`、`trace`
- 适用场景：设计 SDK surface、工具调用循环、多 agent ownership、输入输出验证、human review、sandbox 执行。
- 对应 OpenBook：Chapter 3-4（Agent Loop / API 调用）、Chapter 6-8（工具系统）、Chapter 9-11（权限）、Chapter 12-15（多 Agent）。
- 使用提醒：OpenAI SDK 是具体平台形态。概念可复用，但不要假设它的 API shape 适合所有 runtime。

### LangGraph

- URL: https://docs.langchain.com/oss/python/langgraph/overview
- 类型：orchestration runtime 文档
- 入库等级：A
- 核心问题：长运行、可恢复、可人工介入的 stateful agent runtime 应该有哪些底层能力。
- Harness 贡献：把 durable execution、streaming、human-in-the-loop、persistence、memory 明确成 runtime 能力。它还区分 harness、framework、runtime、observability platform，适合澄清系统分层。
- 可复用原语：`state_graph`、`durable_execution`、`checkpoint`、`human_interrupt`、`persistence`
- 适用场景：设计 checkpoint、resume、可视化状态机、人类介入点、长流程任务。
- 对应 OpenBook：Chapter 3-5（Agent Loop / context）、Chapter 14（任务系统）、Chapter 17（记忆）、Part IX（部署）。
- 使用提醒：LangGraph 解决 runtime 编排，不自动解决工具安全、权限模型和产品治理。

### HumanLayer: 12-Factor Agents

- URL: https://github.com/humanlayer/12-factor-agents
- 类型：生产实践原则
- 入库等级：A
- 核心问题：怎样把 LLM-powered software 当普通软件工程系统来设计。
- Harness 贡献：把 context window、prompt ownership、control flow、pause/resume、tool calls、execution state、error compaction、small focused agents 变成工程约束。它适合做生产 readiness 审查。
- 可复用原语：`own_context_window`、`own_control_flow`、`pause_resume_api`、`execution_state`、`error_compaction`、`stateless_reducer`
- 适用场景：评审 Agent 系统架构、检查状态归属、设计 human escalation、规划错误恢复。
- 对应 OpenBook：Chapter 5（上下文窗口管理）、Chapter 8（工具编排）、Chapter 14（任务系统）、Chapter 22（设计原则）。
- 使用提醒：这是原则集合，不是框架。要转成当前项目 checklist 才能执行。

### Model Context Protocol

- URL: https://modelcontextprotocol.io/docs/getting-started/intro
- URL: https://modelcontextprotocol.io/specification/2025-06-18/server/tools
- 类型：开放协议规范
- 入库等级：A
- 核心问题：Harness 如何以标准方式连接外部数据源、工具、workflow 和 prompt。
- Harness 贡献：把外部能力抽象为 server / client / tools / resources / prompts。Tools 需要名称、metadata 和 schema，模型可以根据上下文选择调用。
- 可复用原语：`external_capability_protocol`、`tool_schema`、`resource`、`prompt_template`、`client_server_boundary`
- 适用场景：设计工具扩展层、接入第三方 API、统一本地/远端工具、区分 MCP / Skills / Plugins。
- 对应 OpenBook：Chapter 18（MCP）、Chapter 19（Skills）、Chapter 20（Commands / Plugin）。
- 使用提醒：MCP 是连接协议，不负责 agent loop、权限策略、业务验证和任务状态。Harness 不能把这些责任推给 MCP。

### Strands Agents SDK

- URL: https://strandsagents.com/
- URL: https://strandsagents.com/docs/user-guide/concepts/tools/
- URL: https://strandsagents.com/docs/user-guide/concepts/agents/hooks/
- URL: https://aws.amazon.com/blogs/machine-learning/strands-agents-sdk-a-technical-deep-dive-into-agent-architectures-and-observability/
- 类型：SDK + AWS 生态文档
- 入库等级：B
- 核心问题：一个企业化 Agent SDK 如何暴露 hooks、tools、observability、MCP、sandbox 和多 agent pattern。
- Harness 贡献：Hooks 文档很有价值。它把 agent lifecycle event 变成可订阅、可修改、可取消、可 retry、可 resume 的工程接口。Observability 文档把 trajectory、model call、tool call 接到 OpenTelemetry 生态。
- 可复用原语：`lifecycle_hook`、`before_tool_call`、`after_tool_call`、`retry`、`resume`、`trajectory_trace`、`otel`
- 适用场景：设计 Hook 系统、tool interception、approval / intervention、observability、AWS 部署。
- 对应 OpenBook：Chapter 8（工具编排）、Chapter 11（Hooks）、Chapter 22（可观测性）、Part IX（云上部署）。
- 使用提醒：Strands 的“model-driven”路线降低上手门槛，但核心治理仍要靠 hooks、sandbox、trace 和 guardrails。

### Amazon Bedrock Agents

- URL: https://docs.aws.amazon.com/bedrock/latest/userguide/agents-how.html
- 类型：托管平台文档
- 入库等级：B
- 核心问题：托管式 Agent 平台如何组织 build-time 组件和 runtime orchestration。
- Harness 贡献：清楚展示 build-time instructions、action groups、knowledge bases、security configurations、prompt templates 如何被打包成 agent；runtime 则是 preprocessing、orchestration、post-processing，orchestration loop 在 action group 和 knowledge base 之间循环，并记录 trace。
- 可复用原语：`action_group`、`knowledge_base`、`prompt_store`、`orchestration_trace`、`preprocessing`、`observation`
- 适用场景：设计托管 Agent 平台、trace surface、action schema、KB 与 tool loop 的关系。
- 对应 OpenBook：Chapter 4（LLM API）、Chapter 6-8（工具系统）、Chapter 16（prompt 组装）、Part IX（部署）。
- 使用提醒：Bedrock Agents 是平台抽象，细节受 AWS 产品约束；用它学组件边界，不要照搬产品形态。

### Google ADK + Memory Bank

- URL: https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/adk-quickstart
- URL: https://cloud.google.com/blog/topics/developers-practitioners/remember-this-agent-state-and-memory-with-adk
- 类型：SDK + Memory 平台文档
- 入库等级：B
- 核心问题：Agent 如何跨 session 管理 long-term memories，并在运行时检索。
- Harness 贡献：把记忆做成 service interface，而不是纯 prompt 文本。ADK wrapper 暴露 `add_session_to_memory`、`add_events_to_memory`、`search_memory`，可以通过 callbacks 或 tools 编排写入与读取。
- 可复用原语：`memory_service`、`session_events`、`add_session_to_memory`、`search_memory`、`callback_context`
- 适用场景：设计记忆服务、会话事件入库、长短期记忆分层、memory tool。
- 对应 OpenBook：Chapter 16（System Prompt）、Chapter 17（记忆系统）、Chapter 21（Dream）。
- 使用提醒：Google 的路线偏服务化记忆；OpenBook 的文件型记忆更轻。选型时先看可审计性、可迁移性和基础设施成本。

### Microsoft AutoGen / Microsoft Agent Framework

- URL: https://microsoft.github.io/autogen/stable/
- URL: https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/
- 类型：多 Agent runtime / migration 文档
- 入库等级：B
- 核心问题：多 Agent 协作、事件驱动 runtime、GroupChat、distributed agents 如何演进。
- Harness 贡献：AutoGen Core 把多 Agent 系统放到 event-driven runtime 里，Agent Framework 则是 Microsoft 新的多语言 SDK 基础。它适合研究 message routing、GroupChat、distributed worker、multi-language agent。
- 可复用原语：`event_driven_runtime`、`group_chat`、`message_routing`、`distributed_agent`、`agent_framework_migration`
- 适用场景：研究多 Agent 通信模型、迁移旧 AutoGen 系统、设计分布式 agent runtime。
- 对应 OpenBook：Chapter 12-15（多智能体）、Chapter 20（Commands / Plugin）。
- 使用提醒：新项目优先看 Microsoft Agent Framework；AutoGen 仍有研究价值，但不宜只停留在旧 API。

### O'Reilly: Building Applications with AI Agents

- URL: https://www.oreilly.com/library/view/building-applications-with/9781098176495/
- 类型：书
- 入库等级：C
- 核心问题：完整 Agent 应用工程包含哪些横向主题。
- Harness 贡献：目录覆盖系统设计、tool use、orchestration、knowledge and memory、validation and measurement、monitoring、improvement loops、protecting agentic systems、human-agent collaboration。适合作为 OpenBook 之外的横向教材。
- 可复用原语：`agent_system_design`、`validation_measurement`、`monitoring_production`、`improvement_loop`、`human_agent_collaboration`
- 适用场景：需要系统性读书、补 evaluation / monitoring / safety / human collaboration 章节时。
- 对应 OpenBook：Chapter 22（设计原则）、Part IX（OpenHarness）、全书横向对照。
- 使用提醒：这本书偏全面教材；用于补盲，不如官方文档适合查 API 细节。

### Manning: AI Agents in Action, Second Edition

- URL: https://www.manning.com/books/ai-agents-in-action-second-edition
- 类型：书
- 入库等级：C
- 核心问题：如何从 minimal agent 逐步走到 tool-using、多 agent、deployable systems。
- Harness 贡献：提供实践路径和连续代码示例思路。它适合把抽象 Harness 概念压成可运行项目演进路线。
- 可复用原语：`minimal_agent_path`、`tool_using_agent`、`multi_agent_path`、`deployable_system`
- 适用场景：教学、workshop、从零实现 demo、给团队安排循序渐进的学习路线。
- 对应 OpenBook：Appendix D（Mini Agent Harness）、Part I-III、Part V。
- 使用提醒：实践代码路径需要按当前 SDK/API 重写，避免复制旧框架写法。

## 聚合标签

| 标签 | 首选资料 |
|---|---|
| `long_running_agent` | Anthropic long-running harness、LangGraph、12-Factor Agents |
| `agent_loop` | OpenAI Agents SDK、Bedrock Agents、OpenBook Chapter 3-4 |
| `tool_system` | MCP Tools、OpenAI Agents SDK、Strands Tools、OpenBook Chapter 6-8 |
| `permission_guardrail` | OpenAI guardrails、Strands Hooks、OpenBook Chapter 9-11 |
| `memory` | Google ADK Memory Bank、LangGraph memory、OpenBook Chapter 17 |
| `multi_agent` | OpenAI handoffs、AutoGen / Agent Framework、OpenBook Chapter 12-15 |
| `observability` | Strands OTEL、OpenAI tracing、LangSmith、O'Reilly monitoring |
| `production_readiness` | 12-Factor Agents、O'Reilly、Anthropic Building Effective Agents |
