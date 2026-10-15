# Cited Alpha 下一条真实业务 Run 集成审查

2026-09-11；只读源码审查，未运行新模型、未操作生产、未读取 secrets/database 配置内容。

## 结论

SEC-only 的下一条集成可以完全复用现有运行器，应用代码无必需修改。应把真实 API admission、WorkspaceRunTaskConsumer、ResearchRunExecutor、ResearchCallbackService、GCS CheckpointStore、真实 Pi/Vertex/SEC 和真实审阅串起来。只新增临时 composition harness，覆盖本地服务身份和固定 HTTP 目的地的传输；不能再复制 agent loop、计算、检查、存储或 delivery。

这能证明“本地真实 MySQL 业务 Run + 真实云端模型/GCS + 正常 report persistence”，不能声称验证了生产 OIDC/Cloud Tasks/生产发布。PDF 跨源另有依赖和注入缺口，见下。

## 已核对绑定

- Backend /Users/xuhao/Documents/Other/mindspace_backend，feat_codex/financial-report-agent-plan-writer-20260717，ca114683b50159f1584349f0fcd569614b6464e5。执行了 pwd/top-level/branch/HEAD/status/worktree；旧 dirty 保留。
- ML /Users/xuhao/Documents/Other/mindspace_ml_backend，同分支，4d778fb23f7c98890db49fde5072b649beb5dc9e。相同六项检查，旧 dirty 保留。
- 未读写 Web，本审查无需 Web 修改。遵循两仓 AGENTS 和 research_runtime/research_agent README。

以下路径以 Backend 或 ML 根目录为前缀。

## 精确调用链

1. Backend `mindspace/router/v1/workspace_router.py` 的 `POST /api/v1/workspaces/{workspace_id}/runs`：真实 JWT/UserDao、owner workspace。参考 `mindspace/script/research_mysql_api_smoke.py` 中真实 User/Chat/Workspace 创建，但问题、idempotency key、Run 必须新建；不得复用已终态 smoke Run。
2. `mindspace/service/research_runtime/admission.py:16` ResearchRunAdapter.create_run：冻结 question/asOf/target/limits；真实 DAO 原子创建 Run/Event/Outbox/初始 artifact。仅在 isolated workspace allowlist 开启。实例 limits 要在 admission 前注入，例如 64/128/1800，生产默认仍是 30/100/900。
3. `mindspace/service/workspace_run_task_consumer.py:35` WorkspaceRunTaskConsumer.consume：读取真实 outbox，核对 eventId/executionScope 后调用 host.execute_run。优先直接 consume 真实 outbox，保留队列语义；本地不需要造新 scheduler 或发真实 Cloud Tasks。API admission 的 `_attempt_run_dispatch` 可以暂时 hold，随后显式 consume 一次；必须标记 Cloud Tasks transport 未验证。
4. WorkspaceService 已在文件末尾 `compose_research_runtime(workspace_service)`，persisted research-v1 分发到 adapter.execute_run，再到 `research_runtime/executor.py:19` ResearchRunExecutor。
5. Executor 真实 claim Run/Step、heartbeat、原始 deadline、加载 checkpoint，调用 `MLResearchExecutionService.execute`（`service/ml_service/ml_research_execution_service.py`）。POST `/agent/v1/research/execute`，请求只一次。
6. ML `router/v1/research_execution_router.py` 真路由：DTO/大小校验、ResearchExecutionService、PiProcess；`service/research_agent/execution_service.py` 真 model/tool loop。
7. ML `ResearchCallbackClient` (`service/research_agent/callback_client.py`) 调用 Backend `/api/v1/workspaces/internal/research/{runId}/{checkpoint|calculate|check-draft}`。
8. Backend `router/v1/workspace_run_internal/research_router.py` 真路由 -> `ResearchCallbackService.dispatch` (`research_runtime/callback_service.py:21`)：真实 Run scope/lease/deadline/step/sequence，构造 CheckpointService、SourceIntegrity、CalculationService。
9. Checkpoint `research_runtime/checkpoint_store.py` 真 ADC/GCS immutable write/read；SQL checkpoint DAO 指针/CAS 真实。check-draft 调 `ResearchReportCheckAuthority` 真 SEC 原文回读 -> `MLResearchReviewService` -> ML `/agent/v1/research/review` -> ResearchBundleReviewer + ResearchReportReviewer 真模型。
10. ML 只回 compact status；Executor 从 GCS/DAO 加载 checkedCandidate，`checkpoints.deliver_checked` 真事务写版本/Run 终态/outbox，再 finalize_run_message。不要从 ML response 手写 artifact。

