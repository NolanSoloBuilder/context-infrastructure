# Agent Harness Design Primitives

日期：2026-07-06

这些原语来自 OpenBook 与外部资料的交叉理解。它们不是某个 SDK 的 API，而是构建 Harness 时需要落成工程接口的概念。

## 一句话模型

Agent Harness = `model` + `loop` + `tools` + `state` + `context` + `constraints` + `verification` + `recovery` + `observability` + `extension_boundary`

其中 prompt 只属于 `context / INFORM` 的一部分。一个 Harness 不能只靠 prompt 自律来获得可靠性。

## 原语清单

### 1. Agent Loop

定义：驱动模型、工具调用、工具结果回填、下一轮推理、终止判断的循环。

必须回答：

- 每轮输入由哪些上下文组成
- 模型输出如何解析为 action / tool call / final answer
- 工具结果如何变成下一轮模型输入
- 什么时候继续，什么时候停止
- loop 的状态如何持久化

参考资料：OpenBook Chapter 3-4，OpenAI Agents SDK，Amazon Bedrock Agents。

工程接口建议：

```text
Run {
  id
  status: queued | running | waiting_for_approval | completed | failed | canceled
  input
  messages
  tool_calls
  checkpoints
  final_output
}
```

### 2. Tool Contract

定义：模型能调用的动作单元，包括 schema、描述、权限、执行器、结果预算和错误语义。

必须回答：

- 工具何时暴露给模型
- 输入 schema 是否足够具体
- 结果是否有 token / byte / 行数预算
- 错误是给模型重试，还是直接 fail closed
- 工具调用是否需要审批或 sandbox

参考资料：OpenBook Chapter 6-8，MCP Tools，Strands Tools，OpenAI Agents SDK。

工程接口建议：

```text
Tool {
  name
  description_for_model
  input_schema
  permission_policy
  executor
  result_budget
  error_policy: return_to_model | retry | fail_closed | require_human
}
```

### 3. State Surface

定义：Agent 运行时对外暴露、可保存、可恢复的状态面。

必须回答：

- 哪些状态属于业务状态，哪些属于执行状态
- 状态是否能被 checkpoint / resume
- human review 修改的是 state 还是 message
- 子 Agent / worker 是否共享状态

参考资料：LangGraph durable execution，12-Factor Agents，OpenAI Results and state。

工程接口建议：

```text
Checkpoint {
  run_id
  step_id
  conversation_state
  tool_state
  filesystem_snapshot_ref
  business_state_ref
  created_at
}
```

### 4. Context Assembly

定义：把 system instructions、用户输入、项目规则、记忆、环境状态、工具说明、检索结果组装成每轮模型输入的过程。

必须回答：

- 静态上下文和动态上下文如何分区
- 哪些内容可以缓存
- AGENTS.md / project rules / memory / MCP instructions 的优先级是什么
- 长上下文超限时先删什么、压缩什么、保留什么

参考资料：OpenBook Chapter 16-17，12-Factor Agents，Anthropic long-running harness。

工程接口建议：

```text
ContextPacket {
  static_instructions
  dynamic_environment
  project_rules
  memory_refs
  retrieved_knowledge
  tool_specs
  budget_report
}
```

### 5. Memory Boundary

定义：跨轮、跨 session、跨项目持久化的信息边界。

必须回答：

- 记忆是文件、数据库、向量库还是服务
- 记忆什么时候写入，谁能写
- 记忆检索如何限制数量
- 记忆过期如何验证
- 用户偏好、项目事实、错误经验、外部资料是否分开存储

参考资料：OpenBook Chapter 17 / Chapter 21，Google ADK Memory Bank，LangGraph memory。

工程接口建议：

```text
MemoryRecord {
  type: user | feedback | project | reference | error_experience
  description
  source
  confidence
  created_at
  last_verified_at
  payload_ref
}
```

### 6. Constraint Layer

定义：限制 Agent 能做什么、何时需要审批、哪些动作必须拒绝的边界。

必须回答：

- 哪些约束是确定性硬约束，哪些是软指导
- 权限检查在工具前、工具中、工具后哪个阶段执行
- 项目级规则和用户级规则谁优先
- sandbox / IAM / filesystem / network 如何配合

参考资料：OpenBook Chapter 9-11，OpenAI guardrails / human review，Strands Hooks，Part IX sandbox。

