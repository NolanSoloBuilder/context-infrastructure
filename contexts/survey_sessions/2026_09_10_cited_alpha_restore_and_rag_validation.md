# Cited Alpha 恢复与 RAG 验证记录

日期：2026-09-10（Asia/Shanghai）。当前任务尚未完成线上业务验收。

## 目标与任务归属

用户要求恢复 Google Cloud 上的完整应用，然后优化并验证最终使用结果。
验收路径：登录 → 创建研究 → 生成带来源报告 → 打开引用原文 → 刷新后恢复产物 → 追问/重试。

用户明确确认沿用三个原工作目录的 `feat_codex/financial-report-agent-plan-writer-20260717` 分支，保留原有未提交改动：

- Web：`/Users/xuhao/Documents/Other/mindspace_web_frontend`，HEAD `174e6c737fd94254bea0dfd4439be0b98fbd247b`。
- Backend：`/Users/xuhao/Documents/Other/mindspace_backend`，HEAD `420d5c9e5673489b6fafab9874d3020893b7651f`。
- ML：`/Users/xuhao/Documents/Other/mindspace_ml_backend`，HEAD `b17469f13d77ccf3e500fc48a36c1cc40419240e`。

## 云端取证

项目 `cited-alpha-20260701`、区域 `us-central1`。

