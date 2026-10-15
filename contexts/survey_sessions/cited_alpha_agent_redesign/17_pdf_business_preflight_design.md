# 跨源真实业务 Run：PDF 接入与零模型预检

2026-09-11，只读源码审查。未调用模型/DocAI，未建 DB/云资源，未写应用代码，未触碰 live Run 19411。所有路径前缀：B=/Users/xuhao/Documents/Other/mindspace_backend；M=/Users/xuhao/Documents/Other/mindspace_ml_backend；W=/Users/xuhao/Documents/Other/mindspace_web_frontend。

六项绑定已实时核对：三仓均 feat_codex/financial-report-agent-plan-writer-20260717；B f7e10b1d7e7392644f1403093b73d0a5d9189352，M 58dc18e882b7f68a2969ce629ad60a005377258f，W 8962bbcf2f0197902841f73a891701e5406c8cce。各仓旧 dirty 保留。遵守三仓 AGENTS；本方案保护 router/service/repository 分层。既有 13_real_business_run_acceptance_design.md 仍适用。

## 结论与最小方案

下一条跨源验收可走真实 JWT 上传入口、真实 MySQL 文件库与 Workspace 附件、真实隔离 PG 文档、当前 freeze 的一次真实 DocAI，最后真实 GCS 原件/解析快照与研究 Run。原件存储暂用严格限定目录的本地字节 transport，声明 AWS S3 网络与生产队列未验证。不能给旧 manual version 换 owner/workspace 后直接使用。

当前普通上传后台会 parse，并启动后续索引；研究 freeze 又 fresh parse，一次上传后多次 Run 可重复付费。短期 hold 普通上传 scheduler，再让 freeze 真实调用一次，可避免本次重复成本；这不等于修复生产重复解析。长期应调整为“上传保存原件 → 一次生成不可变解析版本 → 每个研究按当前权限绑定版本”，解析缓存键绑定原件 hash、provider/processor/config/parser 版本，业务授权与可复用解析内容分离。当前先不扩协议。

## 实际入口与调用链

1. Web W/src/app/services/userFiles.ts:60，multipart POST /api/v1/files/library/upload，字段 file、可选 folderId，真实 JWT。
2. B/mindspace/app/launch.py:329 挂 user_file_library_router；B/mindspace/router/v1/user_file_library_router.py:48 转 UserFileLibraryService.upload_file。
3. B/mindspace/service/user_file_library_service.py:76：原件 bytes -> s3_service.save(None,key,bytes,mime)，build_public_url；调用 MLChannelSourceService.index_channel_agent_file_attachments。
4. B/mindspace/service/ml_service/ml_channel_source_service.py:110：真实 HTTP POST /agent/v1/document-store-file-attachments；内部服务身份，body userId/chatSessionId/attachments。
5. M/mindspace/router/v1/channel_agent_file_router.py:114 -> DocumentStoreConversationUploadService.schedule_uploaded_attachments -> DocumentStoreAttachmentScheduler.schedule_one_attachment。
6. M/mindspace/service/document_store/conversation_upload_scheduler.py：真实 PG upsert_document 与 upsert_ingestion_job，然后调用注入 task_scheduler。此阶段只创建 queued 文档；file_id/file_document_id 由服务生成，metadata 带 user_id/file_id/chat_session_id/mime_type。
7. Backend 收 ML 真结果后 UserFileLibraryService.register_documents 建真实 MySQL owner 文件库项。
8. POST /api/v1/workspaces/{workspaceId}/sources/files，body {"fileItemId":"uf_..."}。B/mindspace/router/v1/workspace_router.py:282 -> WorkspaceService.attach_file_source:708，核对 workspace owner 与 file owner，然后写 source metadata。
9. 真实 research admission documentIds=[新 documentId]；B/mindspace/domain/dao/workspace_research_admission_dao.py:56 冻结 authorizedDocuments；每次读仍由 get_research_document_authorization:154 校验 active 文件 owner/attachment/fileId。
10. Executor MLResearchDocumentService.freeze -> POST /agent/v1/research/documents/freeze；M/mindspace/service/research_agent/document_version_service.py 核对 PG owner/file/raw SHA，fresh parse，真 GCS immutable raw/provider/manifest receipts。之后 read-verified 再回读原件与 provider，重放 adapter，精确比对 normalized。

## 关键缺口：hold queued 后没有 raw SHA

