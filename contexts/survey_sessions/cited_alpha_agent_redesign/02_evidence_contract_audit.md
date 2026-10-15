# 证据与通用 Agent 接入审查

> 版本说明：本文保留最初代码审查与候选接口。后文 Markdown marker、`save_report` 和 POST resolve 示例属于历史建议，不是当前已实现合同。当前实现采用段落 AST、`submit_report` 和 GET research-citations；权威实现差异及下一步设计见 [报告交付实现设计](09_report_delivery_design.md)。不要同时实现两套正文或引用接口。

2026-09-10。范围：当前本地 ML Backend、Backend；两仓均为 `feat_codex/financial-report-agent-plan-writer-20260717`。只读审查运行代码，未调用模型、未部署、未执行数据库写入。本文保护 service/provider、router、DAO 之间的职责边界。

## 结论

检索、精读与原文查看可以复用；现有证据写入和报告交付合同需要分离。把通用 Agent 的输出接到原有 finalize，会重新引入 Task/Need/维度矩阵/Writer 审计等固定流程，无法实现用户要求的简化。

第一批建议抽出薄工具适配层：发现资料、检索、精读、字段引用、计算、交付报告。Agent 自由选择调用顺序，服务负责身份、原文版本、字段定位和持久化。工具只接受证据 ID 等受控标识，引用地址、存储路径、权限由宿主补入。

## 现有能力与确切接入点

以下路径以对应仓库为根；观察的是本地实现，不能自动当作线上启用证明。

| 能力 | 文件与函数 | 复用方式及边界 |
| --- | --- | --- |
| 文档目录搜索 | ML `mindspace/service/agent/document_store_tools.py:search_document_catalog_tool` | 下沉调用 catalog service；用于找文档，不用于直接回答数值 |
| 混合检索 | ML `mindspace/service/document_store/document_search_service.py:DocumentSearchService.search` | 词面与向量候选经 RRF，数据库回填、owner 过滤后截断；显式传 `viewer_user_id` |
| 原文页精读 | 同上 `DocumentSearchService.read_page`；工具层 `read_document_store_page_tool` | 带分页读取 line/table/cell，返回真实存储内容；复制上传文档范围校验 |
| 检索引用构建 | ML `mindspace/service/agent/document_store_reference_builder.py:build_document_store_references`、`build_document_store_page_reference` | 保留服务生成 locator；不让模型重新生成地址/坐标 |
| PDF/文档定位 | ML `mindspace/service/document_store/reference_resolution_service.py:DocumentReferenceResolutionService.resolve_reference` | 先精确 bbox/span/cell；缺失页只在同文档中有界修复，不可猜页 |
| SEC 官方资料获取 | ML `mindspace/service/integrations/sec_edgar/client.py:HttpSecEdgarClient`，`parsing.py:resolve_company/select_filings` | 复用官方域名、CIK/accession、安全重定向、大小/重试限制；支持特定历史期，不能默认最新替代用户年份 |
| 原文不可变保存 | ML `mindspace/service/integrations/sec_edgar/snapshot_capture.py:SecEdgarSnapshotCaptureService.capture` | bytes SHA-256 + GCS 条件写入；失败明确 restricted，不能声称全文已保存 |
| 原文分块 | ML `mindspace/service/source_content/original_source_document.py:extract_source_blocks` | 保留表头、年份、单位的独立结构上下文；此文件当前有原有未提交改动，复用前检查发布基线 |
| 现有快照验真 | Backend `mindspace/service/workspace_source_snapshot_object_service.py:WorkspaceSourceSnapshotObjectService.verify` | 重读 bytes/hash/有界表格和 PDF 验证；当前 retained 路径明确限制 SEC，扩展前需 provider registry |
| 引用查看 | Backend `mindspace/service/workspace_citation_reference_service.py:WorkspaceCitationReferenceService.resolve/fetch_source_html/fetch_source_file` | 当前需 Link→Claim→Evidence→Snapshot→Receipt 完整链及 owner 验证；可复用渲染服务，不能跳过链直接接受模型 reference |
| Evidence 查看 | Backend `mindspace/service/workspace_evidence_citation_service.py:resolve/resolve_claim_link` | 有界输出，重新验证持久化事实与归属 |
| API 数据工具 | ML `mindspace/service/agent/financial_datasets_tool_helpers.py:provider_result` | 当前仅返回 provider/endpoint/query/compacted data；没有本层生成的 immutable response ID 与 JSON Pointer |

