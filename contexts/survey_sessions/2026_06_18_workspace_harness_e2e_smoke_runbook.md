# Workspace Harness E2E Smoke 说明

日期：2026-06-18  
范围：`mindspace_web_frontend`、`mindspace_backend`、`mindspace_ml_backend`  
目标：给 Workspace Harness 建一套可重复执行的 E2E smoke 验收说明，优先验证 contract 和状态闭环，再做真实三服务联调。

## 推荐方案

第一阶段采用 **Backend API E2E + 离线契约 E2E**，再补一个可选的三服务本地联调 smoke。

暂不优先上 Playwright。原因是 Workspace Harness 当前最大风险在 backend 编排和状态闭环，而不是浏览器点击路径。Web 侧已经有大量 `AppWorkspaceDetailPage.test.tsx` 级别的 Vitest 测试，先把 SSE contract、Workspace 状态回写和 ML bridge 验稳，收益更高、flakiness 更低。

## 分层策略

| 层级 | 默认执行 | 作用 | 依赖 |
| --- | --- | --- | --- |
| 离线契约 E2E | 是 | 验证三仓 payload、SSE event、provenance、memory/source/artifact contract | fake service / fixture |
| Backend API E2E | 是 | 验证 `/workspaces/:id/conversation/stream` 分流、持久化、checkpoint 续接 | 测试 DB 或 fake DAO |
| ML harness 单测 | 是 | 验证 context compaction、workspace context prompt、evidence bridge | pytest fixture |
| Web contract 测试 | 是 | 验证 Web 消费 stream、刷新 detail、展示引用/记忆/产物 | Vitest + mocked service |
| 三服务 live smoke | 否，显式开启 | 验证本机真实链路 | 8099/8079/9090、本地 auth/session |
| Browser E2E | 暂缓 | 验证完整用户点击体验 | Playwright、稳定后端/测试账号 |

## 必测场景

### 1. Workspace Chat 分支

目标：普通 Workspace 对话不表现成后台 queued run，但仍能写审计快照。

断言：

- Web 调用 `POST /api/v1/workspaces/{workspace_id}/conversation/stream`。
- Backend 先返回 `start` 和 `workspace_context_update`。
- Backend 调 ML execution preflight，返回 `workspace_execution_decision`，`executionMode=chat`。
- Chat 分支复用 channel-agent turn。
- SSE 中出现 assistant/tool/process 事件并最终 `done`。
- 刷新 Workspace detail 后能恢复 `chatSessionId` 对应历史。
- conversation run 只用于引用恢复，不进入 Web Activity Timeline。

### 2. Context Checkpoint / 记忆压缩

目标：长对话超预算时生成 checkpoint，并在下一轮只回放 checkpoint 后的 tail。

断言：

- ML `channel_agent_context_manager_service` 触发 pre-turn summarization。
- 返回 `context_checkpoint`，包含：
  - `runtimeType=channel_agent`
  - `coveredUntilMessageId`
  - `summaryText`
  - `contextManifest`
  - `tokenEstimateBefore`
  - `tokenEstimateAfter`
- Backend 保存 active checkpoint。
- 下一轮请求前 backend 读取 checkpoint，并只拼接 `coveredUntilMessageId` 之后的 raw message tail。
- 没有 `coveredUntilMessageId` 的 mid-turn checkpoint 不应持久化为可续接状态。

### 3. Workspace Memory 写回

目标：Workspace Memory 只通过明确 contract 写入，不由前端关键词直写。

断言：

- 用户显式说“沉淀/记住/保存”时，backend `workspace_conversation_context_events.py` 做 owner-scoped 兜底写入。
- ML 主动发 `memory_update` 时，backend 写入 `workspace_memories`。
- 去重按 memory content 生效。
- Web 只消费 stream/detail 返回的 Memory Context，不直接写 memory。
- Workspace Memory 与 global `record_memory_observation_tool` 语义区分清楚。

### 4. Evidence Run 分支

目标：需要证据研究的 Workspace turn 能桥接 Agent Plaza runtime，并回写可审计结果。

断言：

- execution preflight 返回 `executionMode=evidence`。
- Backend 创建 `runType=conversation` 的 Workspace run，并调用 ML `/agent/v1/workspace-agent/runs`。
- ML `workspace_evidence_run_service.py` 通过 Agent Plaza task-agent semantics 产出：
  - `references`
  - `citationSpans`
  - `claimProvenance`
  - `numericClaims`
  - `provenanceCoverage`
  - `evidencePack`
- Backend 写入：
  - `workspace_runs.metadata.evidencePack`
  - `workspace_run_sources`
  - `workspace_artifact_versions.provenance_json`
- Web 本轮引用来自 runtime references，不混入长期 Source Context。

### 5. Artifact Provenance / 原文打开

目标：产物里的引用能稳定从 Workspace scoped resolver 打开原文。

断言：

