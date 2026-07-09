# Agent Harness 构建资料横向索引

日期：2026-07-06

## 结论

如果目标是“如何构建 Harness”，最接近 OpenBook 的资料不是泛泛讲 Agent 概念的文章，而是能回答这六件事的材料：Agent loop 怎么跑，工具怎么定义和执行，状态怎么持久化，危险动作怎么拦截，长任务怎么跨上下文继续，结果怎么验证和观测。

按这个标准看，OpenBook 的位置更像一本架构地图。外部资料里最值得搭配读的是 Anthropic 的 long-running agent harness 文章、OpenAI Agents SDK 文档、LangGraph runtime 文档、HumanLayer 12-Factor Agents、MCP 规范，以及 O'Reilly / Manning 两本偏系统化的 Agent 书。

## 已入仓的本地基线

OpenBook 成书版已经归档到：

- `contexts/source_materials/openbook/openbook_zh.md`
- `contexts/source_materials/openbook/openbook_zh.pdf`

这个本地基线用于内部章节定位。线上资料用于补外部框架、运行时、平台化能力和最新 API 的对照。

## 优先阅读清单

| 优先级 | 资料 | 类型 | 为什么接近 Harness |
|---|---|---|---|
| A | Anthropic: Effective harnesses for long-running agents | 工程文章 + quickstart | 直接讨论跨多个 context window 的 harness、initializer agent、coding agent、artifact handoff 和 clean state |
| A | Anthropic: Building effective agents | 工程文章 | 给出 workflow / agent 区分、简化原则、Agent-Computer Interface 和工具文档测试要求 |
| A | OpenAI Agents SDK docs | 官方 SDK 文档 | 覆盖 agent loop、tools、handoffs、guardrails、tracing、state、sandbox 和 human review |
| A | LangGraph docs | runtime 文档 | 把 durable execution、streaming、human-in-the-loop、persistence、memory 作为 orchestration runtime 能力 |
| A | HumanLayer 12-Factor Agents | 生产实践原则 | 把 context window、control flow、pause/resume、tool calls、execution state 这些 Harness 关节讲成工程约束 |
| A | Model Context Protocol docs | 协议规范 | 解决 Harness 如何连接外部工具、数据源、workflow 和 prompt 能力 |
| B | Strands Agents SDK | SDK + AWS 生态 | 适合看 tools、hooks、observability、sandbox、MCP 和多 agent 模式如何被产品化 |
| B | Amazon Bedrock Agents docs | 托管平台文档 | 适合看 action groups、knowledge bases、prompt templates、trace 和 orchestration loop 的托管形态 |
| B | Google ADK + Memory Bank docs | SDK + 平台文档 | 适合看 session、short-term state、long-term memory 和回调式记忆写入 |
| B | Microsoft AutoGen / Agent Framework | 多 Agent runtime | 适合看 event-driven agent runtime、GroupChat、多语言 / 分布式方向；注意 AutoGen 正在迁移到 Microsoft Agent Framework |
| C | O'Reilly: Building Applications with AI Agents | 书 | 目录覆盖系统设计、tool use、orchestration、memory、evaluation、monitoring、improvement loop、安全和 human collaboration |
| C | Manning: AI Agents in Action, Second Edition | 书 | 更偏实践代码路径，从 minimal agent 到 tool-using、多 agent、deployable systems |

## 资料笔记

### Anthropic: Effective harnesses for long-running agents

链接：https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents

这是最贴近“构建 Harness”的资料。它把长任务失败归因到 Harness 不足，而不是单纯归因到模型能力。重点机制是两段式：initializer agent 先准备环境、上下文和任务分解；后续 coding agent 每一轮只做增量推进，并在结束时留下明确 artifact，让下一个上下文窗口接得上。

对 OpenBook 的补充点：OpenBook 把 Agent Loop、记忆、工具、权限拆成章节；这篇文章把长任务问题压到一个可执行 harness pattern 上，特别适合我们后续设计 Workspace Harness 的 checkpoint、artifact、clean state 和 session handoff。

### Anthropic: Building effective agents

链接：https://www.anthropic.com/engineering/building-effective-agents

这篇更像原则入口。它建议先用简单方案，只有当单次 LLM 调用、RAG 或固定 workflow 不够时，再增加 agentic complexity。它强调三点：设计保持简单，透明展示 planning steps，认真设计 Agent-Computer Interface，也就是工具说明、工具结果和测试。

对 Harness 的价值：它能防止一上来设计过度。Harness 的第一性问题是“模型需要哪些可验证能力才能完成任务”，而不是“多加几个 agent 会不会更聪明”。

### OpenAI Agents SDK docs

链接：

- https://openai.github.io/openai-agents-python/
- https://developers.openai.com/api/docs/guides/agents

OpenAI Agents SDK 的 primitives 很清楚：Agent、tools、handoffs / agents-as-tools、guardrails。平台文档进一步把阅读路线放在 running agents、sandbox agents、orchestration and handoffs、guardrails and human review、results and state、integrations and observability 上。

