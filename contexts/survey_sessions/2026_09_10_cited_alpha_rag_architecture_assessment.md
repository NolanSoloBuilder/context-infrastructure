# Cited Alpha RAG 架构评估

日期：2026-09-10。范围：当前本地 Web、业务 Backend、ML Backend 的产品文档、接口、检索/解析/证据模块及纯函数复现。没有改动产品代码，没有调用收费模型、生产数据库或索引服务，没有验证线上部署与质量指标。

## 结论

Cited Alpha 已有相当完整的领域 RAG 与 Agent 工作流代码，不是等待接一个向量库的空白项目。建议保留现有 Workspace、证据引用、文档存储和工具合同，优先改进检索融合与检索评测，再依据数字事实场景增强证据验证。不建议整套迁入 RAGFlow、Dify、Haystack 或 LightRAG。

此前推荐 RAGFlow 用于体验、Haystack 用于学习，是面向新实验的建议；查看 Cited Alpha 后，推荐应调整为现有架构的增量演进。开源组件可作为独立对照或适配器，不能为了采用框架重建产品已有状态机。

## 1. 评估基线

本地三个仓库均处于 `feat_codex/financial-report-agent-plan-writer-20260717`，且有未提交改动；下面只记录读取时快照，不将当前分支绑定为实施分支。

| 仓库 | HEAD | status --short 行数 |
|---|---|---:|
| mindspace_web_frontend | 174e6c737fd94254bea0dfd4439be0b98fbd247b | 68 |
| mindspace_backend | 420d5c9e5673489b6fafab9874d3020893b7651f | 33 |
| mindspace_ml_backend | b17469f13d77ccf3e500fc48a36c1cc40419240e | 31 |

因此本报告结论属于当前工作树代码观察，不是已上线事实。公开站读取工具本轮未成功打开；产品定位以本地前端 README、site.config.json、public/llms.txt 和相关研究文档交叉确认。项目内 2026-07-13 Harness 完成度审计包含历史生产验收记录，但本轮不把其视为当前生产验证。

Cited Alpha 主产品在 `/Users/xuhao/Documents/Other/mindspace_web_frontend` 等三仓。`adhoc_jobs/cited_alpha_lead_pipeline` 是联系人采集配套工具，与研究 RAG 主链路不同。

## 2. 业务要求决定 RAG 形态

现有产品是 source-backed research / Deep Work：从选定来源形成带引用、可复查、可跨期续接的研究 memo。主要检索单位不只是相似段落，还包括文档、页、行、表格、单元格与原文 span。

适合的架构是“Agent 管研究问题与缺口，检索服务获取精确证据，确定性代码负责口径和引用约束”。例如比较某公司两个期间的同一指标：先定位公司/文档/期间，查正文和表格，读取行列与单位，计算变化，最后写结论。不能把多个年份数字堆给生成器就认为完成。

## 3. 已有链路

### 长期文档库

代码描述：Document AI Layout Parser → normalized document/page/chunk/line/table/cell/span → AlloyDB 文档真源；目录和 chunk embedding → Vertex Vector Search；词面与结构记录 → OpenSearch；查询返回候选 ID 后回读 AlloyDB 原文。另有 PostgreSQL 文本 fallback。

关键文件（均相对 ML 仓库）：

- `mindspace/service/document_ai/layout_ingestion_service.py:35`：Layout Parser 调用、parse_run_id、sha256、parser_version、结果落库。
- `mindspace/service/document_store/chunk_embedding_payload_builder.py:23`：embedding 输入包含标题、来源、文档类型、页范围、章节路径与原文。
- `mindspace/service/document_store/document_catalog_search_service.py:47`：先按目录文档级 embedding 找文档并回读元数据。
- `mindspace/service/document_store/document_search_service.py:47`：向量、词面、回读上下文与可见性过滤。
- `mindspace/repository/document_store_opensearch_repository.py:90`：词项、短语、数字字符串查询入口。
- `mindspace/service/agent/document_store_tools.py:54/92/141`：目录搜索、内容搜索、精确读页的 Agent 工具。
- `mindspace/service/agent/workspace_document_source_preflight_runner.py`：Workspace 预检实际调用文档工具，不只是工具注册。

### 平台信源与外网