queued scheduler 不读原件、不算 SHA。DocumentVersionService._freeze 必须 document.sha256 == 实际 bytes hash；直接 upload→hold→Run 会在 provider 前拒绝。因此本地准备需要明确记录一项 setup：从此次真实上传对象重新读取 bytes，算 SHA，通过真实 DocumentStoreRepository.upsert_document 在同一 documentId/owner/fileId 上补 sha256；保留 status=queued 与 job=queued/held，metadata、storage_uri、source_document_id 均保留。禁止把旧 normalized 表写成新文档的解析完成状态。

此 setup 只证明真实存储/授权与 fresh-freeze 业务闭环，普通上传 worker 完成路径仍未验。长期应把原件 digest 在上传保存时登记，或者经统一 ingestion 服务完成，而不是每次操作脚本补字段。

## 本地字节 transport 可以做什么

B UserFileLibraryService 构造支持 s3_service 与 ml_service 注入。M DocumentReferenceSourceFileService 构造支持 document_repository、resolution_service、storage_service 注入；后者只需 load_once(bucket,key)。保持该真服务的 owner 判断，再调用字节 adapter。

建议仅供本地 composition 的 RawObjectStore：
- save(None,key,bytes,mime) 写唯一临时对象目录，拒绝绝对路径、..、symlink 越界、覆写不同 bytes；保留原件与 sha/size/mime 审计。
- load_once(None,key) 从同一目录读原始 bytes，无改写、无 parse，无任何授权返回值。
- build_public_url 返回明确本地占位 URL；本次不验证普通文件库 preview-url。若需要显示普通预览，另建真实 JWT owner route；不要公开整个对象目录。
- 不声称调用了 AWS S3 SDK/真实 S3。若要保留 AWS SDK 本身可用 S3 兼容本地 endpoint，但当前未建立/未验，不必要为了表面一致扩大基础设施。
- 正常 SourceFileService 只识别 s3:// 或裸 key；直接塞 gs:// URI 会被当作 key，不可据此声称已有 GCS upload 支持。
- freeze 的 DocumentVersionStore 保持默认真实 ADC/GCS；该 store put 后还读回校验。上传临时目录不是最终证据存储。

## 最小进程组成与注入注意

隔离 Backend MySQL 127.0.0.1:13306/research_api_smoke；独立 ML PG。psql/postgres 在 /opt/homebrew/bin 可用，但本次未探测连接/集群，不能称隔离 PG 已就绪。下一步先只读确认 listener、current_database/current_user/server_address、表列表；避免沿用 remote YAML。必要时另起限定临时 data dir/loopback port 的 PG，由 root 明确执行，不能连接生产库初始化 schema。

M DocumentStoreRepository(session_factory=...) 有正规注入点；initialize_schema 使用 DOCUMENT_STORE_SCHEMA_STATEMENTS，无 pgvector 扩展要求。使用独立 session factory 可避免全局默认 PG。DocumentStoreConversationUploadService(repository=real_repo,task_scheduler=held_scheduler)；held_scheduler 只写本次请求 payload 的私有审计，不启动 Celery，不返回伪造已处理状态，task_id 可空。直接 route service 绑定仅限 composition 进程，不改生产源码。

ML composition 挂真 channel_agent_file_router 和 research_document_version_router；真实内部 token 严格校验；Backend MLChannelSourceService 与 MLResearchDocumentService 连接同一 loopback ML，用显式 InternalServiceTokenProvider 注入。MLWorkspaceService 默认 local token provider 返回 None，仅设置 WORKSPACE_ML_RUNNER_URL 不会自动带本地随机 token。

13号设计指出的 CallbackService 缺口仍存在：其内部构造 ResearchDocumentSourceReader，没有 document_client 参数；Executor 则已有 document_client。优先窄化增加 callback 的 document_client 注入（与 Executor 一致），并复用相同真实 MLResearchDocumentService；不可把 source_factory 换成忽略 document_reader 的 verifier。否则只能过程级更改默认 client/token wiring，容易误扩大影响。此审查未改应用代码。

DocumentVersionService(repository=real_repo,source_reader=真实 SourceFileService 注入字节 adapter,store=真 GCS store)；FreshDocumentParser 保持真实默认。36页会选择 batch，当前 provider 单次提交保护保留。不要把早先 provider_result 注入 parser 后冒充本次 freeze。

## 可执行零模型 preflight 清单

以下都是下一阶段操作清单，本审查未执行；本轮禁止发 Run/正常 freeze 成功请求。