对 Harness 的价值：如果我们要自己实现类似运行时，可以把它当作功能 checklist：loop、tool invocation、handoff ownership、input/output validation、state surface、trace / eval。OpenBook 的概念可以对照这里的实际 SDK surface。

### LangGraph docs

链接：https://docs.langchain.com/oss/python/langgraph/overview

LangGraph 把自己定义为 long-running, stateful agents 的低层 orchestration framework 和 runtime，重点能力是 durable execution、streaming、human-in-the-loop、persistence 和 memory。它还明确区分 LangChain、LangGraph、Deep Agents、LangSmith：Deep Agents 是 harness，LangGraph 是 runtime，LangSmith 是 tracing / evaluation / deployment 平台。

对 Harness 的价值：它适合作为“运行时底座”的对照。OpenBook 讲的是 Harness 全景；LangGraph 可以帮我们把 state graph、checkpoint、resume、human intervention 这些概念映射到一个具体 runtime。

### HumanLayer 12-Factor Agents

链接：https://github.com/humanlayer/12-factor-agents

这份资料的价值是把 Agent 可靠性拉回普通软件工程。它的 12 factors 包括 own your prompts、own your context window、tools as structured outputs、unify execution state and business state、launch / pause / resume with simple APIs、own your control flow、compact errors into context window、small focused agents、stateless reducer。

对 Harness 的价值：这是一套生产约束，不是框架教程。它适合用来审查我们自己的 Agent Harness 是否把控制流、状态、上下文、人工介入和错误恢复交给了可测试的工程接口。

### Model Context Protocol docs

链接：

- https://modelcontextprotocol.io/docs/getting-started/intro
- https://modelcontextprotocol.io/specification/2025-06-18/server/tools

MCP 的定位是让 AI 应用连接外部系统：data sources、tools、workflows、specialized prompts。Tools 规范里明确 tool 需要唯一名称和 schema，语言模型可以基于上下文自动发现和调用。

对 Harness 的价值：MCP 不解决 Agent Loop 本身，但它解决能力扩展边界。用 OpenBook 的分层看，MCP 属于“外部能力连接层”，不应该和 Skills、Hooks、Plugin 混成一个概念。

### Strands Agents SDK

链接：

- https://strandsagents.com/
- https://strandsagents.com/docs/user-guide/concepts/tools/
- https://strandsagents.com/docs/user-guide/concepts/agents/hooks/
- https://aws.amazon.com/blogs/machine-learning/strands-agents-sdk-a-technical-deep-dive-into-agent-architectures-and-observability/

Strands 值得关注的不是“几行代码起 agent”，而是它把工具、hooks、MCP、sandbox、observability 和多 agent pattern 做成一个 AWS 生态里的开发面。Hooks 文档尤其接近 OpenBook 的 Hook 章节：它把 agent lifecycle event 暴露出来，允许拦截、修改、取消、retry、resume。

对 Harness 的价值：适合看 Hook / Intervention / Observability 的工程接口应该长什么样。

### Amazon Bedrock Agents docs

链接：https://docs.aws.amazon.com/bedrock/latest/userguide/agents-how.html

Bedrock Agents 是托管式视角。它的 build-time 组件包括 instructions、action groups、knowledge bases、security configurations、prompt templates；runtime 过程包括 preprocessing、orchestration、post-processing。Orchestration loop 会选择 action group 或 query knowledge base，并把 observation 重新注入下一轮 prompt。Trace 可以看 rationale、actions、queries、observations 和每一步 prompt。

对 Harness 的价值：适合看“平台化 Agent Harness”如何把工具、知识库、session、trace 和 prompt store 产品化。

### Google ADK + Memory Bank docs

链接：

- https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank/adk-quickstart
- https://cloud.google.com/blog/topics/developers-practitioners/remember-this-agent-state-and-memory-with-adk

Google ADK / Memory Bank 资料主要补记忆层。Memory Bank 允许 agents 跨 session 管理 long-term memories，ADK wrapper 暴露 add_session_to_memory、add_events_to_memory、search_memory，并可通过 callbacks / tools 编排。

对 Harness 的价值：适合看“记忆不是单纯塞 prompt，而是一组可调用服务接口”这件事。它和 OpenBook Chapter 17 的文件型记忆路线不同，但问题域相同。

### Microsoft AutoGen / Microsoft Agent Framework

链接：

- https://microsoft.github.io/autogen/stable/
- https://learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/

AutoGen 适合看多 agent 方向。官方文档把 Core 定位成 event-driven programming framework，用于 scalable multi-agent AI systems；Microsoft Learn 的迁移指南说明 AutoGen 先前推动了 GroupChat 和 event-driven agent runtime 等概念，现在 Microsoft Agent Framework 是后续基础。