Source Discovery 有独立 Volcengine 检索、multi-query/RRF、constraint rerank 与 optimizer loop；不要把这一条链路的 RRF 当成 document_store 的实现。外部原文抓取模块做 bounded HTML/PDF 提取和原文片段匹配，部分路径与完整 Layout Parser 文档入库并不相同。

- `mindspace/service/source_discovery/retrieval/volcengine/README.md`
- `mindspace/service/source_content/original_source_document.py:24`：600000 字符、4000 块、80 页 PDF 等界限。

### 证据与产品层

已有 prepare/retrieval checkpoint、生成后处理、引用可用性判定、字段来源修剪、coverage reviewer 和严格覆盖门禁。Backend 保存 Workspace/Run/Artifact 及 evidence ledger，Web 有文档引用 resolve/source-html/source-file 消费接口。

- ML `workspace_evidence_run_service.py:139` 与 `workspace_evidence_reference_contract.py:1`
- ML `workspace_evidence_coverage_reviewer.py:129` 与 `workspace_evidence_coverage_gate.py:46`
- Backend `mindspace/service/workspace_evidence_ledger_service.py`
- Web `src/app/services/workspaces.ts:1185`

已有这些模块不证明每项业务评测通过，但足以说明整套平台替换会重建大量与产品价值相关的工作。

## 4. 按十环节评估

| 环节 | 当前代码观察 | 推荐 |
|---|---|---|
| Parsing | Layout Parser 适配器；外部原文另有 BeautifulSoup/pypdf 路径 | 保留；用财报表格、扫描和长文样本对照解析质量 |
| Chunking | 文档层级、chunk、页行表格与 span 可回读 | 重点评测表头、单位、脚注、跨页条件有没有随证据返回 |
| Embedding | 标题/章节/页码/类型加原文；文档级与块级两种索引 | 不先换模型；先分清目录召回失败还是块召回失败 |
| BM25/词面 | OpenSearch 词面通路已有 | 让精确命中在融合后确实获得展示机会 |
| Hybrid | 两路均调用，但文档库合并偏向语义原顺序 | 首要修复候选融合与最终截断策略 |
| RRF | 平台信源有相关模块；文档库当前 merger 不执行 RRF | 文档库做 RRF/归一化融合对照，不跨链路推断 |
| Rerank | 文档 search→format 链路未见 cross-encoder 重排；其他路径有约束排序 | 仅在独立测试集显示收益后接入模型重排 |
| Context assembly | 原文回读、页/表/单元格、source refs 已有 | 强化相同主体、时间口径、单位与列头组成完整证据 |
| Generation | Agent task service 与 Workspace bridge 已有 | 保留，约束输出的每个事实/计算来源 |
| Verification | 引用合同、字段溯源、覆盖评审与 gate 已有 | 不把 coverage 当逐项事实证明；增加数值口径和来源支持的独立验收 |

## 5. 优先级最高的具体发现

### P0：词面独有命中可能被最终 top_k 挤掉

`hybrid_retrieval_merger.py:29` 先加入所有向量候选，`46` 行附近再追加词面独有候选；同块仅补词面 metadata，不改变其排名。`document_search_service.py:137` 达到 result_limit 就停止返回。

本轮直接加载真实 merger 纯函数，以合成 ID 做无网络复现：

```text
vector = [semantic_0, semantic_1, semantic_2]
lexical = [exact_metric(score=99)]
merged = [semantic_0, semantic_1, semantic_2, exact_metric]
final_top_3 = [semantic_0, semantic_1, semantic_2]
```

在前三个语义候选均可见、可回读的条件下，词面唯一找到的精确指标会被截掉。该复现证明排序/截断机制，不证明生产中具体某题已错，也不证明 exact_metric 在真实语料一定正确。