1. 六项复核三仓，读现有 root 私有配置方式，输出只允许 localhost/端口/库名，禁止 token/password/全配置。
2. PG 只读探测并绑定专属实例或库；得到许可后仅对该目标 initialize_schema。ML 断言禁止默认 remote DB，模型与 DocAI 调用入口采用 fail-on-use 审计。
3. 新建独立本地 API composition（不要修改/重启 live 19411 的服务）；挂真实 auth/upload/workspace routes，ML 挂真实 attachment/document routes，固定内部 token 与 loopback。
4. 真实 JWT owner 上传归档原件；记录 upload HTTP code、fileItemId/fileId/documentId 与 objects SHA；GET /api/v1/files/library/{id} 回读；ML repo get_document 回读 owner/file/source/storage。审计 scheduler held、模型数0、DocAI数0。
5. 再读实际存储对象，hash 应为 05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc，11267189 bytes，36pages。使用真实 repository 补 SHA，记录 setup 操作，保持 queued/job held。
6. 真 JWT POST workspace sources/files；GET workspace sources；调用 get_research_document_authorization 验证同一 fileItem/fileId。另一个真实测试 User JWT 读该 file、workspace、attach 都应拒绝；该用户不得沿用 owner token。
7. 仅对不存在或错 owner/fileId 的测试 document 调 /freeze，预期 422/detail.providerCallAttempted=false，审计云调用0。不要对正确 scope 调 freeze，那就是付费步骤。
8. 独立进程 SourceFileService.fetch_source_file 正确 owner 返回此次上传原 bytes，错误 owner拒绝；验证 adapter未伪造解析与授权。
9. Callback 客户端/token 注入修复后，对不存在测试Run做callback只应409；不得拿 liveRun试错。到此 preflight 结束。
10. 上一付费 Run 终态后，root 才启动新真实跨源 Run，frozen question/documentIds/asOf/limits，由 Executor 按真实权限 freeze 一次，记录 provider intent/operation、原截止时间、调用次数。不要在预检手动 freeze 后再交 Executor 重新 freeze（会双重付费）。

## 旧 provider 输出的复用边界

已有原件、provider shard 与真实 operation 可只读校验、做 adapter replay、离线 locator/geometry 验证。原件内容相同不等于旧 owner/workspace version 可转让。当前 freeze 硬写 providerCallAttempted=true/providerCallStatus=completed，缺少 cache/import provenance；注入回放 parser 会误报本次真实调用，禁止作为正式 Run。

以后若新增 reuse，应记录旧真实 provider operation/处理器/配置/hash、原件 hash、cache hit/no new call、新授权 scope、重新生成的 manifest/version；区分本次 providerCallAttempted=false 与 priorParseStatus=completed。此方案尚未实现。对于当前 API 正常新 Run，需一次 fresh provider 调用，或先实现并测试完整 reuse 协议。

## 原材料与验收范围

原件：/Users/xuhao/Documents/Other/context-infrastructure/contexts/source_materials/cited_alpha_cross_source_tesla_2024/05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc.pdf
真实历史provider：/tmp/cited-alpha-docai-full36-01/provider-result.json；对应operation.json/completed-operation.json；旧version目录仅只读。

Tesla 10-K + Tesla earnings PDF 是不同资料/格式、同一发行人，不能声称两个独立机构。batch目前 geometry 可能降级页级；报告必须真实声明定位精度。Document typed numeric normalization 仍受 Backend限制，不能未经支持把PDF数值纳入金融计算。最终真实报告需要同时核对来源链接、原件SHA、段/行/cell locator实际支持、跨源口径/期间差异、审阅回执、持久化版本、Chrome读回；queued上传或parse完成都不是报告验收。


## 正常上传SHA与跨来源composition（2026-09-11）

正常上传SHA链路已实现并推送：Backend8ae870a从原字节计算摘要，MLff6e4c5传递、入库并在worker转换/解析前核对。独立新scope通过正常JWT上传、附件授权、PG摘要及另一进程原件回读。证据目录 `/tmp/cited-alpha-pdf-isolated-MJJV9O/sha-v2`。此前null摘要记录保留，未手动修补。

下一条跨来源任务准备位于 `/tmp/cited-alpha-cross-run-7YGKhq/README.md`。零模型18883/18884复用上述真实已有用户和附件，Executor与Callback共用document client；真实SQL确认该用户Run数为0，未调用freeze或provider。DocAI显式配置来自旧36页实际operator，不能沿用默认local.yaml的旧项目。当前只证明授权和原件可读，正式Run、解析、报告与生产链路仍待验证。

正式研究中由Executor触发freeze，禁止预先人工parse后再让Executor重复解析。普通上传worker当前被显式held；生产上传解析与研究freeze之间的复用仍是需要解决的产品问题，独立预检不能掩盖该缺口。
