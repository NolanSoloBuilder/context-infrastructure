# Workspace Harness 能力完备性评估

日期：2026-06-18  
范围：`mindspace_web_frontend`、`mindspace_backend`、`mindspace_ml_backend`  
评估问题：当前 Workspace 是否已经具备一个生产级 agent harness 所需的上下文、记忆压缩、工具治理、证据运行、产物和可观测能力。

## 结论

当前 Workspace 已经不是空壳，具备一个 **内部 Beta 级 agent harness** 的主体骨架：Workspace shell、workspace-scoped live conversation、chat/evidence preflight、channel-agent context compaction、Workspace Memory/Source/Artifact/Run 表、Agent Plaza evidence bridge、runtime references、artifact provenance、profile runtime registry 都已经落到了真实代码路径。

但它还不能算 **生产级完备 harness**。主要缺口不在“有没有记忆压缩”这一个点，而在三类闭环：

1. **profile runtime 的质量门槛还未产品化**：evidence run 已桥接 Agent Plaza，但不同 Workspace profile 的 source policy、tool policy、provenance coverage、open questions 和失败降级还缺统一验收矩阵。
2. **记忆是两套系统，闭环还需要治理**：Workspace Memory Context 和 channel-agent long-term memory 已明确区分，但缺少跨层策略、可解释 UI、去重/冲突/清理和运营指标。
3. **缺少跨三仓端到端验收**：ML 单测覆盖了 context compaction、workspace context prompt、router forwarding；但 Web -> business backend -> ML -> backend persistence -> Web refresh 的真实长对话、压缩、引用恢复、artifact provenance、memory update 还需要 E2E smoke 和质量评测。

一句话判断：**基础能力已达“可继续用 Workspace 替代 Agent Plaza 的实现底座”，但还没有达到“可放心对外承诺长期任务工作台”的完备度。**

## 外部 Harness 标准

本次参考了 `dawei008/openbook` 上下文沉淀文档，以及 Google/GitHub/web 搜索到的官方和一手资料。可复用的评估维度如下：

| 维度 | 外部原则 | 对 Workspace 的含义 |
| --- | --- | --- |
| Runtime loop / session | Agent harness 要清楚拥有 state、history、tool execution、handoff 和 guardrails。OpenAI Agents 文档把 runtime loop、state、sandbox agents、handoff、guardrails、tools/MCP/observability/evals 作为阅读主线。 | Workspace 不能只是 UI 容器；必须有独立 session、run、checkpoint、tool policy、artifact/source/memory 回写。 |
| Context engineering | Anthropic 强调 context 是有限资源，context engineering 是维护系统指令、工具、外部数据、历史和 memory 的 token 集合；过多上下文会带来 context rot。 | Workspace 需要有分层预算、压缩、可审计 manifest，而不是把 Goal/Memory/Source/Artifact 全量塞进 prompt。 |
| Memory / compaction / tool clearing | Claude Cookbook 区分 compaction、tool-result clearing、memory：compaction 是压缩当前上下文；tool-result clearing 是丢弃可重取的旧工具结果；memory 是结构化持久笔记。 | Workspace 不能把“保存一条 memory”当作“长上下文管理”；需要同时处理会话压缩、工具结果压缩和长期记忆。 |
| Tool design | Anthropic 工具文章强调工具命名空间、上下文有效性、token efficiency、工具描述和 eval。 | Workspace profile 需要明确工具 allowlist/blocklist 和工具结果压缩，不能让通用 chat 工具面直接承担高质量研究任务。 |
| Multi-agent / long-horizon | Anthropic multi-agent research system 提到长任务需要 checkpoint、压缩、外部 memory、subagent 输出落文件或 artifacts，降低信息丢失。 | Workspace 的 Run/Artifact/Source/Memory 应成为长任务外部状态，不应只依赖一次模型上下文。 |

主要来源：