## 最小 harness 结构与依赖注入

建议两个独立 Python 进程，各用本仓 .venv 和 cwd。两仓包均叫 mindspace，不能在同一解释器通过 sys.path 拼装两个服务。

### Backend 进程

- 环境强断言 ENV_MODE=local，MySQL 127.0.0.1:13306/research_api_smoke，无 unix socket；读取已有私有 override 但不输出。旧 smoke 的全外网 socket 禁令不能原样复用，因为 GCS/SEC 要真实访问；改成明确目标/凭证约束，不改为默认 remote DB。
- 只挂真实 workspace public router、research_callback_router；若要测 run-task HTTP 可挂真实 workspace_run_internal_router。不要启动通用 app scheduler/email/旧工作队列。
- `store_factory=lambda: ResearchCheckpointStore(bucket='cited-alpha-workspace-source-snapshots')`，不传 DiskObjectTransport；Executor 与 CallbackService 必须使用同一 bucket。
- `source_factory`: 真 ResearchSourceIntegrityService(sec_reader=SecResearchSnapshotReader(bucket=相同原文 bucket))，无 FakeAuthority。
- `ml_executor=MLResearchExecutionService(connection=LocalConnection)`；LocalConnection 只有固定 loopback ML `_base_url` 和 `_internal_authorization_headers`。这是本地 service credential 注入，不是生产 Google 身份。
- `reviewer_factory=lambda **scope: MLResearchReviewService(**scope, connection=LocalConnection)`；Executor 和 CallbackService 均注入一致 reviewer。保留 HTTP payload/scope/hash 校验。
- 用现成 `ResearchRunExecutor(host, ml_executor=...,store_factory=...,source_factory=...,reviewer_factory=...)` 构造；用 ResearchRunAdapter(host,executor=executor,limits=...) 替换本进程 host._research_run_adapter。
- FastAPI dependency_override `research_router.callback_service` 返回真实 ResearchCallbackService(dao=host._dao, execution_scope=host.run_execution_scope, 同 factories)。不要 override dispatch 的结果。
- override `require_workspace_internal_service_identity` 为严格检查本次随机本地 token 的 dependency；拒绝错误/缺失 token。仅这个本地 app 内生效，绝不修改生产 verifier。

### ML 进程

- 最小 FastAPI app 只挂 research_execution_router/research_review_router，prefix=/agent；隔离/禁用 ML MySQL、Postgres/Mongo，不让 import 沿用 remote DB。SEC-only 路径本身不需要 document store。
- override execution router `runtime_settings` 返回 enabled 且绝对 Pi node/module/entrypoint 路径的 ResearchRuntimeSettings。
- **callback settings 不能直接配 http://127.0.0.1:port**：resolve_research_runtime 强制 HTTPS 443。不要放松规则。
- 可用现有 `callback_factory` 注入真实 ResearchCallbackClient(settings,scope,callback_context,token_provider=local_token,http_client_factory=...)。http_client_factory 使用仅允许一个虚拟 HTTPS authority 的 harness AsyncBaseTransport，将该 authority 的实际网络连接投送固定 loopback Backend HTTP 端口；任何别的 host/path、重定向不允许。或者起本地 HTTPS/443 并装显式测试 CA；前者配置更少。必须清楚标记 TLS/OIDC 未验证，不能把本地投送视为真实 HTTPS。
- transport 只转发 bytes，绝不生成业务成功响应。这样保留实际 callback client 的 8 MiB、scope、序列、一次发送和错误 fatal 行为。
- execution_factory 可保留默认 ResearchExecutionService；若需10轮同等 pacing/审计，用 factory 注入真实 ResearchModelGateway 的包装器，不能复制 run 方法。reviewer_factory 可注入带相同审计/总调用上限的真 reviewer；review route 默认每请求 max_calls=1 并不限制跨请求总次数。
- override ML require_internal_service_identity 为相同严格本地 token dependency。不要全局 `lambda: object()` 无鉴权。
- Vertex 仍通过已登记场景 agent_deep_research/workspace_report_semantic_verifier 和显式 process override；SEC client/capture 保留真默认服务和私有 bucket。

