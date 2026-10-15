# 原件解析一次、研究按权限复用：最小长期方案

2026-09-11，只读源码设计；未改代码、未调用provider、未读取密钥。ML根目录为 /Users/xuhao/Documents/Other/mindspace_ml_backend，Backend根目录为 /Users/xuhao/Documents/Other/mindspace_backend。

## 判断

应把“对原件调用解析provider”与“为一次研究绑定可引用版本”分开。上传与研究都请求同一个持久化解析产物；研究只在当前权限校验后绑定产物，不再默认fresh parse。实现上无需引入新的多Agent流程：新增一个统一解析产物service及小型PG持久化状态，复用现有原件store、provider adapter、normalizer、reader和Backend Run checkpoint。

最小版本先按同一owner/file/document复用，不做跨租户内容去重。即便SHA相同，其他用户是否拥有该文档及provider产物也不能从cache命中泄露。以后有明确存储授权设计再扩共享。

## 现有代码证明重复在哪里

1. ML `service/document_store/conversation_upload_service.py` 的 index_uploaded_file 真实读取原件并检查hash、prepare_parse_input后调用布局ingestion。
2. `service/document_ai/layout_ingestion_job_service.py` 包装ingest，当前max_attempts默认3；成功后调catalog/chunk embedding和lexical索引。这是普通上传解析路径。
3. `service/document_ai/layout_ingestion_service.py` 再调用 DocumentAIBatchService，拿documents交adapter，最后 repository.replace_parse_result。
4. `service/research_agent/document_version_service.py` 的 freeze 独立回读同一上传文件，检查owner/file/hash，调用 FreshDocumentParser；没有按原件hash查询上传解析产物。新研究会再次调用provider。
5. Backend `service/research_runtime/executor.py` 已可继承父Run的completed documentCaptures；这是同scope既有研究版本的恢复/续接，不是普通上传产物复用，也不解决初次研究重复parse。

## 现有持久化物料能否直接复用

| 已有物料 | 当前能证明什么 | 距离复用所缺 |
|---|---|---|
| documents.sha256、owner/file metadata | 上传原件内容标识和业务身份；新hash链已能queued即登记 | 不等于immutable原件已保留，也不证明解析采用该bytes |
| documents/pages/lines/tables/cells/spans | 当前可搜索展示的解析结果 | replace_parse_result会按document_id删除重建相关记录；不能作为不可变历史证据 |
| parse_runs/raw_output_uri、ingestion_jobs/raw_output_uri | 有provider输出目录线索、parse run/status | 无逐object generation/hash/size清单，不能证明目录完整或对应唯一provider调用 |
| batch返回documents/operation_names/gcs_input_uris/gcs_output_uris | 当前一次调用内有更多真实信息 | layout_ingestion_service仅把首个gcs_output_uri写parse_run；完整chunk/operation清单未成为权威不可变manifest |
| GCS provider JSON输出 | 若对象仍在，可只读找回真实provider材料 | 当前list_json_keys只读单页列表，不处理nextPageToken；取目录最新对象，不钉generation；没有immutable receipt/hash，重试可能混入同前缀结果 |
| Research DocumentVersionStore | 已有content-addressed raw/provider/manifest并回读hash，scope绑定和adapter replay | 版本目前按研究scope构造、freeze硬写providerCallAttempted=true；需要可复用产物与scope绑定分层 |

另一个细节：operation_client在返回documents前按chunk page_offset调整页码及layout嵌套pageSpan。这是派生后的provider表示，不是原始GCS JSON逐字节。长期manifest需要同时保存原始shard bytes及offset转换recipe/版本，才能证明重放。不能把已调整内容标记成未经变换的provider raw。

因此，不能直接把mutable表组装成manifest，也不能只凭raw_output_uri为旧文件自动盖“可复现”章。可复用的基础最接近现有DocumentVersionStore；普通上传应在解析成功当时把完整provider材料封存进去。

## 最小产物与状态设计

新增 `document_parse_artifacts`（名称建议，PG一张表即可承载当前阶段）。逻辑主键包含 owner/document/file、original raw SHA、parse_spec_hash；记录状态、lease/fencing token、intent/operation清单、immutable artifact receipt、错误类型/时间。唯一约束防上传worker与研究同时提交相同解析。SQL状态用于协调；不可变manifest才是证据正文。