- 结算审计：2026-08-04 11:28:03 UTC `DisableResourceBilling`；2026-09-10 07:19:49 UTC `AssignResourceToBillingAccount`。
- 用户确认自己曾关闭结算、刚重新关联。CLI 确認项目 `billingEnabled=true`、结算账户 `open=true`；控制台确认有可用赠金。
- 主库 `cited-alpha-mysql` 最初 `SUSPENDED / BILLING_ISSUE`，activation policy 已是 `ALWAYS`。
- 尝试 `gcloud sql instances patch ... --activation-policy=ALWAYS --quiet`，返回 HTTP 409，未恢复实例。
- Google 官方说明结算问题解决后，Cloud SQL 可能需要数小时恢复：[Cloud SQL suspended state](https://docs.cloud.google.com/sql/docs/mysql/diagnose-issues#suspended_state)。不通过反复关闭/开启结算、重建主库规避控制面状态。
- SQL 所需 `sqladmin.googleapis.com` 和 `sql-component.googleapis.com` 已启用。
- Cloud Tasks `workspace-runs` RUNNING，Scheduler `workspace-run-outbox-dispatch` ENABLED。
- Web `/app/login` 与 API echo health 返回 200。Chrome 进入 `/app/deepwork`，创建入口禁用；这不能算完整登录或功能验收通过。
- API 日志见 `/api/v1/m/user/profile` 403、token refresh 请求；Cloud SQL connect 日志明确未处于 EXPECTED_RUNNING。HTTP 200 echo/outbox 不能当作数据库健康证明。

### 当前运行版本

| 服务 | Ready revision | 流量 |
|---|---|---|
| cited-alpha-api | cited-alpha-api-00045-qgz | 100% |
| cited-alpha-workspace-runner | cited-alpha-workspace-runner-00021-8sj | 100% |
| cited-alpha-ml-api | cited-alpha-ml-api-00041-g78 | 100% |
| cited-alpha-ml-runner | cited-alpha-ml-runner-00021-vfr | 100% |

Backend 镜像 source SHA `57bd5d2fa3364e67f8d1cac5ff47c5c6a5c58bdc`，Actions run `29573333238`。
ML 镜像 source SHA `249f31b85e9c5a430deb116e482be90490019f67`，Actions run `29572962179`。

ML API 禁止模型调用；私有 ML runner 允许模型调用，但 embedding/ASR/image 仍禁用，MongoDB 连接禁用。未改变这些门禁。源码存在 document-store 并不表示该路径已在当前生产启用；主库恢复后需按实际研究路径验收。

## 本次本地检索优化

修改仅位于 ML service/document_store 层及其离线测试；原 dirty agent/source-content 等文件未覆盖。

1. `hybrid_retrieval_merger.py` 从语义优先追加改为等权 RRF (`k=60`)。按每路不同 chunk 排名，重复 cell/span 只贡献一次排名票数，同时保留全部命中定位信息。平分保留首次出现顺序。
2. `document_search_service.py` 分离候选预算与最终返回数：每路 `min(100, max(20, 3*top_k))`。权威正文回填与 owner 过滤后截取最终结果。
3. 候选全部失效或无权限时，也尝试原有显式 document_id 范围内的 Postgres 文本兜底；继续检查 owner。没有扩大成全库兜底。
4. 更新模块 README；补充精确词召回、重复候选不重复计票、失效/无权限候选兜底测试。
5. 原页面读取 fake 缺少已有的 `target_table_ids/target_cell_ids` 参数，顺带同步 mock 签名，生产 page reader 未修改。

验证：

```bash
.venv/bin/python -m pytest tests/test_document_store_search_service.py tests/test_document_store_agent_tools.py tests/test_document_reference_resolution_service.py -q
```

结果：35 passed。`git diff --check` 通过。

客户端边界：Web 通过 workspace-scoped document reference resolve/source-html/source-file；移动端 Agent 使用既有 document reference 类型。未更改路由、请求字段、引用结构或鉴权合同；新增 retrieval 排名诊断字段。这里是离线契约验证，尚未证明真实语料召回率/延迟改善。

修改清单：
- `mindspace/service/document_store/hybrid_retrieval_merger.py`
- `mindspace/service/document_store/document_search_service.py`
- `mindspace/service/document_store/README.md`
- `tests/test_document_store_search_service.py`

ML 修改已提交 `906720d`，PR #30 合入 main `061d27c7c7ed39bac92f674a0261e7db1e086aa1`。Actions `34453214456` 正在部署；上表为恢复时版本快照。

## 待完成的线上验收

1. SQL 回到 RUNNABLE，确认数据库连接和业务读请求成功。
2. 检查当前登录态；必要时重新登录，再确认资料和历史 workspace 能加载。
3. 按部署门禁做无模型健康 smoke，再用一个有边界的真实研究任务验收。
4. 检查队列交付、SSE、终态、产物保存、刷新恢复、引用原文打开及后续追问。
5. 以真实任务的失败点决定进一步优化。新增检索代码经目标分支 PR/main/Actions 发布后，回读实际 SHA、流量与效果；不能直接把含大量其他修改的 dirty 工作目录部署出去。

## 恢复进展（实时补充）

- 15:29:50 开始的 Cloud SQL UPDATE 操作 `0d0b3746-162d-4fb1-93ff-10b100000032` 于 **15:36:20** 完成（DONE，无 error），实例恢复 RUNNABLE。
- 等待命令返回过超时，表示55秒轮次结束，不代表该云端操作失败。
- Chrome 旧 token 失效后，通过已有 Google 账号重新登录成功，用户名称与历史 Deep Work 列表恢复，创建输入框可用。
- ML API 首次健康请求500，日志显示 AUTOSCALING 冷启动且无可用实例；后续 `/nash-algorithms-docs` 返回200（3.2秒）。没有为此修改镜像或扩容配置。
- 已填写单项真实验收任务：仅核对 Tesla 2024 财年总营收，要求官方10-K、期间/币种/单位、可打开的引用，避免扩展研究。
- 已 fetch ML `origin/main`，当前任务 HEAD 被 main 包含（main多9个merge commit）；本次两个运行时代码文件在 HEAD 与 main 无差异，待修复合入时无需把其他 dirty 改动一起发布。

## 首次真实业务验收与修复

- 工作区 `workspace-dd47f68c-df1a-4a3c-80ca-a40c6d9cf6f5`；Run `workspace-run-65148178-0f30-4d30-9ca1-83f5cfbe5617`。
- 15:39:27 创建，15:47:35 失败，未生成报告版本。数据库只读查询与 ML 日志共同确认：`snapshot.table must include at least 2 rows and 3 columns when runPlan requires comparison_table`。
- 默认 V2 investment profile 将 comparison_table、valuation、scenario 等完整模板要求合并进单指标任务，生成器遵守短任务时与表格校验冲突。不能通过编造表格或关闭事实校验解决。
- 检索有19个引用，Chrome 历史展示的样本包含2026 SEC文件和无关汽车新闻，未形成2024官方年报证据闭环。
- SSE 约300秒结束后页面误显示完成；数据库当时仍 running。刷新又只读取一次，后台终态不自动更新。
- Web 提交 `4a869f1`，PR #27：SSE 结束后观察原 Run，回放已持久化结果；刷新后只读轮询原 Run，终态刷新详情/历史，保留文档草稿，切换工作区忽略旧响应。干净提交快照96项测试及Vite构建通过。
- Backend 提交 `9f41836`，PR #35：只增加本次验收 workspace 到现有V3 allowlist，全局比例保持0，旧Run重试仍继承V2，新消息才进入V3。main+本次配置的干净快照15项测试通过；原dirty目录三个证据维度测试失败，未纳入发布。
- 三仓已有未提交开发内容均保留；正式部署走独立PR/main/Actions，没有把dirty工作目录直接打包发布。
- Chrome 另确认历史 assistant 无条件标记完成；正在补充与关联 Run 状态一致的标签回归。

### 已上线的修复（16:11 回读）

- ML Actions `34453214456` success，source SHA `061d27c7c7ed39bac92f674a0261e7db1e086aa1`；`cited-alpha-ml-api-00042-c7w`、`cited-alpha-ml-runner-00022-tsp` 各100%流量。
- Web 第一轮 PR #27 Actions `34453288707` success；历史状态追加提交 `4758ebc` / PR #28，merge SHA `8333a28cee4a8d44525581e1c4872616cdb74bdf`，Actions `34453501833` success，Pages deployment `73fc9e3b`。历史页面标签在 Chrome 刷新后已从“已完成”变为“失败”。追加回归先2 failed，再页面65 passed。
- Backend PR #35 merge SHA `4203c60f2042810f0451d609054da58403868a4f`，Actions `34453286717` 正在执行迁移任务 `cited-alpha-api-schema-migrate-tkmwg`；截至回读尚未发布新API版本。
- 验收独立真值：SEC Tesla 2024 Form 10-K，Consolidated Statements of Operations 的 Total revenues 为97,690 million USD（2024年度），来源 https://www.sec.gov/Archives/edgar/data/1318605/000162828025003063/tsla-20241231.htm 。不得把该数字灌入被测任务来冒充自主检索成功。

### 后端发布与新版验收启动

Backend Actions `34453286717` success；API revision `cited-alpha-api-00046-ksh`、Workspace Runner `cited-alpha-workspace-runner-00022-zs8`，镜像均关联 main `4203c60f2042810f0451d609054da58403868a4f`，各100%流量。API/ML health 200，队列 RUNNING、Scheduler ENABLED。迁移执行 `tkmwg` 以及收尾任务 `glpdq` 经现有发布门禁完成。

16:19:44 从 Chrome 发起新的证据研究消息，Run `workspace-run-5ec2eb1e-16bc-46cd-9b0e-4269b76debc7`。只读数据库确认 harness_contract_version=v3、status=running；旧失败 Run 仍为v2。没有修改历史 Run 或直接写业务数据库。

## V3 内容质量验收发现：成本误作收入

V3 Run `workspace-run-5ec2eb1e-16bc-46cd-9b0e-4269b76debc7` 已生成并保存报告，引用可在Chrome原文查看器打开保留的SEC 2024年报（含 Total revenues / 2024 定位）。但报告同时将97,690和62,873 million USD均标为营收；后者原始行是 Total automotive cost of revenues。因此业务执行成功不等于内容质量通过，当前灰度不扩大。

根因：`workspace_dimension_claim_window._dimension_span_scope_is_allowed` 缺少成本限定词判断；从 revenue alias 开始截取后丢失 cost of，fallback 将成本数字提升为收入 Atom，Backend相同独立重算规则也接受。修复在裁剪前排除成本前/后缀，两侧保留正确年度/单位/原文定位合同。

- ML `f0a491c` / PR #31；Backend `d191191` / PR #36。每仓3文件：绑定模块、独立9项回归、README中本次追加段。README已有dirty内容使用单独patch暂存，未夹带既有开发改动。
- Backend干净快照25 passed。ML干净快照74 passed / 3 failed；未修改main为65 passed /相同3 failed（交付量局部窗口、重复多期数字、FSD定性证据），本次新增9项均通过。
- 两PR已按main发布流程合入，待部署后再生成新版本替换当前错误的验收报告。

## 后续 RAG 架构优先级（建议，尚未实现）

本次故障表明继续更换向量库不是首要矛盾。金融数值应优先利用 SEC Inline XBRL 的 concept/contextRef/unitRef 绑定主体、指标、期间和单位；表格行列定位保留为可打开的人工核验界面，文本别名仅作召回与受控降级。当前成本限定词修复是已复现漏洞的有界修正，不是完整会计指标分类器。

还应建立 entity+metric+period+unit+currency 的冲突检测：同一口径出现不同数值时，需要解释版本、重述或分部差异，不能直接生成两个“已验证”结论。报告展示应收敛为回答问题所需的内容，避免把原始Task、内部审核结构和同一事实多次重复给用户。验收集需覆盖历史年份、分部/集团、成本/收入、同比/绝对值、原币/换算、修订报表、缺证据和相互冲突的官方材料。上述均为建议，不计入本次已上线能力。

### 指标修复发布记录

ML PR #31 merge SHA `9a6c7e41d1943f4321a9e59f4e5eb65fecbb029d`，Actions `34455221982` success，ML API `cited-alpha-ml-api-00043-5lv` 与 ML Runner `cited-alpha-ml-runner-00023-9xq` 各100%流量。Backend PR #36 merge SHA `24b91fb869be48cd7020d5378043ab99ec2bcadf`，Actions `34455223187` 尚在收尾；主迁移 `9tdr2`、收尾 `jhmmg`。本轮迁移容器调度约4分47秒，发布时长明显高于有界代码修复本身。建议后续建立可审计迁移版本/校验和机制，减少无结构变更时重复执行全量迁移；这项发布流程优化尚未实施。

## 产物验收纠正（2026-09-10）

Backend 第二次部署 Actions 34455223187 成功，API cited-alpha-api-00047-nfj、Runner cited-alpha-workspace-runner-00023-rvm；source 24b91fb869be48cd7020d5378043ab99ec2bcadf。后续 Run workspace-run-0b62bde3-08be-4b4a-858a-0ea82dfa6771 与 workspace-run-bb45e0db-034f-411c-ad5a-ff6058f126ed 均 failed，无新 report_version_id；后者报 ReportDocument analysis contains an unbound factual token。不能记录最终报告验收通过，也不能确认仅生成一个任务。Chrome仍展示旧v1，包含先前错误结论。

用户明确要求从高标准报告产物出发，并根据用户请求选择多个内置模板。后续以 [报告产物标准与生成设计](2026_09_10_cited_alpha_report_product_standard.md) 为设计基准；基础设施恢复已完成，报告质量优化和线上验收尚未完成。