- Markdown artifact 使用 `citationSpans`。
- HTML artifact 使用 `htmlAnchors` / `data-ms-citation-id`。
- 结构化 evidence result 使用 Agent Plaza 同源 `blocks/source_refs/referencePayloads`。
- 点击 citation 调用 `/api/v1/workspaces/{workspace_id}/document-references/*`。
- 前端不直接使用 `storage_url` 跨 artifact 取原文。

## 建议测试落点

### mindspace_backend

优先扩展：

- `test/test_workspace_router.py`
- `test/test_workspace_conversation_context_events.py`
- `test/test_channel_agent_context_checkpoint_service.py`
- `test/test_workspace_service.py`

建议新增场景：

- chat/evidence execution decision 分流。
- `context_checkpoint` 保存和下一轮 request context 构造。
- `memory_update` 持久化和去重。
- evidence result 投影到 run source 和 artifact provenance。

参考命令：

```bash
cd /Users/xuhao/Documents/Other/mindspace_backend
.venv/bin/python -m pytest \
  test/test_workspace_router.py \
  test/test_workspace_conversation_context_events.py \
  test/test_channel_agent_context_checkpoint_service.py \
  test/test_workspace_service.py \
  -q
```

### mindspace_ml_backend

优先扩展：

- `tests/test_channel_conversation_context_service.py`
- `tests/test_channel_workspace_context_prompt_service.py`
- `tests/test_workspace_agent_service.py`
- `tests/test_workspace_agent_router.py`

建议新增场景：

- Workspace turn 超预算触发 checkpoint。
- Workspace visible context 保持 bounded，不 dump 全 artifact。
- evidence bridge 输出 evidence pack 和 provenance fields。
- Workspace profile runtime 保持 source families/tool policy/provenance requirement。

参考命令：

```bash
cd /Users/xuhao/Documents/Other/mindspace_ml_backend
.venv/bin/python -m pytest \
  tests/test_channel_conversation_context_service.py \
  tests/test_channel_workspace_context_prompt_service.py \
  tests/test_workspace_agent_service.py \
  tests/test_workspace_agent_router.py \
  -q
```

### mindspace_web_frontend

优先扩展：

- `src/app/pages/AppWorkspaceDetailPage.test.tsx`
- `src/app/lib/workspace-document-reference.test.ts`
- `src/utils/router-adapter.test.ts`

建议新增场景：

- stream 中 `workspace_execution_decision` 按过程步骤展示。
- `memory_update` 后刷新右侧 Memory Context。
- runtime references 和 mounted sources 分开展示。
- conversation run 不进入 Activity Timeline。
- artifact provenance citation 点击走 Workspace resolver。

参考命令：

```bash
cd /Users/xuhao/Documents/Other/mindspace_web_frontend
pnpm test -- \
  src/app/pages/AppWorkspaceDetailPage.test.tsx \
  src/app/lib/workspace-document-reference.test.ts \
  src/utils/router-adapter.test.ts
```

## 可选三服务 Live Smoke

仅在显式设置环境变量时执行，不进入默认 CI。

前提：

- Web: `http://localhost:8099`
- Backend: `http://localhost:8079`
- ML backend: `http://localhost:9090`
- 本地已有可用登录态或测试 token。

开启方式：

```bash
RUN_WORKSPACE_HARNESS_LIVE_SMOKE=1 ./scripts/workspace-harness-smoke.sh
```

脚本建议只做接口级 smoke：

1. 创建 Workspace。
2. 获取 detail，确认 `workspaceId`、`chatSessionId`、primary/default artifact 状态。
3. 发送普通 chat turn。
4. 断言 SSE 包含 `workspace_execution_decision` 和 `done`。
5. 发送显式 memory 指令。
6. 重新获取 detail，确认 Memory Context 有新增项。
7. 如果本地环境允许，触发 evidence run；否则跳过并输出 skip reason。
8. 查询 runtime sources 和 artifact latest version provenance。

Live smoke 失败时记录：

- 请求 URL 和响应状态。
- 最后一个 SSE event。
- workspace id、run id、chat session id。
- backend 日志关键字：`workspace_conversation`、`context_checkpoint`、`workspace_evidence_run`。
- ML 日志关键字：`workspace_agent`、`context_guard_trimmed`、`workspace_evidence_run_service`。

## CI 建议

默认 CI 只跑离线契约测试：

- backend pytest target
- ML pytest target
- Web Vitest target

Live smoke 和未来 Playwright E2E 用独立 job，必须显式环境变量开启，且失败先作为 non-blocking 信号观察一段时间。

## 不做的事

第一阶段不做：

- 不引入默认 Playwright E2E。
- 不依赖真实 LLM 或外部搜索。
- 不新增 DB migration。
- 不把 runtime references 写入长期 `workspace_sources`。
- 不让前端直接写 Workspace Memory。

## 完成标准

第一阶段完成时，应能回答：

- Workspace live conversation 的 chat/evidence 分流是否稳定。
- 长对话是否能生成并续接 context checkpoint。
- Workspace Memory 是否能通过 contract 写回。
- evidence result 是否能投影为 runtime references 和 artifact provenance。
- Web 是否能消费这些状态，并在刷新后恢复。