parse_spec至少包含：provider/product、明确processorVersion（不能只记可变processor默认版本）、mode online/batch、规范化processOptions（区分None与{}）、原件MIME、page selection/chunk策略/版本、语言或OCR关键配置。normalizer版本独立于provider parse key：normalizer升级通常可以重放已有provider输出，不必再次付费。

不可变解析产物manifest至少保存：

- 原件receipt：hash、size、MIME、固定对象/版本；非native格式另列derived PDF receipt、转换器版本及原件→派生关系。
- 完整provider执行信息：真实processorVersion、提交时间、每个operationName、每个chunk输入hash/页区间/输入对象、请求配置hash、输出shard列表与各自generation/hash/size、页完整性检查结果。
- provider原始shard receipts及可确定重放的排序/offset recipe版本；需要时附normalized-provider表示receipt。
- normalizer recipe与版本、规范化结果receipt/hash，包含重放所需documentId/title/source metadata（不能事后拿当前可变title重建旧结果）。
- geometry所需provider frame/mode/配置证据与资格状态；字段geometry仍从immutable原件与provider算出，未知框架明确page precision。

现有normalizer的ID包含document身份，因此最小产物仍绑定owner/file/document；跨workspace可在同document上复用，重新创建workspace-bound版本，不改旧版本内容。不急于让normalized数据完全跨document通用化。

## 两条调用路径如何共享

上传：保存原件/sha → `ensure_parse_artifact(identity, parseSpec)` → 真实provider结果封存 → publish ready artifact → 从该artifact重放/投影mutable搜索表 → 异步embedding/lexical。

研究：当前Workspace附件授权 → `resolve_ready_artifact(identity, parseSpec policy)` → 校验receipt/hash与normalizer replay → `bind_document_version(user, workspace, document, file, artifact)` → 保存Run documentCaptures。研究中引用与计算仍走Backend独立source verification。

可保留现有/private freeze路由作为兼容入口，但不能在内部悄悄假报fresh调用。建议新增明确`resolve/bind`操作与version v2：`resolution=reused|created`、`providerCallAttemptedThisRequest`、`parseStatus=completed`、`parseArtifactId`。原v1继续按旧规则只读；新v2双端显式识别。不要把已有providerCallStatus=completed解释为这次发生了调用。

同时区分“本次请求没新调用”与“已有解析仍处理中”。遇到submitted/running返回pending+artifact/job identity，不能为了让同步freeze成功而重复parse。Backend最小需要明确文档准备等待/恢复状态；原Run期限继续生效。若暂不扩Run等待，可在Run admission前阻止未ready附件并让上传页显示处理中，但不能把待处理当failed或隐式fresh fallback。

## 并发、重试与未知结果

协调不能只靠Python锁。领取同parseSpec产物必须CAS/lease，submit intent持久化在POST之前；真实operation收到即写回。另一个请求只能观察同产物。

- 未提交前失败：允许有界重试。
- 已有operation：只读poll同operation，成功后从完整输出封存；不要再POST。
- POST超时且operation未知：状态unknown，禁止普通worker的run_with_retries再次付费；需要同operation检索/人工确定的恢复策略。
- 封存失败但provider完成：重读同operation输出、重复content-addressed put，不能重parse。
- 搜索表/embedding失败：产物仍ready，修复投影或索引，不重parse。

普通上传当前ingestion层3次重试与operation client自身重试不能原样包住新统一付费阶段。必须将重试范围缩小到明确可重放的读取/封存/投影步骤；这是消除重复费用的必需组成，不只是加cache。

## 各类文件的产品行为

| 状态 | 用户及系统行为 |
|---|---|
| 新native PDF | 上传保存后自动排一个解析；文件显示处理中；ready后所有研究复用同产物 |
| 正常worker解析中，用户发研究 | 引用同一job等待；不再提交；期限到返回明确未完成状态 |
| 原件相同且同owner/file的另一workspace | 当前附件与owner重新核验后新workspace绑定；原产物不改 |
| 旧文件只有mutable表/raw_output_uri | 标legacy_unverified；先只读审计是否能建立完整历史执行链。证据不足则明确需要一次新解析，不用缓存伪装 |
| 旧文件已有合格research v1 receipts | 独立验证原件/provider/manifest、保留旧provenance后注册兼容产物；不修改原version，不声称本次调用provider |
| 已知失败且未provider提交 | 可重试同产物准备 |
| submitted/unknown | 观察/恢复原操作，不自动启动新解析 |
| 原件bytes变化 | 新raw SHA新产物；旧报告继续绑定旧原件/解析版本 |
| normalizer升级 | 从旧provider原始shards重放，生成新normalized版本；无provider调用；旧报告仍用旧reader版本 |
| processor/config升级 | 新parseSpec需要新provider产物，只在明确选择/迁移时执行；不因为阅读旧报告触发升级 |
| 权限撤销/附件归档 | 即使命中产物，新的绑定与读回仍拒绝；不通过知道hash或artifactId访问 |