建议独立设置每路候选预算与最终证据预算，先合并排名，再统一截断。RRF 可先在应用层跨 Vertex/OpenSearch 做，不必先更换存储；对照归一化加权、RRF、融合加 reranker。OpenSearch 官方也区分分数融合与基于名次的 RRF：[官方说明](https://docs.opensearch.org/latest/vector-search/ai-search/hybrid-search/index/)。

### P1：后置权限过滤可能造成少返回或空返回

当前 search 在向量/词面取 top_k 后回读并过滤可见上下文。PostgreSQL fallback 只在初始 chunk_ids 为空时触发。因此候选存在但随后全部被过滤/无法回读时，不会进入该 fallback。这里讨论召回完整性，不断言权限泄漏。

建议能前置的 scope 进入两路索引过滤，原文层继续做最终授权，并加受限 over-fetch/补召回；旧索引孤儿和越权候选分别记录原因。

### P1：覆盖评审不能替代原文事实验证

`workspace_evidence_coverage_prompt.py:29` 构造的 prompt 包含目标、问题、block 摘要、sourceBackedFindings 和 referenceIds，未把完整原文材料包作为该 reviewer 的输入。它适合判断问题有没有覆盖，不能独立证明财务数字/因果结论被原文支持。其他链路已有来源校验，不能据此说整个系统完全没有验证。

建议数字结论形成 typed fact：entity、metric、value、unit/currency、period、reported_or_derived、source span；派生值保存操作和输入证据。对于“同比”检查期间与口径，计算由确定性代码执行。暂无法证明的因果关系明确保持假设。

### P2：不同来源路径的证据粒度与截断需要统一暴露

原文快取与完整解析各有用途，但 80 页限制、字符/块限制等应进入返回元数据，避免把“本次没读到”推成“文档没有”。需要统一 EvidenceHit 对外合同，保留各 provider 的能力差异，不要求把所有来源迁入同一索引。

## 6. 推荐方案

保留现有 Web/Backend/ML 边界与研究状态机。文档真源继续承载原文和定位；检索索引只提供候选；Agent 调用 search/read 与专门的事实/计算工具；产物保持现有引用和版本合同。

推荐的文档 search 内部顺序：

```text
目标公司/文档/期间与访问范围
 → Vertex 向量 + OpenSearch 词面（各有候选预算）
 → 去重、RRF 或分数融合
 → 原文回读与授权确认、候选不足时有界补充
 → 可选 reranker
 → 精确页/行/表/单元格上下文
 → 带 locator 的 evidence hits
```

检索计划与补读由现有 Agent/预检层控制。热点新闻使用既有信源链路；只把经确认且需长期复用的资料纳入版本化真源，不把所有临时外网结果无差别灌进永久向量库。

## 7. 开源方案取舍

| 方案 | 对 Cited Alpha 的判断 |
|---|---|
| RAGFlow | 用作独立文档解析/检索对照；整体替换会迁移已有定位、上传作用域、引用与工作区合同 |
| Dify | 可用于外围快速工作流实验；不建议接管现有 durable run、Artifact 版本和证据账本 |
| Haystack / LlamaIndex | 可用于隔离的 retriever/评测原型，或逐个适配组件；不建议仅为框架统一而改写已存在的 Agent |
| LightRAG | 只有明确需要跨公司/供应链/事件关系查询且普通检索失败时实验；不是当前精确财务证据问题的优先修复 |
| OpenSearch | 现有系统已集成词面检索；优先提升融合效果。未来能否兼管向量，应以现有版本、成本、并发和评测为依据 |
| Docling / 其他解析器 | 可以作为已有 Layout Parser 的可替换对照候选；本轮不做能力或成本排名 |

这套代码目前使用托管服务的适配器。用户尚未要求完全去云或全部自托管，因此不主动开展存储/模型迁移。若全开源自托管成为明确目标，需另列 Document AI、Vertex、AlloyDB 等替换与迁移验收，而不仅换一个 RAG 框架名。

## 8. 可执行验收顺序

先选约 40 个代表问题作为诊断起点（不是统计充分性声明）：精确财务指标、同指标跨年、表头与单位、脚注例外、跨文件对照、无答案/旧版本/无权限。每题人工标注所需原文 span、表格 cell 与可接受结论。

固定语料快照、模型、查询预算，对比：现状；仅词面；仅向量；RRF；RRF+reranker。记录 required-evidence recall、排名、最终证据保留率、错公司/期间/单位次数、引用定位成功率、答案支持率、补读次数、P50/P95 与每题成本。

先完成无模型的融合机制修复验证；再跑检索与生成的独立测试。人工 gold evidence 交给生成器仍答错时，优先修验证与表达，不换向量库。

成功标准应围绕具体错误减少和证据可追溯，不用“接上了框架”“返回更多引用”当验收。正式实施前需用户确认需求分支/worktree，因为三仓当前有大量其他修改；本轮没有切分支、提交或更改产品代码。