LangChain `@tool` 不是必要依赖。Pi 适配器可以调用受鉴权的内部 HTTP service，再由 Python service 调上述实现。不能从 Node 进程假设 Python ContextVar 已自动携带用户身份。

## 定位合同的真实覆盖

`document_store_reference_builder.py:_build_chunk_locator` 已支持 document/chunk/page/line/span/table/cell，含 bbox、row/col header、numeric value、unit、currency、period。多命中时保留真实匹配坐标，不能仅保留 chunk ID。

Backend `workspace_citation_reference_contract.py:_LOCATOR_KEYS` 已允许大量 PDF、HTML、sheet/cellRange、时间与表格字段，但需要注意：允许字段不证明相应 parser、持久化和 viewer 全链路可用。当前白名单没有 JSON Pointer；`unit/currency` 也不能依赖 locator 的透传，应在 Evidence 口径字段保存并在 viewer 中显示。

| 信源 | 最小有效定位 | 本次审查结论 |
| --- | --- | --- |
| SEC HTML | snapshot hash + visible table/row/period column 或 block/quote | 有完整获取/保存/验证基础 |
| PDF | immutable document + page + bbox/span/cell | 有工具与 viewer 基础；具体上传解析链仍需真实验收 |
| 普通网页 | bytes snapshot + parser version + block/字符范围 +逐字 quote | 原文 parser 可复用；通用 retained capture 及 Backend provider 验真需补 |
| XLSX/CSV | 原始文件版本 + sheet/range + header/unit | locator 字段存在；Office 转 PDF 的预览不能单独证明原 Excel 字段定位完成 |
| 数据 API | response snapshot hash + JSON Pointer + request scope/as-of | 当前 Financial Datasets 工具缺持久字段证据合同，需补 |
| 派生数字 | calculation ID + inputs evidence IDs + formula/单位转换/精度 | ORM 预留 derivation，但现有 factual Claim validator 明确禁止 derivation；需新计算记录通路 |

## 旧合同中必须解除的耦合

1. `workspace_evidence_ledger_service.py:persist_retrieval_ledger` 强制 plannerSnapshot、成功 retrieval、effective Profile、Task/Need/coverage 重算。研究中发现的新事实不能自然地随工具结果入账。
2. `workspace_report_claim_contract.py:verify_report_claims` 要求一条 Claim 恰好绑定一个 Evidence、固定 key-facts/block、无 rationale/span，并拒绝 derivation。无法直接表示多证据综合分析、自然段内引用和派生值。
3. `workspace_report_delivery_verifier.py:verify_workspace_report_delivery_authority` 强制冻结 Task v3、Writer audit、三 Gate。直接调用会把旧编排重新带入通用运行器。
4. `workspace_source_snapshot_object_service.py:verify` 将 retained adapter、capture schema、license 与 SEC 绑定。多信源应新增明确 provider 验证适配器，不能简单删除 allowlist。

可保留底层 owner-scoped DAO、对象验证、版本保存/幂等机制，但新报告合同需有显式 schema 和独立验证器；旧报告继续走旧验证器，不能把新格式伪装为旧 `financial-report/v1`。

## 建议最小工具合同

宿主向工具注入 `{userId, workspaceId, runId}`，模型参数中不提供这三项。

```ts
search_sources({query, entities?, period?, kinds?, limit?})
search_evidence({query, sourceIds?, limit?})
read_source({sourceId, locator?, cursor?, limit?})
cite_field({sourceId, locator, quote?, metric?, period?, unit?, currency?})
calculate({operation, inputs: [{evidenceId, role}], precision?})
save_report({title, templateId?, markdown, citations, calculationIds?, gaps?})
```

`search_*` 返回候选且标明检索路径/精度。`read_source` 返回实际快照内容、结构上下文及服务分配的可引用 ID。`cite_field` 重新验证字段与快照对应关系，生成 Evidence；不存在的坐标返回可修订错误。`calculate` MVP 使用受控 Decimal 运算，保存输入证据和单位转换，后续再接通用代码 sandbox。`save_report` 验证每个引用归属和报告定位、冻结原文/计算集合，并原子保存一个版本。

报告引用建议用明确 marker ID，交付保存为 `{citationId, evidenceIds, reportAnchor:{blockId, markerId}, relation}`；多信源结论可以带多个证据，不再强制一 Claim 一 Evidence。正文变更不能依赖旧字符 offset，优先稳定 block/marker。网页/API 文本即使内容相同也保留其各自来源，去重不得抹掉来源差异。

MVP 中计算支持 sum/difference/ratio/growth-rate，拒绝单位不兼容、分母零、缺输入与非法数值。公式展示含每个输入的点击入口。这里是建议接口，尚未实现。

