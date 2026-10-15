# 上传 Document 的不可变版本缺口与最小实现

日期：2026-09-10。状态：基于当前代码的只读审查；尚未新增 retained 接口或存储写入。

## 结论

现有 DocumentStore 是“当前解析结果”的查询系统，不是报告可永久核查的版本证据库。直接把 Backend 的 documentIds 查询成 `sha256/storage_uri/parser_version`，不能证明旧报告仍指向同一份 bytes 和同一套字段定位。

因此当前上传文档入口保持明确不可发布状态。必须先冻结原始文件、实际解析文件及解析清单，再开放 `read_verified`；不能以数据库里恰有 SHA 字段代替不可变存储保证。

## 已有可复用能力与证据

| 当前代码 | 能力 | 边界 |
|---|---|---|
| `DocumentStoreQueryRepository.get_documents_by_ids` | 返回 document_id/source/storage_uri/sha256/parser_version/metadata | 查询本身不鉴权，无工作区关系 |
| `conversation_upload_payloads.file_metadata` | 写 user_id/chat_session_id/file_id | 没有 workspace_id，不证明文件属于某工作区 |
| `DocumentSearchService._is_context_visible` | conversation_upload 按 user_id 校验 | 不是 workspace授权；非conversation_upload默认公共 |
| `DocumentSearchService.read_page` | 真实页、行、表、cell与定位 | 查当前解析表；formatter不返回顶层sha/parser |
| `DocumentStoreRepository.replace_parse_result` | 一次更新当前解析 | DELETE旧source_refs/spans/tokens/chunks/cells/tables/lines/pages后重写 |
| `DOCUMENT_UPSERT_STATEMENT` | 更新document元数据 | 同document_id覆盖storage/sha/parser |
| `conversation_upload_pdf_rendering` | Office/HTML渲染PDF，保留original_*关系 | 渲染写普通storage.save，没有版本化receipt |
| `AwsS3Storage.save/load_once` | 现有对象读写 | 普通put_object与当前key读取，未见VersionId/IfNoneMatch绑定 |
| `DocumentReferenceSourceFileService.fetch_source_file` | 源文件viewer读取与定位 | 读取当前对象；没有独立SHA重算或固定解析版本读取 |
| `SecEdgarSnapshotCaptureService` | 内容寻址GCS、create-if-absent、hash-bound receipt | 只支持SEC合同/大小/MIME，不能给上传文件伪造SEC receipt |

这些观察来自实现，不推断真实bucket一定开启/关闭版本控制。即使bucket事实上保留旧版本，当前数据合同没有保存并读取generation/versionId，也不能宣称已经绑定版本。

## 必需的新写入步骤

1. **Backend授权绑定**：由已认证用户的workspace附件/Source记录得到 documentId/fileId，核对文件owner与工作区关系。只认documentIds不够。Backend把允许集合通过内部服务身份交给ML，不让模型提供owner/storageURI。
2. **冻结原始文件**：服务端从现有file记录取存储key，按流限制读取，重算SHA；写私有GCS新prefix `workspace-source-snapshots/documents/sha256/<sha>.<ext>`，`ifGenerationMatch=0`，保存对象generation、MIME、size与SHA receipt。使用现有ADC存储能力，独立上传文件合同，不套SEC。
3. **冻结实际解析输入**：非PDF如先渲染PDF，原始Office与实际PDF分别保存内容寻址对象。解析定位绑定PDF的SHA；receipt同时记录原始SHA、派生SHA、converter版本。不要把Office的SHA绑定PDF坐标。
4. **冻结解析清单**：在同一解析事务/一致快照中导出 document/page/line/table/cell/span/source_refs 与坐标单位、page尺寸、parser/processor版本。规范JSON后算 `manifestSha`，以内容寻址方式保存不可变manifest。避免导出期间replace_parse_result导致半旧半新。
5. **登记版本引用**：生成 `documentVersionId = hash(parsedContentSha,manifestSha,parserVersion)`。当前document表可以继续作为检索入口，但报告永久引用这个版本；旧manifest不随重解析删除。
6. **独立核验**：Backend使用只读ADC读取指定raw/parsed/manifest对象，验证大小、MIME、hash、generation，再从manifest exact locator解析quote。对PDF文字/表格，抽取结果与原始PDF支持关系的可信程度要明确；manifest hash证明没有变，不自动证明OCR正确。

既有文件回填也必须走以上流程。若当前源key已变、旧SHA不匹配，只能保存新的版本并明确旧版本缺失，不能补造历史版本。

## 最小host-only接口提案

### Resolve版本目录

`POST /agent/v1/research/documents/resolve-versions`，仅private runner并复用内部身份。

请求由Backend组装：`userId/workspaceId/runId/authorizedFiles:[{documentId,fileId}]`。ML查询并交叉核对现有document metadata；返回已存在且可证明的version记录。对于没有workspace/file关系证明或没有immutable receipt的记录，返回明确的 `authorization_unproven` / `version_not_retained`，不把当前metadata包装成retained。

冻结/回填是独立host写入操作，应有幂等键和完整操作结果；resolve不能隐式触发重新OCR、付费embedding或覆盖解析结果。

返回记录最少包含 `documentId/fileId/documentVersionId/ownerUserId/originalReceipt/parsedReceipt/manifestReceipt/parserVersion`。storage URI只在内部传递，工具和public viewer拿受限locator与版本ID。

### 精确独立读取

`POST /agent/v1/research/documents/read-verified`：请求同scope与documentVersionId、exact locator，不接受quote/value/storageURL。

从不可变manifest读取真实行/cell/span，返回quote、原始字段元数据、表头/单位/脚注上下文与版本receipt。Backend必须绑定当次授权scope并核验引用版本；只转发ML的“verified=true”不算独立证据验证。

现有DocumentSearchService仍负责召回当前候选，候选document_id被映射到host冻结的版本后再精读。检索结果页号/cell_id找不到旧manifest时明确重新定位，不跨版本自动猜同名字段。

## 实施与验收顺序

1. 先查Backend现有workspace附件关联，确定能证明owner/workspace/document/file关系的正式查询接口。
2. 新增document snapshot writer与manifest writer，fake store测试包括create-if-absent、SHA错误、变更对象、原文件与PDF不混绑。
3. 用同一document_id重解析两次，证明旧版本manifest和引用仍能独立读出旧quote，新版不会覆盖旧定位。
4. 实现上述私有resolve/read接口、Backend独立读取、普通上传文件权限反例测试。
5. 最后接ResearchExecutionService授权目录与Web引用查看器。用真实上传PDF/表格报告验收，不能以SEC成功替代Document路径验收。

本次没有新增声称retained的接口，也没有进行存储回填；这是阻止错误证明的必要边界，并非把上传文档永久排除出MVP。