工程接口建议：

```text
PermissionDecision {
  action
  risk_level
  decision: allow | deny | require_approval
  reason
  policy_source
  audit_ref
}
```

### 7. Verification Layer

定义：判断 Agent 产出是否正确、是否可交付、是否需要重试或升级的机制。

必须回答：

- 验证是 deterministic test、LLM judge、human review 还是 trace analysis
- 验证失败后进入哪条修复路径
- 哪些验证结果写回 context / memory
- “完成”是否有可核对 artifact

参考资料：OpenBook Part IX，O'Reilly validation / monitoring，OpenAI evaluation / tracing，Anthropic long-running harness。

工程接口建议：

```text
VerificationResult {
  run_id
  checks: test | lint | build | security_scan | human_review | llm_eval
  status
  evidence_refs
  failure_summary
  next_action: accept | retry | repair | escalate
}
```

### 8. Recovery Loop

定义：失败后如何纠正，而不是让模型重新猜。

必须回答：

- 失败信息如何压缩进下一轮上下文
- 最多重试几次
- 重试是否换模型、换工具、换策略
- 什么时候升级给人
- 成功修复经验是否入记忆

参考资料：OpenBook Chapter 21 / Part IX，12-Factor error compaction，Anthropic long-running harness。

工程接口建议：

```text
RepairAttempt {
  source_failure
  compacted_error_context
  repair_prompt
  changed_files
  verification_result
  attempt_index
  max_attempts
}
```

### 9. Observability

定义：让开发者和用户知道 Agent 做了什么、为什么做、在哪里失败。

必须回答：

- 是否记录每次 model call、tool call、permission decision
- trace 是否能关联到 run / session / artifact
- 用户能看到多少 planning / progress
- 失败诊断需要哪些字段

参考资料：OpenAI tracing，LangSmith，Strands OpenTelemetry，Bedrock trace，O'Reilly monitoring。

工程接口建议：

```text
TraceEvent {
  run_id
  step_id
  event_type: model_call | tool_call | permission | checkpoint | verification | repair
  input_ref
  output_ref
  duration_ms
  token_usage
  metadata
}
```

### 10. Extension Boundary

定义：用户和第三方如何给 Harness 增加新能力，但不破坏核心 loop、权限和状态模型。

必须回答：

- 外部服务接入走 MCP 还是自定义 tool
- 流程知识走 Skill 还是 prompt
- 生命周期拦截走 Hook 还是 Plugin
- plugin 能注册哪些资源，不能做什么

参考资料：OpenBook Chapter 18-20，MCP docs，Strands hooks/plugins，OpenAI MCP integration。

工程接口建议：

```text
Extension {
  type: mcp_server | skill | hook | plugin | command
  capabilities
  load_policy
  permission_scope
  lifecycle_hooks
  version
}
```

## 设计审查顺序

做新 Harness 或审查现有 Harness 时，按这个顺序过：

1. Loop：有没有明确的 run state、继续/停止规则、tool result 回填机制。
2. Tool：工具 schema、权限、错误语义、结果预算是否完整。
3. State：是否能 checkpoint / resume，业务状态和执行状态是否分开。
4. Context：静态/动态上下文、记忆、项目规则、检索结果是否有明确优先级。
5. Constraint：危险动作是否有确定性硬约束，不依赖模型自觉。
6. Verification：完成标准是否可核对，失败是否有证据。
7. Recovery：失败是否进入 repair loop，而不是重启后重新猜。
8. Observability：能否从 trace 还原发生了什么。
9. Extension：MCP / Skills / Hooks / Plugins 是否分层，不互相污染。

## 与 `CONSTRAIN / INFORM / VERIFY / CORRECT` 的映射

| 支柱 | 包含原语 |
|---|---|
| `CONSTRAIN` | Constraint Layer、Tool permission、Sandbox、Human approval、Extension permission |
| `INFORM` | Context Assembly、Memory Boundary、Tool descriptions、MCP resources、Project rules |
| `VERIFY` | Verification Layer、Observability、Trace、Evaluation、Deterministic checks |
| `CORRECT` | Recovery Loop、Error compaction、Repair attempts、Memory update、Escalation |

Agent Loop 和 State Surface 是四根支柱包围的执行核心。没有这两个核心，四根支柱没有承载点；没有四根支柱，loop 只是让模型连续说话和调用工具。