## 需要改应用代码吗

SEC-only：本次源码未发现必需应用修改；所有关键依赖已有注入点。新增文件只应是本地 composition/启动/验收脚本，不能把临时 bridge 写进生产安全 client。生产端最终必须另验真实 OIDC、队列及 deployed image。

PDF 跨源：
- Executor 已有 document_client 注入，DocumentSourceReader 本身有 client 参数。
- **CallbackService 当前内部硬构造 ResearchDocumentSourceReader(...)，未暴露 document client/reader factory。** SEC-only 不受影响。完整本地 PDF 验证可优先让 MLWorkspaceService 的现有本地配置/auth 指到同一 ML 进程，从而默认 DocumentService 也走正确地址；若配置不能覆盖，建议窄化增加 document_reader_factory/document_client 注入，而不要 monkeypatch source verifier 或移除授权检查。
- 需要真实 owner document/file-library/workspace attachment，以及 ML Document store 的真实隔离记录；以前手动 local-canary version scope 不等于这次 user/workspace/document/fileId，不能直接嫁接。
- 36页实际 parse 可在正确 owner scope 下验证/保留已有 provider artifacts 后建立版本，是否能合法复用必须按 DocumentVersionService scope 合同核对；不要重新付费 parse 只为造 smoke 资料。
- Backend 源校验仍禁止 Document numeric normalization，所以 PDF 目前能做带定位的证据/对照，不可擅自声明参与 typed financial calculation。

## 可执行下一步与验收

1. 先只实现两个临时 app composition 和 bounded launcher；打印可公开版本、环境 target、PID、随机运行 ID，不打印 token/secret/thought signature。
2. 零模型 preflight：两个 listener loopback only；错误 token 401/403；真实 JWT workspace GET；固定 callback test 用不存在 Run 返回409；不得拿 live Run 做未知副作用试探。确认 GCS bucket与 ADC project，不写生产业务 SQL。
3. root 的 report10产物判定后才开新 paid integration，避免并行模型成本；在新 Workspace 使用实际研究问题，admission 冻结预算与截止时间。真实 outbox consumer 调一次。把 request/run/event/outbox/pointer/version ID 记录到私有 audit 文件。
4. 实时只输出 Run 状态、模型/工具数、checkpoint sequence/bytes，回读真实 MySQL pointer；在独立服务实例读 GCS 校验恢复。总调用SDK上限、审阅上限、原截止时间放 harness 审计，不篡改 Run 的 frozen limits。
5. 成功必须同时满足：Run succeeded；checkedCandidate 与 persisted artifact bundle hash一致；check receipt绑定；artifact version从V1到V2且只一次；正常 JWT artifact/citation API可读；另一真实用户 JWT 被拒；重复消费同一 outbox 不产生第二版本/模型调用。
6. 用真实 Web 指向此 local API，真实登录身份打开刚创建的 Workspace，页面看报告和引用。不用拦截伪造 report HTTP。若现有 Web 登录态不能接入本地 JWT，要独立解决本地 login setup；不能把组件 fixture展示算业务闭环。
7. 故障/恢复需另一个有界案例：先做“已有 checkedCandidate 后重新 Executor 无模型交付”真实状态恢复；不要为演示随意 kill 正在付费 tool 的进程造成 unknown effect。是否重用10 checkpoint须遵守 user/workspace/run scope，默认不能迁移。

## 仍未覆盖/风险

- default limits 30/100/900 与已观察长报告成本不匹配。通过 admission 前 harness limits 注入能验证64/128/1800；不代表生产预算产品方案已确定。
- GCS checkpoint 每事件全量immutable保存会增加时延和对象数；当前8 MiB max需要在长报告真实读取 bytes 验证，不靠估计。
- Callback HTTP120秒、review HTTP95秒、总Rundeadline共同限制，一次review的source回读+模型可能接近上限；若实测超时，先定位哪个边界，不要一概放大所有timeout。
- endpoint返回 incomplete 会使真实 Run failed；不能沿用scratch resume方式偷偷把failed Run当running。业务retry产生新Run；unknown provider intent必须按现有规则处理。
- 本文只有源码审查与入口设计，未宣称这条链已执行通过。