历史provider导入需要明确`historical_import`来源、观察时间、能证明/不能证明的processor与input关系。若实际processorVersion/全部chunk映射不可找回，不可升级为qualified geometry。允许page-level历史证据须由版本合同明确，而不是填一个猜测的processor版本。

## 具体文件映射

ML：

- 新 `service/document_store/parse_artifact_service.py`：统一ensure/resolve/封存编排；不堆进router或现有大型service。
- 新 `repository/document_parse_artifact_repository.py` +小型schema迁移：唯一键/CAS/lease/status/operation指针；ORM/SQL只在repository。
- 新 `domain/.../document_parse_artifact.py`：typed artifact/parseSpec/状态合同；无网络。
- `document_ai/operation_client.py`、`batch_service.py`、`gcs_io_service.py`：返回每个真实operation/chunk及原始shard完整清单；分页/generation/hash，单次submit边界。既有常规调用兼容需逐步迁移，不能误改变其他provider入口。
- `document_ai/layout_ingestion_service.py` 与 `layout_ingestion_job_service.py`：从统一artifact取得产物，再写mutable投影/索引；分离paid段与投影重试。
- `research_agent/document_version_service.py`：拆出纯bind/replay，沿用DocumentVersionStore；fresh parser调用迁至统一artifact producer。
- `research_agent/document_version_store.py`：复用content-addressed写/读，扩manifest类型/receipt需向后兼容。
- `research_agent/document_geometry.py` 与 online provider：资格判定来自实际执行recipe；拒绝cache metadata自行声称qualified。
- `router/v1/research_document_version_router.py`：新增resolve/bind/pending合同；不在router判缓存或调provider。

Backend：

- `ml_service/ml_research_document_service.py`：v2版本/pending/本次是否调用的显式校验。
- `research_runtime/executor.py` / document capture相关模块：等待/绑定真实artifact，保留原scope/deadline/checkpoint fence；未知操作不重发。
- `research_report/document_reader.py` / source_integrity：v1/v2按各自reader重放，继续当前附件校验；不能仅检查artifact存在。

Web/mobile：文件处理状态可区分原件已存、解析中、可研究、索引中/索引失败；研究准备等待文案不冒称正在分析报告。若最小阶段只在ready后研究，须明确用户可恢复入口。公开旧请求继续兼容，新增状态应做双端降级。

## 最小实施次序与验收

1. 原件SHA链（已做）只提供基础，不宣布已解决重复parse。
2. 新上传只对native PDF启用统一不可变产物，先让上传worker封存成功；旧表投影从产物生成。暂不迁移旧文件。
3. 新研究改resolve/bind；旧v1报告只读兼容。先同file跨Run，再同owner跨workspace。
4. 单独历史导入/升级工具，先dry-run清单，输出缺失证据，不静默补齐。

必要验收：

- 一次真实上传完成后连续两个研究，provider总POST=1，两份报告绑定同parse artifact、各自正确scope；两个并发请求也只1POST。
- 原始shard+chunk映射完整重放产生同normalized hash/字段ID；缺shard、错generation、篡改hash、重复/漏页一律拒绝。
- 真实PDF几何在受支持recipe中一致，batch未知frame仍页级，normalizer升级不能提升资格。
- 同hash其他用户无法访问；撤销附件后拒绝；旧报告不随mutable表重建或新版本升级而改变。
- 故障注入覆盖submit前、POST结果未知、operation已存、provider已完成但封存失败、投影/embedding失败；只重放安全步骤。
- 旧请求/旧job/旧v1版本可读；新解析中状态与期限在真实API/Chrome回读，未ready不伪称失败或成功。
- CI的离线provider计数fixture仅证明合同；最终至少一个真实上传+两个真实研究验证实际一次provider调用，才关闭重复解析问题。

本方案尚未实现；已有/tmp跨源composition仍是hold普通worker、由freeze一次fresh parse的有界验收路径，不等于这里的长期统一产物已交付。