## MVP 验收证据

- 一个包含用户上传材料和官方原文的真实研究任务，点击报告数字分别定位两个来源中的字段，显示来源版本与单位。
- 至少一个跨期派生数字可复算，两个输入可点击核对。
- 故意引用其他用户 evidence/source ID，拒绝且不泄露对象是否存在。
- 故意把费用行绑定成营收，交付检查拒绝或要求修订，不能因为 quote/hash 正确即通过。
- 快照更新后旧报告仍打开旧 bytes；源被删除时明确不可用而非静默改成实时网页。
- 浏览器中断后同一 Run 恢复；重复 save 不产生重复报告版本。
- JSON/Excel 如果未实现对应定位与 viewer，不在产品里宣称具备这两类字段级定位。

本审查没有执行功能测试；测试清单是后续交付门槛。源码路径证明可复用的实现存在，真实运行和多信源定位必须另行验证。

## `research-report/v1` 最小交付协议细化

沿用现有 Artifact/ArtifactVersion 表中的 `content`（可导出 Markdown）、`document_json`、`report_schema_version`、`document_checksum`、`provenance_json`。新 schema 明确为 `research-report/v1`，不制造旧 Gate/Receipt。一个 version 内冻结以下有界内容：

```ts
type ResearchReport = {
  schemaVersion: 'research-report/v1';
  title: string;
  markdown: string;
  citations: Array<{
    citationId: string;
    marker: string; // 例如 [[cite:c1]]，出现于 Markdown
    evidenceIds: string[];
    relation: 'supports' | 'contradicts' | 'context';
  }>;
  calculations: Array<{
    calculationId: string;
    operation: string;
    inputs: Array<{evidenceId: string; value: string; unit: string}>;
    result: string;
    unit: string;
    precision: number;
  }>;
};
```

`provenance_json` 储存宿主工具登记簿里对应的 exact reference、snapshot receipt/hash、locator、quote、period/unit/currency，以及输入证据。模型只提交已获工具 evidence ID；服务按 ID 取可信条目。正文引用可先用 marker，Web 不必等完整富文本编辑器才交付。若要兼容现有 `citationSpans`，由服务根据最终正文 marker 推导，禁止模型任意提供 offset 后当作可信定位。

必须新增且独立于 Need 的验真：

1. 验证 Run/Workspace/Artifact 的 owner 与 base version；接收已完成工具登记簿中的 evidence，不接受模型自造 reference。
2. 逐条验证 snapshot hash/原文引用与 locator，保留信源能力状态；不够精确时明确显示精度，不以来源URL冒充字段定位。
3. 所有 marker 有对应 citation，所有 evidence/calculation ID 在当前受权集合内；计算用 Decimal 重算、检查单位和零分母。
4. schema、长度、集合大小及去重验证；冻结 Markdown+结构+证据集合 checksum。
5. 锁定目标 Artifact 后一次事务保存版本、currentVersion、Run成功与交付事件；以 `runId+operationId` 幂等键绑定内容hash，重放hash不同返回冲突。

`workspace_artifact_dao.py:create_or_get_artifact_version` 可以参考其 owner 筛选，但当前 IntegrityError 重放仅按 version ID 返回，未核对 payload，且单独 commit；不能直接串联其他 DAO 调用来声称原子交付。参考 `workspace_report_delivery_transaction.py` 的事务方式，新增单一职责轻量事务。

原 generic 引用解析的入口为 `workspace_artifact_operations.py:resolve_document_reference` → `_require_reference_in_artifact_provenance` → `_reference_from_provenance`。最后一个函数会把请求中的 reference/locator deep merge 到可信base上，所以新 schema 必须走 **只接收 citationId 的解析分支**：读取指定版本冻结 citation，再从服务端 provenance 找完整 reference，忽略调用方 URL/locator 后交给已有 document reference service。这可以复用现有 viewer 而不复用客户端可覆盖证据位置的行为。

对应最小路由建议：`POST /workspaces/{workspaceId}/artifacts/{artifactId}/versions/{version}/research-citations/{citationId}/resolve|source-html|source-file`。浏览器只传 route ID。旧 financial-report 和旧 document-reference 路由保持各自合同，新路径不伪装旧 Claim Link。

现有 `workspace_artifact_canonical_policy.py:require_legacy_artifact_mutation_allowed` 会拒绝未知 structured schema，这是合理保护。新报告的编辑、恢复和再研究需要明确 research-report-aware 路径；不可通过清空 schema/checksum 来绕过。