- Anthropic, [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)
- Anthropic, [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Anthropic, [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- Anthropic, [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- Claude Cookbook, [Context engineering: memory, compaction, and tool clearing](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools)
- OpenAI Agents SDK, [Sessions](https://openai.github.io/openai-agents-python/sessions/)
- OpenAI, [Agents guide](https://developers.openai.com/api/docs/guides/agents)
- 本仓沉淀：`contexts/survey_sessions/2026_06_18_openbook_context_support.md`

## 三仓现状

### Web：Workspace Shell 已成型

`mindspace_web_frontend/src/app/README.md` 已把 Workspace 定义为登录后业务体验的一等入口，当前关键约束包括：

- `/app/workspaces` 和 `/app/workspaces/:workspaceId` 是 Workspace 路由，主导航入口暂时隐藏。
- Workspace detail 是 Codex-like workspace-scoped live conversation + 右侧 Workspace Sidebar，不复用平台级浮层 ChatPanel。
- Goal、Memory、Source、Schedule、Artifact、Activity、Version History、Suggestions 收纳在右侧 Sidebar。
- Web 不按关键词判断 `executionMode`，只传 active artifact、artifactIntent、selection、mountedSkillRefs、profile hint，由后端请求 ML preflight。
- `chatSessionId` 由后端绑定，刷新恢复必须读真实 session history，localStorage 只做临时兜底。
- Memory Context 只消费 stream 返回的持久化事件，前端不能关键词直写 memory。
- Source Context 已拆分为长期挂载源和本轮引用；runtime references 读取 `workspace_run_sources` 或 run metadata，不混入长期 Source Context。
- Artifact provenance 是 version-scoped contract，支持 `references`、`citationSpans`、`htmlAnchors`、`claimProvenance`、`numericClaims`、`provenanceCoverage`。

判断：Web 层的产品边界和状态隔离基本正确，已经从“页面功能”转向“harness shell”。当前风险主要是 UI 能否稳定消费 ML/后端产出的所有事件和 provenance，而不是缺少概念设计。

### Business backend：Workspace 状态与 stream 编排已落地

关键代码路径：

- `mindspace/domain/model/workspace_models.py`
  - `WorkspaceModel`
  - `WorkspaceMemoryModel`
  - `WorkspaceSourceModel`
  - `WorkspaceArtifactModel`
  - `WorkspaceArtifactVersionModel`
  - `WorkspaceRunModel`
  - `WorkspaceRunSourceModel`
- `mindspace/router/v1/workspace_router.py`
  - `POST /{workspace_id}/conversation/stream`
  - 创建或绑定 workspace chat session
  - 先调用 execution preflight
  - `chat` 走 `_iter_workspace_channel_agent_turn_stream`
  - `evidence` 走 `_iter_workspace_evidence_run_stream`
- `mindspace/service/channel_agent_context_checkpoint_service.py`
  - 加载 active checkpoint
  - 按 `coveredUntilMessageId` 拼接 raw history tail
  - 保存 ML 返回的 context checkpoint
- `mindspace/service/workspace_conversation_context_events.py`
  - 解析 `memory_update`
  - owner/workspace-scoped 写入 Workspace Memory
  - 对“沉淀/记住/保存”显式用户指令做兜底持久化
- `mindspace/service/workspace_run_operations.py`
  - 执行 Workspace run
  - 写入 `memory_diff`、`source_diff`、`artifact_diff`
  - 投影 runtime sources

判断：backend 已经承担了 harness 里最关键的“状态所有权”：raw messages 仍是 source of truth，checkpoint 是派生续接状态；Workspace Memory/Source/Artifact/Run 是外部状态，不依赖浏览器内存。这一点符合长任务 harness 的基本要求。

### ML backend：Channel-agent Harness 能力较强，Workspace Evidence Bridge 初步完成

关键代码路径：

- `channel_langgraph_runtime_preparer.py`
  - 构造 workspace context message
  - 加载 memory context
  - 调用 `channel_agent_context_manager_service.prepare_context`
  - 应用 tool policy
  - 输出 debug payload
- `channel_agent_context_manager_service.py`
  - 合并 checkpoint summary、memory context、turn context
  - 超预算时触发 pre-turn summarization
  - 生成 checkpoint payload、context manifest 和 compaction events
- `channel_agent_context_budget.py`
  - 定义 context 层级预算：runtime policy、current turn、task state、recent history、tool trace、summary checkpoint、memory、environment、skills retrieval。
- `channel_agent_context_compaction.py`
  - 对 context fragments 按 layer/global budget 截断或丢弃
  - pinned fragments 不移除
- `channel_agent_memory_context_service.py`
  - 加载 bounded long-term memory context
  - scope 可走 `context_type/context_id`，因此 Workspace scope 可用
- `channel_agent_memory_tools.py`
  - 提供 recall 和 `record_memory_observation_tool`
  - 不让主 agent 直接 add/replace/remove active memory
- `channel_workspace_context_prompt_service.py`
  - 构造 bounded Workspace visible context
  - 明确 Workspace memory_update 与 global record_memory_observation_tool 是两套记忆
  - active artifact 截断到 2600 chars，总消息约束小于 7000 chars
- `workspace_execution_decision_service.py`
  - 轻量模型 preflight 判断 `chat` 或 `evidence`
- `workspace_evidence_run_service.py`
  - 通过 Agent Plaza task-agent semantics 执行 evidence-backed run
  - 输出 artifact update、references、citation spans、claim provenance、numeric claims、evidence pack
- `workspace_profile_registry.py`
  - profile -> Agent Plaza template、source families、required result fields、provenance level
- `agent_plaza_tool_policy.py`
  - template-scoped allowlist/blocklist
  - 阻断 channel mutation、memory mutation、image generation 等不适合任务执行的工具
- `agent_plaza_tool_result_compactor.py`
  - 对 document store/search result 做工具结果压缩，保留 locators/references

判断：ML 侧已经拥有比较完整的 channel-agent harness。Workspace live conversation 继承了这套压缩、memory context 和工具策略；Workspace evidence run 则开始把 Agent Plaza 迁入 profile runtime。

## 能力矩阵

| 能力 | 当前状态 | 评估 |
| --- | --- | --- |
| Workspace-scoped session | 后端创建/绑定 `chatSessionId`，Web 刷新读真实 history。 | 基本完备 |
| Raw history + checkpoint | backend raw messages 是 source of truth，checkpoint 按 covered message tail 续接。 | 基本完备 |
| 会话压缩 | ML `ChannelAgentContextManagerService` 有 pre-turn summarization、checkpoint、manifest；backend 持久化 checkpoint。 | 基本完备，但需 E2E 验收 |
| Context 分层预算 | ML 有 layer ratio、pinned context、fragment truncate/drop。 | 基本完备 |
| Workspace visible context bounded | prompt service 限制 artifact/list/text 长度，测试确认内容小于 7000 chars。 | 基本完备 |
| Long-term memory | channel-agent 有 vector/keyword recall、observation -> curation；Workspace 有独立 Memory 表和 memory_update。 | 部分完备，两套记忆治理未闭环 |
| Tool policy | channel-agent 有 deterministic router；Agent Plaza 有 template-scoped policy；Workspace evidence bridge 使用 Workspace-specific resolver。 | 基本完备，但 profile 质量门槛未验收 |
| Tool result compaction | Agent Plaza document/search results 有 compactor；channel-agent context 有 tool trace layer。 | 部分完备，通用工具结果 clearing 仍需矩阵化 |
| Evidence-backed run | Workspace preflight 可进入 evidence run，并桥接 Agent Plaza task-agent。 | 基本完备 |
| Provenance | artifact version 支持 references/citation spans/claim/numeric coverage；evidence pack 可写入 artifact update。 | 基本完备，但需要质量 gate |
| Runtime source audit | `workspace_run_sources` 投影，Web 区分本轮引用和长期挂载源。 | 基本完备 |
| Artifact lifecycle | 版本、恢复、publish、suggestion、active artifact contract 已有。 | 基本完备 |
| Multi-agent/subagent | Agent Plaza research/evidence collector 有多阶段思想，但 Workspace 当前主要是 channel-agent/evidence bridge。 | 部分完备 |
| Observability | ML debug payload 包含 context budget、tool policy、memory、skills；backend run metadata 保存 result。 | 部分完备，缺生产指标面板和失败 taxonomy |
| Evals / regression | 有 ML 单测；缺跨三仓 E2E 和质量评测集。 | 不完备 |

## 关于“记忆压缩”的专项判断

这里要区分四种能力：

1. **会话历史压缩**：已有。`channel_agent_context_manager_service.py` 在超预算时生成 conversation summary checkpoint，backend 保存并按 `coveredUntilMessageId` 只回放 tail。
2. **Workspace visible context 压缩**：已有。`channel_workspace_context_prompt_service.py` 对 workspace、goal、active artifact、sources、memories、selection 做 bounded formatting。
3. **工具结果压缩/清理**：部分已有。Agent Plaza 的 document/search 工具有 compactor；channel-agent 有 tool trace layer budget。但还没有形成“哪些工具结果可丢、哪些 locator 必须保留、哪些必须转 artifact/source”的全局 contract。
4. **长期记忆治理**：部分已有。channel-agent long-term memory 有 recall/observation/curation，Workspace Memory 有 memory_update 和显式用户指令兜底；但两套 memory 的边界、冲突、去重、可解释 UI、质量指标还需要治理。

所以，问“Workspace 有没有记忆压缩”：答案是 **有会话压缩和 bounded context，但长期记忆治理还没完备**。

## 主要缺口

### P0：跨三仓 E2E 验收缺失

需要至少覆盖这些真实链路：

- 创建 Workspace -> 自动首轮 live conversation -> backend 绑定 chatSessionId -> Web 刷新恢复 user/assistant history。
- 长对话触发 context compaction -> ML 返回 checkpoint -> backend 保存 -> 下一轮只回放 checkpoint tail -> 回复仍保留任务连续性。
- 用户说“沉淀这条记忆” -> backend 兜底写 Workspace Memory -> Web Sidebar 刷新可见。
- Agent 主动发 `memory_update` -> backend 写 Workspace Memory -> Web 消费事件。
- 进入 evidence run -> Agent Plaza bridge 输出 references/citation spans/evidence pack -> backend 写 artifact version provenance + workspace_run_sources -> Web 本轮引用和 artifact citation 可打开原文。

当前只跑了 ML 侧相关单测，不能替代这些 E2E。

### P0：Profile Runtime Quality Gate 不足

`workspace_profile_registry.py` 已有 profile 到 template/source families/provenance 的映射，但还需要正式质量门槛：

- 每个 profile 的 required evidence families。
- 是否允许 provider web search fallback。
- 最低 provenance coverage。
- numeric claim 缺出处时如何暴露 open item。
- weak signal 是否允许进入结论。
- source tier/source usage 的可解释 contract。
- tool allowlist/blocklist 的回归测试。

没有这些 gate，Workspace 虽然能跑 evidence，但不能保证不降低 Agent Plaza 质量。

### P1：两套 Memory 的产品语义需要收口

当前已有明确提示：Workspace `memory_update` 持久到 Workspace Memory Context；global `record_memory_observation_tool` 是另一套 long-term agent memory。

风险在于：

- 用户可能不知道某条记忆是 Workspace-scoped 还是 global agent memory。
- Workspace Memory 没看到 conflict/merge/expiration/importance 策略。
- channel-agent memory recall 可能通过 `context_type=workspace` 命中 scoped memory，但这和 Workspace Memory 表不是同一数据源。
- 后续运营需要能回答“本轮模型到底用了哪些 memory”。

建议把 Memory 分成三层并在文档和 UI 上固定：

- Workspace Memory：任务空间内显式事实、偏好、约束。
- Agent Long-term Memory：跨会话、跨产品的用户/项目偏好，由 curation 管。
- Conversation Summary Checkpoint：只服务压缩续接，不作为用户可编辑 memory。

### P1：Evidence run 与 live conversation 的上下文衔接仍偏弱

`workspace_evidence_run_service.py` 调 Agent Plaza task-agent 时传 `context_checkpoint=None`，主要依赖 request payload 中的 workspace、goal、memories、sources、active artifact。也就是说 evidence run 不是完整继承 live conversation 的 summary checkpoint 语义。

这不一定是 bug，但要明确：

- evidence run 应该消费哪些历史上下文？
- 是否只消费 Workspace Memory/Source/Artifact，而不消费闲聊历史？
- 用户刚在 live conversation 里澄清的条件，进入 evidence run 时是否已经进入 request payload 或 memory？

建议把 evidence run 的上下文输入 contract 固化为 `WorkspaceRunContextPack`，包括 goal snapshot、active artifact digest、latest workspace memory、mounted sources、selected conversation summary、user latest instruction。

### P1：工具结果 clearing 还没有全局化

外部 harness 最佳实践会把 tool-result clearing 和 memory/compaction 分开。当前 Agent Plaza document/search 有 compactor，但通用 channel-agent 工具结果的生命周期还需要明确：

- 哪些工具结果可只保留 locator/reference？
- 哪些必须写入 Workspace Source/Artifact/Run metadata？
- 哪些可从 model context 中清理但保留 audit？
- 工具调用失败或半成功如何进入 run ledger？

### P2：Observability 和 eval 不足

已有 debug payload 和 run metadata，但缺少产品级指标：

- context compaction trigger rate、压缩前后 token、summary coverage。
- memory update accepted/deduped/conflicted/skipped。
- evidence run source count、source tier 分布、provenance coverage。
- citation open success rate。
- run failure taxonomy。
- profile-by-profile regression suite。

## 验证

本次跑了 ML 侧相关单测：

```bash
cd /Users/xuhao/Documents/Other/mindspace_ml_backend
.venv/bin/python -m pytest \
  tests/test_channel_conversation_context_service.py \
  tests/test_channel_workspace_context_prompt_service.py \
  tests/test_workspace_agent_router.py \
  tests/test_channel_langgraph_router.py \
  -q
```

结果：`28 passed in 16.56s`。

当前三仓 commit：

- `mindspace_web_frontend`: `abe5087`
- `mindspace_backend`: `f55d912`
- `mindspace_ml_backend`: `0b5bcff`

## 建议下一步

1. 先补一个 Workspace Harness E2E smoke 文档和脚本，覆盖长对话压缩、memory_update、evidence run、artifact provenance、runtime references。
2. 为每个 Workspace profile 建 `quality_gate.md` 或代码化 schema，明确 source/provenance/tool policy 的最低标准。
3. 定义 `WorkspaceRunContextPack`，让 evidence run 明确消费哪些 live conversation/summary/memory/source/artifact 输入。
4. 把 Memory 三层模型写入 Web/backend/ML README，并在 UI 上区分 Workspace Memory 与 agent long-term memory。
5. 建 profile regression set：至少每个 profile 2 个成功样例、1 个弱证据样例、1 个失败/缺来源样例。