对 Harness 的价值：适合研究多 Agent communication、event runtime、distributed workers。选型上要注意：如果要新项目，优先看 Microsoft Agent Framework，而不是只停留在旧 AutoGen。

### O'Reilly: Building Applications with AI Agents

链接：https://www.oreilly.com/library/view/building-applications-with/9781098176495/

这本书的目录覆盖面很接近 Harness：Designing Agent Systems、Tool Use、Orchestration、Knowledge and Memory、Validation and Measurement、Monitoring in Production、Improvement Loops、Protecting Agentic Systems、Human-Agent Collaboration。

对 Harness 的价值：适合做外部书籍层面的系统化对照，尤其补 evaluation、monitoring、production protection 和 human-agent collaboration。相比 OpenBook，它更像横向教材。

### Manning: AI Agents in Action, Second Edition

链接：https://www.manning.com/books/ai-agents-in-action-second-edition

Manning 页面把它定位为 practical and comprehensive guide，覆盖 designing、implementing、evaluating、deploying agents，并从 minimal agent 逐步走向 tool-using、多 agent 和 deployable systems。

对 Harness 的价值：适合作为实践路径补充。它不一定比 OpenBook 更像架构地图，但对“从可运行小系统逐步加工具、记忆、多 Agent、部署”有用。

## 与 OpenBook 的对应关系

| Harness 问题 | OpenBook 本地章节 | 外部资料 |
|---|---|---|
| 长任务跨上下文继续 | Chapter 5、Chapter 14、Chapter 21、Part IX | Anthropic long-running harness、12-Factor Agents |
| Agent Loop 与 state surface | Chapter 3-5 | OpenAI Agents SDK、LangGraph、Bedrock Agents |
| 工具 schema 与执行 | Chapter 6-8 | MCP Tools、OpenAI tools、Strands tools、Bedrock action groups |
| 权限 / guardrails / human review | Chapter 9-11 | OpenAI guardrails、Strands hooks、Bedrock preprocessing / trace |
| 记忆系统 | Chapter 16-17、Chapter 21 | Google ADK Memory Bank、LangGraph memory、12-Factor context window |
| 多 Agent 编排 | Chapter 12-15 | OpenAI handoffs、AutoGen / Agent Framework、LangGraph subgraphs |
| 观测与评估 | Chapter 22、Part IX | OpenAI tracing / eval、LangSmith、Strands OpenTelemetry、O'Reilly monitoring chapters |
| 协议和插件边界 | Chapter 18-20 | MCP docs、Strands MCP、OpenAI MCP integration |

## 推荐阅读顺序

如果只想快速补 Harness 构建心智：

1. OpenBook Part I、Part II、Part III，先建立 Agent = LLM + Harness、loop、tools 三件事。
2. Anthropic Building Effective Agents，校准什么时候该用 workflow，什么时候该用 agent。
3. Anthropic Effective Harnesses for Long-Running Agents，理解为什么 compaction 不够、为什么要 initializer / coding agent / artifact handoff。
4. OpenAI Agents SDK docs，拿实际 SDK surface 对照 Agent / tools / handoffs / guardrails / tracing / state。
5. LangGraph overview，理解 durable execution、persistence、human-in-the-loop 这些 runtime 能力。
6. 12-Factor Agents，用生产约束重新审查 context、control flow、pause/resume、error compaction。
7. MCP docs，明确外部能力连接层和工具 schema。
8. 再按需要补 AWS Bedrock、Google ADK、Strands 或 O'Reilly / Manning。

## 对我们自己的 Harness 设计启发

第一，Harness 应该从状态机和边界开始，而不是从 prompt 开始。Prompt 是 INFORM 的一部分，不能替代 CONSTRAIN、VERIFY、CORRECT。

第二，长任务能力的关键不是无限上下文，而是可交接环境。Initializer、artifact、checkpoint、progress ledger、clean state，比“更长 context window”更可控。

第三，工具系统要同时设计 schema、权限、结果预算和错误语义。工具结果不是普通 stdout，它是下一轮模型输入的一部分。

第四，记忆要先区分工作记忆、跨 session 记忆、项目治理文档和检索知识库。文件型记忆、Memory Bank、LangGraph memory 都是在解决这个边界，只是存储形态不同。

第五，观测和评估要进入第一版 Harness。没有 trace、trajectory、tool-call log、resume state，就很难判断 Agent 是真的完成了任务，还是只是输出了一个看似完成的回答。

第六，MCP、Skills、Hooks、Plugins 应该保持分层。MCP 连接外部能力，Skills 注入过程知识，Hooks 拦截生命周期，Plugins 打包分发能力。把这些混成一个系统会让权限、加载和调试边界变得模糊。

## 后续可做

如果要继续深入，下一步可以把这份索引变成一个 `agent_harness_design_checklist.md`：按 `CONSTRAIN / INFORM / VERIFY / CORRECT` 列出我们自己的 Harness 必备接口，再逐项对照 OpenBook、OpenAI SDK、LangGraph 和 Anthropic long-running harness。
