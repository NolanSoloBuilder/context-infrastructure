# MVP 实施进展

2026-09-10。目标 active，MVP未完成。首轮目标工作属于实际进展：完成专题设计、新运行核心/宿主/消息转换、纯报告合同、独立阅读组件及离线验证。

## 绑定

- Web /Users/xuhao/Documents/Other/mindspace_web_frontend，HEAD 4758ebcdad6ec76df3781a765ad3448224da540e。
- Backend /Users/xuhao/Documents/Other/mindspace_backend，HEAD d191191dc9fc4787f73e74e18b792062fce97dac（下一轮需重新核对）。
- ML /Users/xuhao/Documents/Other/mindspace_ml_backend，HEAD f0a491ca881e8f0fddb67e02e0cd84d132d53db9。
- 以上均绑定 feat_codex/financial-report-agent-plan-writer-20260717，原dirty全部保留，新增代码尚未提交或发布。

## 当前新增

ML runtime/pi-research：bridge.mjs、runner.mjs、main.mjs、runner.test.mjs、README.md，真实Pi 0.85.1核心，JSONL模型/工具请求交给Python，不读个人凭证，无内置shell/network。

ML mindspace/service/research_agent：pi_process.py、vertex_messages.py、model_gateway.py、README.md。Python host独立预算、超时与child清理；Vertex DTO保留thought signatures、tool IDs和计量；model gateway忽略child型号，仅用model-policy选择。resources/{local,preview,prod}.yaml在agent_deep_research追加code-path/used-by，不换模型。

Backend mindspace/service/research_report：contract.py、calculations.py、__init__.py、README.md。research-report/v1正文及research-report-bundle/v1，摘要引用、段落多证据、Decimal计算；不包含原文真实性或语义检查。

Web src/app/components/workspace：ResearchReportDocumentView.tsx、ResearchReportDocumentView.test.tsx、research-report-types.ts。README末尾追加本次说明，原dirty部分未覆盖。尚未接页面，不代表UI已运行验收。

## 验证

- Pi Node实际核心9项离线测试通过（子agent执行）。
- Python宿主+Vertex转换+模型policy集成26项通过（主agent执行，PI_MODULE_ROOT=/opt/homebrew/lib/node_modules/@earendil-works/pi-coding-agent/node_modules ENV_MODE=local .venv/bin/python -m pytest tests/test_research_model_gateway.py tests/test_research_pi_process.py tests/test_research_vertex_messages.py -q）。
- Backend合同23项通过（子agent执行）。
- Web renderer6项通过（子agent执行）。
- 未真实模型调用、未业务落库、未UI集成、未构建发布。测试通过不证明报告质量。

## 下一步依赖

1. 主agent审查新协议与renderer一致性；未来增加表格时显式扩schema，当前paragraph-only不能伪装支持表格。
2. 新证据工具复用DocumentSearchService.search/read_page与SEC原文capture，宿主注入身份，服务生成可信evidence catalog。
3. 原文/字段验证、检查报告语义、计算记录接入，模型不能提供trusted_evidence参数。
4. Backend新原子保存事务（版本、current pointer、Run终态同事务）；只凭artifactVersion+citation ID解析引用，禁止客户端locator覆盖。
5. 新运行类型接现有队列/事件恢复；避免伪造旧固定Need/Gate receipt。
6. 页面接新schema，版本与导出对齐，真实Chrome点击与报告验收。
7. PR/main/Actions发布与runtime回读，多信源/计算/完整财报/续研成功后逐项完成04_mvp_delivery_contract验收矩阵。

## 已发现需保留的问题

旧固定流程不适合直接接新运行器。原generic resolver会合并请求方locator覆盖可信base，不能用于新强引用路径。SEC capture与普通网页/API/Excel的持久化能力不一致，需明确支持矩阵。会话JSONL不是可靠任务调度器；Python取消可以清理child，但现有Vertex client底层to_thread请求的远端取消行为仍需如实评估。

## 第二轮目标进展：工具、交付事务与页面接入

本轮属于progress。三仓实时核对与上述绑定一致。未提交/发布，MVP继续active。

ML新增 document_tools.py（授权文档精读）、sec_tools.py/sec_html_fields.py（发现SEC文件、retained快照、精确cell/paragraph/XBRL）、evidence_catalog.py（保留rawEvidence并规范化）、report_tools.py/research_session.py（真实Pi宿主组合、草稿检查修订）、report_review.py（独立事实与五项编辑审查）。model-policy沿用agent_deep_research/workspace_report_semantic_verifier，仅登记新增code-path。

Backend新增research_report delivery/citation/operations；workspace_research_report_dao.py挂WorkspaceDao；研究报告版本、指针、Run/Step终态与事件同事务，hash相同重放幂等、不同内容拒绝。GET research-citations路由按owner+workspace+artifact+version+citation读取冻结bundle，不接客户端locator。source-integrity authority仍在实现，不能凭纯schema/假review通过发布。

Web页面接research-report/v1，documentJson纯正文、provenance完整bundle；新ResearchReportArtifactView展示版本限定来源、计算输入。复制/下载投影与正文一致，计算引用展开公式与输入原文。旧canonical/Markdown保留，未知/损坏research marker不回退冒充正文。新报告暂禁直接编辑/restore/分享，续研生成新版本；精确原文通过onOpenEvidence待接。

新增验证证据：主agent研究session/草稿/审查12项通过，其后session防复用旧acceptance回归4项通过；catalog+Document+SEC+session28项通过。Backend agent合同/事务/route/旧引用兼容48项通过。Web agent统一79项通过，后续证据面板及计算导出/来源集合加强12项通过（非统一总数）。未真实模型、MySQL并发、Chrome新UI验收或生产发布。

当前活跃子agent evidence_contract_audit 正在补source_integrity，已与SEC字段解析协议对齐；需要beautifulsoup4同版本以DOM物理索引一致。其余子agent工作已完成。

接下来必须完成：source integrity与independent review的真正绑定；MVP运行入口/队列调度及检查反馈串联；计算工具注册（Backend纯计算已存在但Agent尚无工具）；模型上下文预算与持久化恢复；原文viewer接新citation；实际产物质量/多来源/计算/续研验收；发布。已完成的离线模块不能替代这几项。

## L1/L2设计推进：产物、接口与迁移

本轮属于progress：读取当前三仓实现，新增06产品验收、07运行接入、08工具与恢复、09报告交付设计，并将主审决策回填00。没有修改应用代码、执行生产研究或发布。总目标继续active，MVP尚未完成。

发现并解决设计歧义：Backend要求双reviewer而ML已实现单次综合review，统一为一次独立于writer的综合审查；交付不重复审查同一冻结候选。数据库 `harness_contract_version` 有v2/v3 CheckConstraint且是执行唯一权威，不能在ContextPack另藏运行开关，决定正式增加research-v1并做兼容迁移。当前paragraph-only合同不足以承载完整财报指标表，扩展需要三仓同步。历史02的Markdown marker示例已注明为候选旧方案，避免误按两套正文接口实现。

Backend source-integrity子任务现已完成代码：SEC原文重读/精确字段重解析、authority组成，子agent报告研究相关62项离线测试通过；本轮仅主审读取未重跑，不作生产证明。Document原文reader依然缺失。

下一批按07/09先实现执行轨道迁移与研究分派、审查反馈/候选持久化，再接08计算和恢复。仍需补Document与原文viewer、表格、真实三类报告及续研、MySQL故障竞争、Chrome与正式发布。用户既定完整MVP范围没有删除。

## 实施批次：审查传输与运行轨道

本轮实际进展：Backend `check_authority.py` 已统一单个report_reviewer，新增ResearchReportReviewRejected保留具体block反馈；无问题说明的拒绝、hash错误、相互矛盾的通过仍作为技术异常。新增 `ml_service/ml_research_review_service.py`，构造时冻结问题和scope，复用内部服务身份与ML Runner配置，单次POST、不自动重试，响应256KiB上限、scope/hash绑定。对应目录README已更新。

ML新增 `research_agent/bundle_review.py` 与内部 `router/v1/research_review_router.py`，提供 `POST /agent/v1/research/review`，仅workspace-runner挂载。请求严格有界，复用服务身份鉴权，错误响应不回显原文。单次请求限一次review；全run累计预算仍未完成。

Backend新轨道底座：research_runtime/routing.py、模型列/check扩展迁移、admission与create/execute/retry/resume显式dispatch、watchdog冻结恢复预算。实际数据库尚未迁移。全部环境research-enabled关闭，缺少research_run_adapter时拒绝，不落回旧writer。完整adapter、checkpoint CAS与真实执行未实现；不可开启canary。

Web计算面板增加公式、逐项输入和原文回调，零值/负值/precision0保留；舍入规则仅有元数据时显示。主审进一步要求移除默认raw locator JSON，改可读字段定位，正在完善。原文callback仍未从Page真正接入。

本轮验证：主agent统一运行Backend review transport/authority/contract/delivery/source/route共79项通过，14项已有依赖弃用warning。子agent轨道/迁移28项通过；ML adapter及route23项通过；Web计算面板18项通过（后续可读定位修改需重新验证）。没有真实模型、MySQL DDL/并发、Chrome或发布证明。轨道agent额外旧rollout测试有3项在未修改的dirty taxonomy queryTerms处失败，主agent尚未隔离干净基线，不能笼统宣称全量检查通过。

下一步：实现research_run_adapter与ML执行入口，Backend-owned checkpoint/candidate CAS；挂权威计算工具、原文查看和Document独立验真；同步表格合同；随后真实报告/续研/恢复与发布验收。所有新应用代码仍未提交。

本批主审后修正：ML route先调用共享纯bundle校验再构造provider，坏hash不会提前初始化模型客户端，相关测试更新为24项通过。Web已移除默认raw locator JSON，展示人类可读HTML表/行/列或PDF页/行、期间/单位；未知定位不猜测，21项面板测试通过。这两组为修改后的各自focused结果，不与上一轮数量累加。

## 实施批次：持久进度、任务接线与执行传输

Backend 已增加 research checkpoint GCS 内容寻址存储、Run/Step 租约下 CAS 指针、冻结候选和单次检查后交付；草稿重新提交先使旧批准失效。内部回调从数据库取得目标、问题与执行身份，ML 不能提交已批准候选。真实 admission/executor 复用现有 Run、Step、队列和心跳，默认研究开关保持关闭。

本轮补齐 `MLResearchExecutionService`：复用私有 runner URL/身份，单次发送有界请求，保留截止时点与 checkpoint sequence，校验回应的 user/workspace/run 和状态；超时及不明确回应不自动重试。主审发现 ML 原请求合同不接受 Backend 已冻结的 asOf，正在同步修复 ML 合同和检索截止约束。Backend checkpoint/executor/callback 同时绑定 asOf，恢复不能更换研究截止时点。

本轮主 Agent 实际统一验证执行传输、executor、内部回调、checkpoint service，44 项通过；包括缺失截止时点拒绝、同截止恢复、不同截止恢复拒绝。新增与既有脏改动均保留在已确认 feature 分支，未提交或发布。Web/mobile 私有研究 execute/review 路径搜索无调用，本批未更改其公开接口。

上述是实现与离线验证，不是 MVP 通过。仍需跨服务真实链路、上传 Document 版本与原文校验、原文查看、结构表格、完整样稿、累计模型预算和中断效果恢复，最后执行真实报告与生产验收。GCS IAM、MySQL 实际并发和 Chrome 页面验证仍未证明。

## 实施批次：原文查看与版本冻结

新增保存版本的 `research-citations/{citationId}/evidence/{evidenceId}/source` 只读接口。Backend 先校验 owner、版本、引用成员（包含计算输入）、bundle 和原文字节 hash，再按保存坐标重新验真；返回净化展示衍生件，归档原文字节不改。Web 接入真实报告面板的原文入口，无权限 sandbox 展示；版本切换和关闭阻止迟到响应覆盖当前内容。

主 Agent 在 Chrome 本地真实组件预览中点击了引用和原文，确认公式、输入及来源入口可读；资料明确是合成数据，不能作为金融事实或生产端到端证明。首轮长表第36行目标不在首屏，故定位体验判为未通过；随后增加 `focusHtml` 原始目标行、`targetHtml` 来源完整表、`html` 全文三个层次，待同一Chrome场景复验。目标行不从数字搜索得到，不猜表头。

实际测试：运行/回调/持久化相关统一107项通过；原文source/routes/integrity第一版统一33项通过；增加focus后的source/routes统一20项通过。Web子Agent报告对应组件/page测试通过，完整类型检查仍存在无关基线问题；最终数量与视觉复验以本节后续追加为准，不将各轮数值累加。

现有Document库重新解析会覆盖旧页/行/表格，普通上传对象也不保证不可变。因此新增原生PDF研究冻结服务：核对owner/file/rawSHA，再以同一bytes调用现有解析器，保存raw PDF、provider JSON和解析manifest并互相绑定。子Agent报告9项离线测试通过；尚未接Backend授权附件路径、真实provider/GCS或PDF viewer；Office双原件仍缺，不宣称多信源验收完成。

线上只读复核：Cloud SQL RUNNABLE/ALWAYS，五个Cloud Run服务Ready，API健康200。两私有runner timeout均1800秒。实际补充并回读快照桶条件IAM：workspace-runner仅能在workspace-research-checkpoints/v1/创建对象，保留已有读取权限，无删除/覆盖权限。这是配置生效证据，尚未实际运行部署后的checkpoint写入。应用修改仍未提交、未发布；04中的MVP验收项全部保留。

## 本地合成UI复验与清理

2026-09-10 主Agent在本地Chrome复验新研究组件：focusHtml首屏显示真实DOM表头及目标单元格20高亮；完整上下文tab保留原始整表，完整原文tab显示标题/说明，版本提示一致。fixture明确使用合成公司/数值，source HTML由当前Backend实际source_html函数生成。属于真实组件与净化定位产物的本地交互验证，不属于真实金融报告、跨源生产链路或线上验收。Web focused tests 28项通过（source5+面板23），TypeScript本次文件无错误，全量仍有既有错误。

验收后仅删除本任务临时`output/research-report-local-preview.html`和`output/research-report-source-fixture.json`，停止独立Vite会话41167；正式代码和测试保留，尚未提交/发布。MVP仍须完成真实模型研究产物、实际信源/字段及计算、续研恢复、正式部署等04要求。

## 实施批次：报告结构表格与 PDF 私有冻结接口

报告新增真实 table block：caption、2–12 columns、1–100 rows、每行等宽cells，每cell有稳定id/text/citationIds。Backend执行全文anchor唯一、引用与计算成员校验；summary保留为审查锚点，所有其它结构不得占用。独立审查收到完整表格，反馈可指向cell/row/column。DAO Markdown投影同步支持表格以避免交付时读取paragraph.text失败，事务逻辑不变。

ML submit_report工具schema同步paragraph/table联合结构、缺失值明确标注、单元格独立引用；review指令要求核对每格的期间、单位与来源，不借邻格引用替代支持。主Agent增加跨仓检查：由Backend实际build_research_report生成bundle，验证ML实际工具schema与review接收、原样传递及cell/row/column问题回传；重签hash后的summary锚点冲突也拒绝。

Web typed renderer、validator、Markdown导出和引用点击均已扩展，语义caption/thead和局部横向滚动，管道/HTML/换行转义。旧paragraph保持兼容。当前表格真实Chrome视觉验收尚未运行，前一批Chrome通过的是原文查看，不能扩大为表格已验收。

验证范围：主Agent实际运行Backend相关63项通过（随后summary冲突修正由子Agent40项通过）；ML跨仓table/tool/bundle/review/router统一33项通过；Web子Agent统一111项通过，后补summary冲突后table专项20项通过。各次结果不累加。未调用真实模型，未发布。

PDF新增私有POST `/agent/v1/research/documents/freeze` 与 `/read-verified`，严格服务身份、host user/workspace/document/file与固定schema，默认研究配置关闭。read_verified比对解析版本/providerReceipt，重读provider JSON并用真实适配器重建全部normalized结构，防止伪造field manifest后重签hash。子Agent25项相关测试通过；Backend workspace授权附件→冻结→checkpoint→基于manifest检索的接线尚待完成。当前DocumentResearchTools不能继续对可变解析库检索后冒充冻结版本，后续必须更换读源。

下一批：接PDF授权版本获取与冻结manifest检索，研究运行中计入解析/模型预算并持久化；同时完成表格Chrome验收、真实短核验/完整财报/多信源比较与续研恢复。全部既定MVP要求保留，尚未达到发布验收。

## 实施批次：上传 PDF 授权、冻结、检索与核验接线

Backend 新增私有Document传输适配器，固定freeze/read路径、服务身份、scope/version/字段回读检查；未知请求结果不重试，仅严格422未调用证明可标记provider_call_attempted=False。新增ResearchDocumentSourceReader，限定该Run宿主冻结版本，重新核对Workspace附件与fileId，并精确重建quote/locator/provenance/source refs。

执行器先持久documentCaptures.intent，再调用freeze，再保存completed版本。唯一存储仍是原checkpoint包，ML不能修改documentCaptures。恢复只用已成功版本；未知intent阻止普通retry。已completed版本可从原Run私包重新绑定到新Run scope复用，不复制旧消息/证据身份。原Run deadline以外层timeout覆盖冻结、模型和交付，避免恢复重新获得完整时间预算。

Callback从宿主包读取全部completed版本，文档集合必须等于admission附件集合，再构造Document reader。ML execution改用ImmutableDocumentResearchTools，对验证后manifest进行有界词面检索、分页精读与字段引用，不再查询可变DB解析结果。PDF目前是文本证据，未伪造typed财务数值。

主审发现孤立PDF单元格丢表头/单位风险，已将同页context纳入raw evidence hash并投影给独立review；Backend核对normalized/raw/原文回读context一致。超过200KB上下文拒绝引用而不截断；换同页span不能绕过，该限制仍待更细上下文合同完善。此上下文补充不替代OCR准确性审查。

主Agent统一运行Backend传输、reader、callback、source integrity及document execution/executor/checkpoint/admission相关101项通过。ML子Agent此前28项通过，context补充专项12项通过；均为离线与真实parser适配器替身测试，没有实际付费解析。实际为ML runner补上documents/sha256前缀的只读桶权限并回读，避免create成功后无法verify；生产解析和模型请求仍待真实验收。

未提交/发布，研究开关仍关闭。尚需PDF原文viewer、表格Chrome验收、整条真实研究/完整报告/多来源/续研恢复及生产发布。04要求不变。

## 真实模型首轮 canary：发现检索接口问题

2026-09-10，主Agent在隔离本地双进程中运行真实Pi/Vertex/SEC工具及Backend核验服务，项目明确固定cited-alpha-20260701，使用ADC，未修改生产配置。问题为Tesla 2024年度财务表现，未向模型预填财务答案。预算12次writer、24次工具、2次独立review、600秒；本轮最终incomplete/model_error，实际计数10次model、9次tools，9次返回usage，review0、证据catalog0，没有accepted报告，不能算报告验收通过。产物保留于/tmp/cited-alpha-tesla-2024-canary-01，尚未发布。

工具已真实找到并读取10-K；read_filing把段落和表格分开排序，标题附近读取难以获得相邻表格；每个单元格重复table_context，3次结果约43,741/39,807/18,947字符，模型输入从约4千增至5万token。最后model_error仅host_execution_failed，尚不能认定为配额、输入上限或网络。后续先增加安全错误分类、压缩展示冗余、改善导航与预算反馈，保留永久证据定位及原文完整性，不预填答案或降低报告检查要求。

本轮之前整组研究测试Backend242项、ML129项通过（ML含真实Pi进程）。这些验证没有预测到真实研究行为及接口效率问题，后续验收仍以真实报告和Chrome来源核对为准。

## 结构表格与PDF本地合成验收

Web新增结构table block、全篇唯一锚点（summary保留）、逐cell引用、语义表头与横向滚动、Markdown转义导出。新增PDF source分支和认证source-file读取，真实pdfjs canvas禁eval/XFA，打开Backend 1-based指定页；非法页失败不clamp。分页、缩放、返回引用页、失败重试和版本切换取消已实现。当前Backend bboxNormalized=null，页面明确页级定位，不猜字段框。

本轮统一105项测试通过：PDFservice8、table20、PDFcanvas5、HTMLsource5、页面67。TypeScript新增union的2项scope类型错误已修；最终本次Research/research/page/workspaces文件无错误，全量仍有既有基线错误。git diff --check通过。未提交或部署。

主Agent在真实Chrome查看本地合成fixture，确认表格金额单元格点击后canvas显示第2页20 million USD；上一页切换第1页10，返回引用页恢复第2页；截图确认真实canvas文字和明确页级定位提示。该证据仅证明本地真实组件交互，资料和数值均为合成，不证明真实金融产物、跨源生产链路或PDF字段框选完成。

验收后仅删除`output/research-pdf-table-preview.html`和`output/research-pdf-local-fixture.pdf`，停止独立Vite会话26012。正式代码与测试保留。当前真实canary未获得accepted产物，不能用合成fixture替代MVP验收。

### 下一次真实accepted bundle的临时阅读方案

只有真实canary成功且Backend已接受、完成owner/snapshot/语义检查的bundle，才可进入这一预览。记录runId、artifactId/versionId、bundle contentHash、documentChecksum及原文snapshot关联；从owner限定API/数据库只读提取本次版本，保留原始document/citations/evidence/calculations，不重写正文、不补数字、不将失败草稿改标accepted。

优先通过正常工作区页面读取已持久化版本，验证实际GET来源与source/source-file链路。若真实accepted bundle尚未接入可运行本地业务页面，可建立一次性localhost预览，直接import现有ResearchReportArtifactView，使用该原始bundle；仅本地不提交的fixture文件，明确“真实canary产物的本地展示，非线上验收”。来源请求优先通过本地受授权Backend，不将生产token写进HTML/fixture。若只能离线显示bundle，则禁用原文操作并明确溯源端到端尚未验证；不能用合成source response或外部URL伪装真实快照。

展示前核对同版documentJson/provenance一致、hash及accepted记录；展示后逐段人工评阅报告质量，检查表格指标/期间/单位、cell引用和计算输入。只有真实返回的原文可作为溯源验收证据。截图/导出应标记实际版本、数据截止时点和本地/线上范围。结束删除仅本任务临时数据并停止本任务进程。当前canary失败，因此暂不制作这一真实报告预览。

主Agent后续独立复跑PDF source/routes/HTML source：29项通过，14项既有依赖弃用警告。Canary已返回usage合计input229742、output716、thought2565、total233023，其中cachedInput140882；这些是provider记录的token用量，不是费用估算，失败调用未提供usage。不重试未知结果以推定免费。

## 实施批次：按需研究方法与第二轮真实验证

新增ML纯服务research_methods.py及read_research_method工具，六类方法为事实核验、财报分析、公司研究、比较研究、事件影响、估值研究。会话仅带短目录，模型按需读方法；没有关键词分类器、强制维度、额外模型场景或专用执行流程。用户范围优先，方法不能发行证据或通过报告检查。已有调用上限和checkpoint覆盖方法读取。session/执行相关14项通过，随后新增方法不能冒充证据或交付的测试后session5项通过；不累加为同一测试集。

SEC修复使用真实已捕获Tesla快照离线对照：汽车收入43,741→6,578字符，经营现金流39,807→7,951，capex18,947→3,954；永久paragraph/table/cell编号不动，增加派生DOM导航、标题邻接、词项回退与展示字节预算。工具反馈剩余预算和证据数量，模型错误保存安全类别。子Agent27项通过，包含真实Pi及快照验证。

第二轮相同Tesla问题及12writer/24tools/2review/600秒预算正在运行，产物目录/tmp/cited-alpha-tesla-2024-canary-02。最终结论待实际result与报告核对，当前不声明通过。

第二轮最终结果incomplete/model_budget_exceeded，12model/12tools，已登记3条真实字段证据，modelDiagnostics为空，未submit、未review、无accepted报告。与首轮model_error不同，本轮明确为调用预算用尽。首个find_filings同时给ticker/entity被互斥校验拒绝，暴露schema说明与固定修复反馈不足；正在修复。下一轮完整报告计划显式32model/64tools、2review、600秒预算，不扩报告成功标准，不修改已结束运行的原始记录。

PDF几何子方案已实现真实pdfjs PageViewport金标与ML/Backend接线，子Agent报告ML27项、Backend18项通过；指定documents/sha256归档为空，尚无真实DocAI frame证据，生产仍返回page。准备两页合成PDF真实单次解析，以原始provider结果和Chrome坐标比对决定可支持frame；几何数学测试不替代解析行为验收。

## 真实解析基础设施与网页入口核查

主Agent实际启用cited-alpha-20260701的Document AI API，操作成功；在us创建OCR_PROCESSOR，HTTP200/ENABLED，身份projects/829189946367/locations/us/processors/ba7872f1c0ed02be，默认版本pretrained-ocr-v2.1-2024-08-07。创建处理器不等于已解析，尚待两页样本单次请求及原文坐标核对。未修改旧项目配置或创建重复处理器。

Web真实入口审查发现conversation/stream携带chatSessionId/messageId/selection，而research admission严格字段集拒绝；activeArtifactId路径还缺baseVersion。正在修复实际入口归一化与权威版本冻结、兼容旧客户端，不能只用本地绕过admission的canary宣称生产可用。

第三轮财报研究正在运行，预算32model/64tools/2review/600秒。已通过真实原文校验取得收入97,690与96,773字段并完成growth_rate计算，仍须等待完整正文和独立审查，当前不声明P1/Q1通过。

第三轮最终24model/23tools时provider_quota失败，modelDiagnostics有明确quota类别；原进度保留8条字段证据与已完成计算，无pending intent，无candidate/review。正在准备严格同scope/asOf/原deadline/累计预算的host明确续接：仅移除末条空失败assistant，原产物只读，不重放已完成工具，不重置预算。

主Agent实际执行两页原生PDF单次DocAI请求成功，原始response/provider/manifest/version留在pdf_geometry_acceptance/real_canary_20260910；版本dv-f89e51e1de4ef1a4f745a2517b1e1c5c7fa1c9deaf4548abdb256132496ca862。此次使用真实processor与本地限定repository/store，未写生产业务DB，不能据此宣称DAO入库或跨源生产链路通过。实际provider坐标支持进一步判断未旋转CropBox映射，尚须Chrome真实字段叠框。生产资格不能按验收文件SHA硬编码；SHA只做版本绑定，支持范围需由processor/frame规则及PDF特征定义。

### 2026-09-10 真实 conversation 入口与版本冻结修复

Web 原 conversation stream 增加 optional baseVersion；续研传正在查看的文档版本。Backend route 透传，research service 归一化匹配的 chat/message transport 字段，非空 selection/skill 覆盖明确拒绝。只有 evidence 命中新 lane；普通 chat 与未启用工作区保留旧 lane。DAO 在原子事务中锁定当前 artifact 版本，旧客户端遗漏版本时使用权威 current_version；显式陈旧版本拒绝。create_new 分配独立 artifact、空 v1 和 Run；已有 primary 保留，重放复用冻结 target。

实测 Backend 64 tests passed（包括挂载 FastAPI HTTP/SSE→实际 ORM admission、缺省版本冻结 current=3、陈旧版本冲突、新建独立产物与重放）；Web 94 tests passed。全量 tsc 仍有既存基线错误，本轮页面/service 无错误。移动端 API 目录检查未发现该 Workspace conversation route 消费者；字段为可选，旧客户端请求兼容。测试中 auth、chat persistence、dispatch 与 Run 观察使用替身；不代表真实模型报告成功或 MySQL 并发锁/线上验收。未部署，未修改 PDF 查看器。

主Agent在Chrome localhost:8796独立复核真实解析叠框：正常页Revenue/Costs120各自准确，第二页Rotate90+非零CropBox的Revenue/Costs240及标题均准确覆盖实际文字。同数值未串位。此为真实provider polygon+原件+pdfjs本地验证，不等于完整报告API或生产上线验收。研究freeze后续将绑定受信processorVersion/mode/options，并按官方同步API上限定义能力，不能把2页验收样本变成产品永久2页限制；较长PDF原能力保留，未知坐标声明page。

财报03在原scope/asOf/原deadline与累计24/23预算上明确续接，resume01再以provider_quota失败（新增1model、0tools；累计25model），未重放完成工具，原记录只读。监控确认模型global/shared/standard的429，ServiceUsage没有该model固定bucket的直接证据，尚不能断定固定额度或动态容量。未擅自切模型或再续期预算。短核验是原MVP P2的独立验收，不替代P1完整报告。

## PDF 字段坐标真实样本与受信在线 OCR 接线

2026-09-10：Root 单次真实 OCR 留存两页合成原件，子审及 Root 独立 Chrome 均确认
六个 provider 派生框准确覆盖文字；Rotate90/CropBox 页的 Revenue/Costs 同值未串行。
详见 `pdf_geometry_acceptance/README.md` 与真实 `real_overlay_candidates.json`。
这是原件/provider/PDF.js 几何验收，不冒充完整产品授权 API E2E。

ML 新增 `document_online_provider.py`，15 页以内固定本项目 processorVersion 的单次
在线 OCR，native 选项冻结进 immutable manifest 的 providerExecution；较长 PDF
保留原 batch 及100页总预算。geometry 按已支持 native/rotation/crop/transform 特征
计算，未知/batch/旧 manifest 降级 page，SHA 仅内容绑定而非文件资格白名单。

Focused tests 38 passed：在线单提交/超页/manifest执行参数/长PDF路由、真实6框回归、
PDF.js 8组viewport金标、旧版本replay、auth路由、batch单提交。没有新增付费调用、
生产写入、提交或发布。受信在线身份必须为本项目 ADC，另项目身份失败关闭。

### 2026-09-10 历史版本只读浏览与防漂移

Web 增加独立“查看版本”动作，恢复动作保持分离；研究报告恢复禁用并说明。精确 artifact/version resolver 不再将缺失历史版本回退为 latest。历史正文、报告 provenance、引用及原文请求共用所选 version；背景 Run 回读保留手动浏览位置，返回最新为显式动作。续研传正在查看的 baseVersion，服务端冲突拒绝避免覆盖。旧版不允许编辑/分享；不可用版本禁用导出并给明确提示。历史列表请求加代次防旧响应覆盖新产物。

Focused Web：98 tests passed（页面 68、版本导航/精确 resolver 2、研究引用23、原文5）；tsc 仍有既存基线错误，本轮文件无错误。提供127.0.0.1临时真实组件预览给主agent Chrome验收；正文和来源为明确标注合成数据，HTML使用 Backend source_html真实净化输出。本记录时 Chrome 尚未回报，不宣称真实金融报告/线上验收。

历史版本 Root Chrome 实际验收补充：使用 localhost 本地临时预览，选择 V1 后正文合成标记10、引用标为 V1且请求路径 versions/1，原文实际高亮10；切换 V2 后旧来源面板消失，新引用标记20且路径 versions/2。返回 V1并模拟该版本缺失，页面明确不可用，截图确认没有显示最新版正文。首次临时页白屏来自直接导入 Vite 预打包 React文件绕过 CommonJS转换，已将临时入口改为裸模块导入后完成上述验收。

范围：真实版本导航/resolver、报告/引用/原文组件及 Backend source_html净化输出；HTTP服务响应与数值均为明确合成验收数据，不是生产DAO、真实金融产物或线上全链路验收。父agent已关闭tab；两个临时fixture（research-history-local-preview.html、research-history-local-source.json）已删除，Vite session99698已停止。正式代码与测试保留。

## 短核验恢复与检索质量反馈

短核验问题“核对Tesla2024年总收入，并说明单位与财年口径”首轮第2model出现429，无证据；主Agent查实际google.genai.errors.APIError源码发现异常JSON在details属性，修复隔离canary诊断并以真实ClientError离线验证安全分类，不打印原始消息。

随后同scope/原deadline/累计预算续接，模型请求恢复，无新provider错误，但最终model_budget_exceeded（本次10model/10tools，加原2model累计12），仍无candidate/review/accepted。实际轨迹多次长查询exact/allterms无命中、标题邻接和表内翻页，暴露自然语言检索效率不足。下一步用真实留存原件与实际query验证BM25相关排序，保留exact/title加权和永久字段定位，不把候选当证据，不以加预算替代质量改进。

ML依赖锁定和CI镜像内断网Pi smoke已实现；子Agent构建合同2项、公共lock干净安装后的Pi9项通过。主机无Docker，未安装服务或本地构建，镜像内实跑必须由后续CI证明，当前不声明O1完成。

## 整组回归、权限回读与计算拒绝边界

主Agent当前整组Backend267项通过；ML159项通过、2项需原件路径先skip；随后显式传入已留存SHA命名Tesla HTML，2项快照回放均通过。没有把skip当通过。最终实际Pi→service→Vertex SDK离线wire审计证明工具/schema/system与动态预算均到达，未发现传输丢失；新增深等测试1项通过。

主Agent给实际ML runner SA新增本项目roles/documentai.apiUser，以及private workspace-runner服务级roles/run.invoker，并分别读回true。未公开服务或更换运行镜像。应用allowlist由Backend部署工作流准备保留dispatch并追加ML身份，10配置测试/19段shell语法通过；开关与新版本仍待受控发布。

短核验03改用32model/64tools/2review/600秒，属于真实轨迹证明原12次诊断窗口不足后的明确预算，不降低检查标准。实际推进到sum后，因财务entity/dimensions不匹配被拒绝；临时authority把ValueError转503导致ML PiHostFatalError，运行exit1，无报告。这暴露了业务计算拒绝与基础设施失败混淆。下一步采用专用计算rejected回执、不生成计算ID，Agent可调整输入或使用原披露值；来源/权限/网络失败仍fatal，不放宽sum的可比性规则。原运行产物/tmp/cited-alpha-tesla-revenue-factcheck-03保留。

## 同任务计算恢复后的真实报告提交观察

Root回读session46012：纯计算重验产生rejected_calculation_recovered，未产生计算ID或模型调用。recovery-audit.json绑定原件哈希、原scope、累计15model/15tools及原绝对截止时间2026-09-10T11:07:58.126778Z。

Root在该截止前执行明确续接（session24577，产物/tmp/cited-alpha-tesla-revenue-factcheck-03-resume-01），终态incomplete/output_truncated，累计18model/16宿主工具；新增3model/1宿主工具，review为0，无accepted或正式候选。最后调用thoughtTokens7860/outputTokens328，触及8192输出预算；终止原因是输出截断，不是本轮provider quota。没有给原任务续期或追加预算。

两个具体问题改变下一步实施：

1. 恢复后SecResearchTools只恢复discovery/catalog，原文_reads/seen为空；模型直接引用此前字段收到host_contract_failed。需提供受信read_required及准确重读参数，重新校验原文后才允许引用，不从模型参数补造已读状态。
2. 模型首次submit_report把summary放到根、用document.heading/id并漏schemaVersion，Pi验证正确拒绝，但required错误显示路径document.schemaVersion，诱导模型将该字段误解为对象。应验证错误路径与可执行修订反馈，补充不含财务答案的最小合法结构说明；保留正式合同及独立事实检查。

短核验的新增输入token为60514、62070、71325，说明检索轨迹/上下文效率仍需优化，不能只靠增加调用次数。实际收入正文已出现，但格式提交未通过，且事实支持仍未审查；不计为P1/P2/Q1完成。

Root独立回归：Backend test_research_calculation_service.py + test_research_callback_routes.py 共35项通过。上下文测量按工具content文本而非包含details的整个消息：5次read_filing约115KB；引用重复table_context共9012字节，唯一1502字节，单纯去重至多减少约7.5KB，不能据此断定已解决上下文效率。

## 恢复反馈、参数诊断与单次响应上下文去重

Root完成SEC read_view单次响应内无损去重：表格行通过context_ref关联本响应source_contexts，完全相同的table_index/context/nearby_headings只保留一份；不同背景不合并，每次分页独立携带完整背景。没有跨消息压缩、证据裁剪或修改parser与永久引用。新测试逐行重建后与原compact结果深等，原输入不变，分页不依赖前次响应。更新既有断言后，Root实跑16项SEC/恢复/真实Tesla原件测试全部通过。

Pi adapter补精确JSON Pointer参数错误：复用Pi校验，不派发非法工具；required兄弟字段独立说明并保留const/type期望。Root实跑11项实际Pi测试全部通过。SEC read_required引导恢复进程真实重读，引用身份保持一致。研究batch另修AuthorizedSession 401付费POST重放问题，子审11项通过，等待整组回归。

Root启动新短核验04（session1196，/tmp/cited-alpha-tesla-revenue-factcheck-04，32model/64tools/2review/600秒），验证上述修复后的真实产物；这是新独立run，不给旧run延长deadline。启动时尚无通过证据。

上述集成后Root整组ML test_research_*.py实际169项通过、1项既有warning，显式提供SEC原件路径，无skip（session16739）。覆盖此次SEC响应共享/恢复、精确参数反馈、真实wire和DocAI单提交。真实短核验04继续运行，尚不能以离线回归替代报告验收。

短核验04终态ready_for_delivery（session1196 exit0），真实source/check得到accepted。但Root人工审阅发现summary/正文增长未绑定计算引用，以及把报表列报币种扩大成记账本位币；Q1仍未通过人工验收。原candidate/accepted/request/runtime/usage及SHA已沉淀actual_report_acceptance/short_04，不修改原回执。后续按实际陈述的引用边检查事实支持，而非看到报告其他位置有同一证据就默认全篇支持。已有真实正式候选说明格式修复有效，不能由此宣称MVP交付。

## 按锚点绑定的真实重审与完整财报04

Root独立20项review相关测试通过，单次真实重审session76404 exit0：原short04同一contentHash被新reviewer v2拒绝，准确定位summary、txt_verification_p1的2023收入/增长引用缺失，以及txt_unit_p1的金额和本位币支持缺失。结果保留actual_report_acceptance/short_04/review_v2；不修改旧accepted、不宣称重新完成来源校验。

Root启动完整原问题财报04（session91539，/tmp/cited-alpha-tesla-2024-canary-04），32model/64tools/2review/600秒，使用新检查与无损上下文展示。当前尚无报告通过证据。完整财报要求不以短核验替代。

ML发布Secret数字pin已实现未部署。Root检查workflow/helper并运行13项release/runtime-build测试通过：同镜像不能跳过已固定配置，CI发布一次解析数字Secret，API与runner共用，回读实际revision引用。历史latest回滚限制保留说明，未改Secret/IAM/线上镜像。

## 真实候选的Chrome原文与计算查看

Root在Chrome tab1044432687验证localhost:8099的short04原candidate：点击97,690引用显示2024期间，打开原文定位正确高亮Total revenues的97,690；完整上下文原表显示Year Ended December31及2024/2023/2022各列。点击0.95%显示真实公式(97690000000÷96773000000−1)×100、precision2及两个原始输入；点击输入2正确高亮96,773，未串到2024单元格。截图与AX均实际回读。

范围：真实报告bundle、实际React报告/来源/计算组件、Backend真实source_html净化及留存SEC原件；引用HTTP由明确本地适配器提供，不是生产DAO/API/权限验收。报告仍为人工要求修订的原稿。发现单位iso4217:USD重复、长数值未分组、输入期间不直观，正在按真实字段改善展示；不改原报告或引用身份。

完整财报04终态provider_quota，12model/11tool，无证据/候选；Root在原截止11:25:30Z内同scope续接（session31002，目录canary-04-resume-01），当前继续研究。未给旧run加预算或续期。

完整财报04续接最终model_budget_exceeded，累计32model/31tools，仅4条证据，未提交候选。轨迹中19次read占主要研究开销；之后仍需引用、计算及修订。批量引用已实现（子审25项通过），下一轮采用新的明确更大预算，不能以32次诊断限制倒推缩小完整财报范围。旧运行预算不变、不恢复已耗尽的run。

Root再次Chrome回读UI改进：同比公式千分组、两个输入直接显示2024/2023完整期间，金额以美元展示。又发现quote原值97,690旁仅标“原文单位美元”会混淆币种与scale，已要求按实际XBRL scale6区分原文百万美元和规范化美元金额，后续继续复验。

Root验证新增批量工具的SEC/实际Pi恢复/最终wire14项通过。完整财报05已启动（session32175，/tmp/cited-alpha-tesla-2024-canary-05），明确新预算64model/128tools/2review/1200秒；隔离canary入参边界同步扩展且py_compile通过。生产默认配置未变，旧run仍恢复其原预算，不以提高canary上限复活耗尽任务。真实产物待回读，完整MVP仍未完成。

Root Chrome最终金额语义复验通过：原文摘录97,690、币种美元、单XBRL scale6明确按百万美元列示、标准化97,690,000,000美元分别显示，2023对应96,773及96,773,000,000；公式和输入期间正确。52项Web focused tests由子审通过，本轮未修订旧candidate。Root关闭1044432691，临时预览交由子审清理。

完整财报05在10model/9tools时provider_quota 429终止（11:21:19Z），无候选。Root在约88秒后明确同scope/原deadline/累计预算续接一次，目录canary-05-resume-01，等待实际结果。原件和原run记录不变。

真实API准备发现ENV_MODE=local仍指现有远端MySQL，不能直接启动迁移。正在按云SQL MYSQL_8_0匹配准备独立本地MySQL8.0（127.0.0.1:13306，/tmp隔离数据目录），不写云端业务库。后续需要真实admission/Run/checkpoint/Artifact验收，不能用SQLite测试替代MySQL行为。

### 2026-09-10 short04真实候选的Chrome展示验收

Root使用本地Chrome实际查看未改写的short04 candidate：收入引用进入原始SEC保留快照，目标97,690高亮，完整表格年度列可见；同比计算显示真实输入与公式，切到第二输入可定位2023数值。经实看修正显示后，再次截图确认原文97,690、币种美元、按百万美元列示、标准化97,690,000,000美元明确分开；公式使用十进制字符串千分组，输入标题显示真实2024/2023期间。仅单个typed HTML XBRL事实的显式scale6用于说明百万列示，不对OCR猜尺度，不从原文摘录在浏览器计算标准化事实。候选没有rounding或roundingMode，因此不补造历史舍入规则。

Focused tests：52 passed（Artifact27、table20、source5）；全量tsc仍既存基线失败，本轮文件无错误。candidate与原/tmp canary逐字节一致。本地真实组件消费实际候选bundle和真实SEC快照；来源响应通过明确标注的本地适配器提供，HTML由Backend source_html净化，7条实际locator逐一核对quote（仅忽略HTML节点空白差异）与快照SHA。该验收证明候选显示和本地来源/计算交互，不代表候选已获人工通过、已入库生产DAO、生产鉴权链路或线上部署成功。页面始终标注真实候选、人工要求修订、未上线。

Root已关闭Chrome tab1044432691。仅删除本轮Web三个临时fixture（research-short04-local-preview.html、research-short04-local-candidate.json、research-short04-local-sources.json）与/tmp/cited-alpha-short04-source-preview.html，停止Vite session14043。原/tmp/cited-alpha-tesla-revenue-factcheck-04和actual_report_acceptance归档原件均保留；正式UI及测试未再改动。

完整财报05首次续接session24102已终止：新增3model/2tools后再次provider_quota 429，累计13/11，无候选；不是预算耗尽。当前不连续快速重试。准备一个明确的低频调用诊断，等待计入原任务绝对deadline且仍按原预算累计，不切模型、不假定已证明RPM限制。同时审查连续续接必须沿用经审计的原absoluteDeadline，不能从已缩短的duration再次错误重算。

本地MySQL8.0安装由子审执行中（brew session39583），目标独立目录/tmp/cited-alpha-mysql-e2e、127.0.0.1:13306、关闭mysqlx；未启动全局service或连接云业务库。现有short04临时预览4文件已清理，14043终止且8099释放，实际原件保留。

## 隔离MySQL就绪与有界低频续接

本地真实MySQL8.0.46已启动，127.0.0.1:13306、database research_api_smoke、datadir /tmp/cited-alpha-mysql-e2e/data。凭据仅本地600文件；无云业务DB写入，尚待业务schema和API烟测初始化。下一步由真实FastAPI与MySQL驱动验证admission/replay/版本及持久化，外部调度与付费调用边界分别记录。

隔离canary新增可选模型最小间隔，首调用也等待，writer/reviewer共享间隔，所有等待计入原deadline。连续resume沿递归原件hash/scope/question/asOf审计恢复原绝对deadline，避免从已缩短duration错误二次重算。2离线测试由子审通过。Root启动05-resume-02（session60776），20秒最小间隔，沿用原11:40:32Z截止与累计13model/11tool；未切模型、重置预算或改生产。该诊断不预设429由调用频率导致。

三仓origin/main已实际fetch回读成功：Backend24b91fb、ML9a6c7e4、Web8333a28。当前绑定HEAD均为主干祖先，behind分别8/11/4，ahead均0；此前未fetch的2/2观察已过期。没有切分支、merge/rebase、stash、stage或覆盖dirty。发布候选需验证最新主干与本任务选定diff的组合，不以当前旧HEAD本地测试直接证明合并后可发布。Backend只读候选文件哈希清单/tmp/cited-alpha-backend-release-scope.json；Web逐hunk清单/tmp/cited-alpha-web-release-scope.md，均未暂存。

## 隔离真实 MySQL / API 接纳验收

本机MySQL8.0.46仅127.0.0.1:13306/research_api_smoke，当前ORM schema56表建立；
expand_workspace_research_track在当前schema幂等执行成功，不能等同旧生产schema升级证明。
真实FastAPI ASGI路由、签名JWT/真实UserDao、正常POST/workspaces及Chat绑定、POST/runs
接纳/replay/冲突、坏JWT拒绝、SQL独立回读Run research-v1/唯一Outbox/初始Artifact通过。
baseVersion冲突与create_new通过真实service/DAO验证，尚非conversation HTTP覆盖。

可执行入口Backend `mindspace/script/research_mysql_api_smoke.py`；600配置在
/tmp/cited-alpha-mysql-e2e/backend-smoke.json和ml-smoke.json。ML实际MySQL键database
已正确覆盖并回读13306，另Postgres禁到127.0.0.1:1避免访问远端Document store。
脚本仅hold dispatch且拒绝外网socket，无DAO/SQLite替换，无模型/邮件/云端业务写入。
结果api-smoke-result.json留存明确proof字段。checkpoint对象/检查回执/最终report交付
尚待下一步真实持久化验收，不拿当前初始Artifact当生成报告。

## 检查器真实正反样本

Root 单次真实 review（session35853 exit0）通过人工修订的 short04 fixture：补齐局部引用并修正不受支持的本位币断言；已有 evidence/calculation 均不变。verdict semantic/editorial passed，1 次调用，input31266/output74/thought1899 tokens。归档 actual_report_acceptance/short_04/review_v2_positive_fixture。与原稿被 v2 拒绝的记录构成正反回归；不能称为 Agent 自主修订或完整财报产品验收。

### 隔离真实 MySQL 后半段通过

`research_mysql_delivery_smoke.py` 已执行成功：消费前段真实API生成的queued Run，
实际claim Run/Step，再走生产checkpointStore/service与MySQL DAO。GCS transport
由本地磁盘fixture实现，不是内存对象；authority回执明确标注
explicit-local-storage-fixture-NOT-model-review，不冒充原文检查或模型审稿。
新service实例从SQL指针+磁盘恢复，旧sequence重复回调拒绝；检查候选保存到seq3，
首次交付V2、Run succeeded，再次deliver返回同versionId且fixture审稿仅1次。
真实JWT citation路由读取成功，错误版本与另一个真实user签名token被拒。
最终Run workspace-run-91097259a69642ca99c1c0ebc605c56b，版本
research-version-ee3344b5-8da2-5fe3-ba42-cbb694deecbc，结果仅在本地隔离库与
/tmp/cited-alpha-mysql-e2e/delivery-smoke-result.json。diff检查通过。

边界：ASGI应用没有生产startup调度；前段dispatch held；后段直接service调用保存/
check/deliver，没有走真实OIDC callback HTTP或模型/GCS/source-file。不是完整财报E2E。
第一次脚本断言把实际passed写成accepted而失败，已修fixture断言；旧测试行保留，
后续用新API创建Run重跑。没有修改生产业务、发布或提交。

## 隔离候选与真实持久化补验

Root 以 origin/main24b91fb archive 创建普通临时目录，覆盖选定的78个本任务文件；不建分支、不改 index。初次测试因候选没有主机本地 Mongo 配置在收集阶段失败；显式使用隔离 smoke 配置后277 passed、1 failed、1 skipped。唯一失败准确揭示发布清单漏了旧 add_workspace_harness_contract_v3 的 VARCHAR32/research-v1 兼容两处变更；已补入清单与候选，迁移4项复验通过。skip为隔离目录没有ML sibling的可选解析器一致性比较，非主功能测试。Backend HEAD和origin/main tree均d72e4b01ce8e0acc57337619dcf890b61830e406，提交落后没有源码差异。

子审完成真实MySQL后半段：checkpoint保存/新实例恢复/旧sequence拒绝、receipt绑定、V2与Run终态原子写入、重复交付同versionId、真实JWT引用查询及错版本/跨用户拒绝。Root回读脚本与delivery-smoke-result.json。对象传输为本地磁盘fixture、authority明确fixture标识；没有将其冒充模型/GCS/OIDC完整链路。

完整财报05低频续接02终态incomplete/provider_quota，已有22条证据与4项计算，未交付。Root保持同scope、原11:40:32Z deadline及累计预算启动resume03（session29757，30秒间隔含首调用），无重置预算/切模型。降低频率仍429，未证明频率为根因。

## 旧schema真实升级验收与发现的发布阻断修复

独立本地库research_migration_smoke_v2，从最小workspace_runs VARCHAR8/v2-v3 CHECK
及两条旧行开始，实际执行expand→兼容旧v3脚本→插入research-v1→两脚本再次重放。
MySQL8.0.46回读旧值保留、VARCHAR32、新CHECK保留，两个cycle通过；相关离线8项通过。
此为最小旧表升级证明，不代表全生产schema已迁移，原research_api_smoke表未动。

真实测试先暴露1845：约束DROP+ADD不支持INPLACE/LOCKNONE。Root批准后修为单条
ALGORITHM=COPY,LOCK=SHARED，避免无约束窗口，但阻塞写并可能复制全表。发布前
必须核对生产表大小、停止接纳、排空写入并安排窗口；不能按在线无锁DDL发布。
未执行云迁移。脚本research_mysql_migration_smoke.py及migration-smoke-result.json
保留具体证据，diff检查通过。

## 三仓隔离发布范围验证

Web子审由origin/main8333a28 archive覆盖审定21项，临时普通目录、未建worktree，181项组件/服务测试与22项脚本测试通过；生产构建成功（35预渲染路由、PDF worker）。候选和另一个纯主干archive实际运行tsc均42条，完整日志逐字相同，0新增；旧41条日志受旧marketing dirty掩盖一项主干错误，已纠正。结果路径见/tmp/cited-alpha-web-release-scope.md。

ML子审隔离候选/tmp/cited-alpha-ml-candidate-s2p_uk54：portable Python167通过无skip、Pi Node11通过、部署契约19通过，没有发现对排除旧dirty的依赖。CI新增从同release image派生的断网Python测试镜像与显式文件清单，任何skip失败；3类本机/跨仓golden单独列边界。本机无Docker，尚未证明Linux镜像构建。范围与SHA在/tmp/cited-alpha-ml-release-scope.md，未提交发布。

## 截止时间反馈修复与下一轮真实报告

完整05-resume03在原11:40:32Z deadline被取消，累计48model/45tool，28条证据、9项计算，无candidate；一个纯calculate intent未回执，保留unknown状态，不复活过期run。没有把原限额延长。

发现并修复：Backend外层按Run deadline终止，但原来向ML转发原duration；现在真正dispatch前deepcopy并裁剪floor剩余，低于1秒不发，31项回归通过。ML同一单调时钟驱动实际timeout与每轮remainingSeconds，宿主可显式传绝对deadline，不把asOf当运行开始；14项focused及候选170项portable通过。

Root在独立canary脚本传已审计absolute_deadline；新run允许最大1800秒，默认600不变。完整06启动，64model/128tool/2review/1800秒，20秒最小间隔；新scope独立运行，不重置05预算。完整报告仍待验证。

## 2026-09-11 续行：ML 精确提交与真实报告未完成

Root重新核对ML仓库/分支/worktree/HEAD，审定manifest92文件无hash漂移。精确暂存后逐文件核对Git index SHA与候选相同、diff check通过，提交b0525aeb3d1d5cf371e07b8b026b742727aef4fb并推送同一feat_codex/financial-report-agent-plan-writer-20260717。原Need/writer等29项tracked及2项untracked工作保留。ML本会话HEAD基准随本次提交更新为b0525ae；Backend/Web未提交。准备draft PR仅获取Linux构建证据，不合并部署。

第六轮session59267实际终态incomplete/provider_quota：13model/12tool，无证据/候选，429时间2026-09-10T11:46:34Z。原deadline12:12:14Z已过，不续接或延长旧run。下轮研究验证须处理provider可用性及效率，不能用编排/构建测试冒充高标准财报完成。

ML draft PR https://github.com/NolanSoloBuilder/mindspace_ml_backend/pull/32 已创建，head b0525ae；Linux gate run34552556062实际in_progress，watch session83209。未merge/deploy。

下一轮诊断注意：隔离canary强制VERTEX_AI_GENERATE_RETRY_ATTEMPTS=1，生产Vertex client默认4次带指数退避；两者在429恢复行为上不同。尚未使用默认retry跑完整新报告，不可将所有单次429诊断结果泛化成生产必然失败。若验证重试，需要明确记录逻辑模型调用与实际provider attempt的边界、累计预算及绝对deadline，而非静默改变旧run。

## PR Linux 镜像已通过；生产重试策略报告验证启动

Root回读run34552556062终态success（research-image 2m15s），日志/tmp/cited-alpha-ml-pr32-linux-gate.log：真实production Dockerfile镜像构建成功、镜像内Pi Node11pass/0fail、隔离Python测试镜像172passed/1warning。是head b0525ae的PR Linux证据，不是生产部署或报告验收。PR32仍draft。

Root核对本机Google GenAI SDK：retry_options=None时内部stop_after_attempt(1)，应用Vertex客户端默认最多4次退避。隔离canary新增显式--provider-retry-attempts=4新run选项，旧默认1不变；记录每次SDK generate_content开始/返回/错误，仅模型名/时间/状态，无请求正文。新run07 session32274：64逻辑model、128tool、2review、1800秒；合计SDK generation上限(64+2)*4=264，SDK内部retry需None，20秒间隔约束外层调用；内部退避沿生产实现。此次不把logical调用数等同SDK请求数，不允许多attempt旧run未经审计resume。生产配置未修改。

## Backend 合并前验证与精确提交

新增Backend PR生产镜像构建/断网测试gate，无云凭据或写权限。显式22文件测试清单使用dummy本地配置，socket禁止，意外skip失败；仅明确deselect依赖兄弟ML checkout的一项可选比较。当前工作区和排除旧dirty的主干隔离候选均271passed/1deselected，YAML及各run shell语法通过。

Root将既有research范围、纯research近层README、三个明确本地MySQL smoke及新gate共92文件纳入候选manifest。Git index逐文件SHA回读匹配；修正新测试文件末尾空行后diffcheck通过，commit ca114683b50159f1584349f0fcd569614b6464e5，已推送同一feat_codex/financial-report-agent-plan-writer-20260717。Backend本会话HEAD基准更新ca11468；ML b0525ae、Web4758ebc。所有旧dirty仍保留，未merge/deploy。

Backend draft PR https://github.com/NolanSoloBuilder/mindspace_backend/pull/37 已创建，head ca11468；等待PR Linux镜像验证，未合并。完整report07的session32274已再次确认为live，继续原scope及绝对deadline。

## Web 精确候选提交与两层 Linux 镜像通过

Web root按候选manifest逐项验证：21项已测内容仅组件README与工作区不相同，差异为明确排除的旧段落。通过git hash-object/update-index将候选内容精确放入index，工作区README原样保留；另加入只读权限PR Web gate，同181项测试/SEO/生产build入口，无部署。22文件index SHA均匹配，diffcheck通过，提交30e3df924db84b9b7d2307efd539ce1c9eb59088并推同绑定分支。Web当前绑定HEAD更新30e3df9，旧renderer/marketing/local/secret等dirty保留。

Backend PR37 Linux run34552973898已成功（1m40s），production image及断网contract image均通过，未部署。ML PR32此前已成功。

真实report07 SDK第16次请求429后由生产退避策略恢复，后续请求返回且累计登记22条证据。仅证明一次实际恢复；尚无完整候选，不宣称报告质量已通过。

Web draft PR https://github.com/NolanSoloBuilder/mindspace_web_frontend/pull/29 已创建，head30e3df9，等待PR Linux Web build。Backend Linux日志确认271passed/1deselected/15warnings；显式deselect仍为兄弟ML目录比较。三仓均未merge/deploy。

## Web PR 检出失败修复

Web run34553149609在checkout移除临时auth时失败，未进入npm：主干有唯一mode160000的.claude/worktrees/affectionate-wilbur-7abb7c，却无.gitmodules URL。Root仅git rm --cached该gitlink并在.gitignore加.claude/worktrees/，没有删除本地目录、文件或worktree。index确认无gitlink且仅两项变更，commit c600876cd3e6b48aca92e89fabffd4084d540bc9，Web会话HEAD基准更新。PR29继续获取新CI结果，未部署。

report07截至SDK24次只有一次429（第16次，随后恢复），逻辑23model/22tools、22证据/6计算，仍运行，尚无最终报告验收结论。

## 2026-09-11 Web Linux 完成及部署元数据权限修复

Root回读Web PR29 head c600876cd3e6b48aca92e89fabffd4084d540bc9，run34553257033终态success，02:07:21Z完成。日志/tmp/cited-alpha-web-pr29-linux-gate.log确认12文件181测试、SEO脚本检查与生产build通过，35预渲染路由、入口183.66KiB gzip/220KiB预算。先前gitlink checkout错误已消失。三仓PR Linux gate均通过；没有merge或生产部署，也未将CI作为完整报告验收。

当前ML workflow新增冻结Secret数字版本步骤，需secretmanager.versions.get。Root核对GitHub变量部署身份github-ml-deployer与项目/Secret IAM，发现没有该元数据授权；在单一cited-alpha-ml-prod-secrets-yaml Secret上增加roles/secretmanager.viewer并独立回读。角色定义不包含versions.access，原secretAccessor成员保留。未读写Secret内容或创建新版本，当前latest仍ENABLED数字2。

尝试以部署SA执行版本describe时，本机用户缺少iam.serviceAccounts.getAccessToken，失败发生在impersonation，不能据此判断新Secret权限失败。未追加TokenCreator或扩大权限。策略绑定已确认；GitHub WIF真实身份下版本冻结仍待部署workflow验证。

完整财报07 session32274再次回读仍live，同scope、原02:27:38Z deadline；观察到33逻辑model/32tool、26证据/8计算，尚无candidate。继续同一运行，不因观察间隔重启或延长预算。

## 完整财报07语法错误终止及有界纠错修复

Session32274已返回exit0，result.status=incomplete、accepted=false，35逻辑model/34tool、26证据/10计算；SDK generation共37次。最终provider finish=MALFORMED_FUNCTION_CALL，空assistant内容，没有candidate。此终态已确认，不能继续把07描述为live，也不能把10项计算当完整报告。

Root核对Google官方GenerateContentResponse说明，此finish表示无法解析的工具调用语法。ML Pi runner增加最多两次进程内纠错：仅明确此finish且空content，失败消息仍持久化，追加host feedback后由Pi继续；每次消耗原model预算并沿用原timer。按完整messages累计失败次数，不随普通续接重置。Vertex投影仅跳过这类空审计消息，保留签名、已完成call/result和原始checkpoint；有pending调用时仍拒绝。Safety、截断、非空错误、transport/unknown effect不进入纠错。终态checkpoint依旧要求host决策，未修改隔离canary的多attempt resume审计边界。

真实Pi Node16项通过（包含两次上限、小预算、取消、历史累计、证据不重放）；Vertex/model协议24项、Pi subprocess/execution14项通过，diffcheck通过。6文件精确提交9a848b53f51b27da44a7d6bc6235821c8e7147b7，同绑定分支，旧dirty保留。ML绑定HEAD更新为9a848b5；待PR Linux重新验证及真实报告。模块README同步记录限制，不把离线修复当报告通过。

官方语义依据：https://cloud.google.com/vertex-ai/generative-ai/docs/reference/rest/v1/GenerateContentResponse 。

## 纠错版本Linux通过并启动完整财报08

Root回读ML PR32 head9a848b5的Linux run34553784084成功，2m18s。实际生产Dockerfile构建、镜像内Pi16pass/0fail、Python断网合同173passed/1warning；日志/tmp/cited-alpha-ml-pr32-syntax-linux-gate.log。未merge/deploy。Backend PR37与Web PR29仍draft/open/mergeable，当前CloudRun各revision未变化。

Root独立使用Decimal复算完整07的10项growth_rate/difference，逐项核对输入与单一XBRL事实值和单位，均一致；结果/tmp/cited-alpha-tesla-2024-canary-07/independent-calculation-audit.json绑定progress SHA。此为算术及catalog输入一致性，不是DOM原文或完整报告验收。

Linux通过后启动完整08，session67695，输出/tmp/cited-alpha-tesla-2024-canary-08。同原问题逐字比较一致，独立新scope，64model/128tool/2review/1800秒、20秒间隔、生产4次provider退避、SDK上限264；绝对deadline2026-09-11T02:46:16.407575Z。运行文件与ML HEAD精确匹配。没有延长或重置已终止07；08待实际报告和纠错表现验收。

## 生产迁移前只读实测

Root复用已运行并核对命令的Cloud SQL Proxy PID38312/127.0.0.1:13307，目标cited-alpha-20260701:us-central1:cited-alpha-mysql。凭据仅从指定Secret读入进程内，不输出/落盘；直接PyMySQL READ ONLY transaction执行聚合与information_schema，rollback后关闭，无应用初始化或写入。数据库cited_alpha/MySQL8.0.45-google。

workspace_runs当前varchar(8)/v2默认值/v2-v3 CHECK，确实需要迁移。information_schema估计DATA_LENGTH322453504字节（约307.5MiB）、INDEX_LENGTH606208；统计TABLE_ROWS310仅估计，实际按status聚合总396。Steps DATA_LENGTH344473600。COPY/SHARED不能按几行小表假定瞬时完成。

21个running Run的lease均NULL，最后更新2026-07-08；1个running Step租约2026-07-15已过期。没有观察到未来有效lease；这是DB聚合快照，不证明无外部正在执行的请求，也不自动修复历史任务。Outbox172 pending，最后更新7月16日。Queue当前RUNNING，maxConcurrentDispatches2。现部署步骤pause Scheduler/Queue后sleep35只说明调度请求窗口；正式迁移前仍需重新核对实际writer/事务和停写条件。已有configure_workspace_migration_session设置lock_wait_timeout，未为此重复新增机制。

原始非敏感聚合保存/tmp/cited-alpha-production-migration-preflight.json与/tmp/cited-alpha-production-lease-preflight.json。未迁移、未取消任务、未暂停生产投递、未更新Secret。完整报告08 session67695本轮再次确认live，同原deadline。

本轮最后一次同句柄回读确认08已终止：session67695 exit0/result incomplete/accepted false；7model/6tool、0证据/0计算。第7至10次SDK请求连续429（02:18:34Z..02:18:44Z），生产4次退避用尽，modelDiagnostics=provider_quota。无candidate，语法纠错路径尚未真实触发。上段live为更早观测，当前以此终态为准。不得立即重复同配置付费流程或宣称新修复已真实验证；需先核查provider可用性/配额及受治理的模型运行策略。

## 429诊断及研究专用退避

08 provider-diagnostics.jsonl仅返回429/resource exhausted，没有quota名称或Retry-After。历史quota列表的substring匹配命中flash-lite-qcd/flash-cyber，不能算当前gemini-3.5-flash固定配额证据。Google官方https://docs.cloud.google.com/vertex-ai/generative-ai/docs/resources/throughput-quota 与https://cloud.google.com/vertex-ai/generative-ai/docs/error-code-429说明共享容量也可能返回429；本项目原因仍非确定结论。当前已经global endpoint，未切region/model、未购买吞吐。

研究writer/reviewer默认改用service层ResearchVertexClient，继承原有ADC/model-call治理与重试错误分类，仅将退避改10/20/40秒加0..2秒jitter，最多4attempt，环境指定更低值仍生效。普通VertexAIChatService不变；等待受原run/review deadline与取消限制，不增加逻辑模型调用或原请求数量。较短剩余时间可能在完成所有重试前终止。

9项新测试覆盖实际继承transport循环、请求身份保持、成功/4次耗尽、取消、真实短deadline、403不重试、上下限、writer/reviewer接入；另10项gateway/reviewer回归通过。精确6文件提交2a267133a1ec953e8d3dd99779654fd34dad2ac3，ML绑定HEAD更新，旧dirty保留。新测试进入PR断网manifest。/tmp canary已改用同ResearchVertexClient并记录实际退避参数，尚未发起新付费运行。真实可用性改善待验证，不能当作429已解决。

## 完整报告效率基线

Root从07/08原usage记录白名单聚合，保存/tmp/cited-alpha-research-token-baseline.json并绑定原文件SHA。07返回35次generation，累计input3273123/output7747/thought31536，单次maxInput157733；08返回6次，累计input88814，maxInput32526。失败请求可能没有usage，因此这不是完整计费结论。

07工具结果text合计339051字符；仅table_context跨结果重复约30591字符，不能假定单项去重即可解决整个上下文开销。下一次先保持原问题、证据工具及模型，只验证研究专用退避；后续上下文优化须保留原文、引用口径、签名及工具配对，以真实报告验收衡量，不能靠删除事实简化任务。当前ML2a26713 CI run34554333539正在构建，watch session19299。

ML2a26713 Linux run34554333539最终success，2m21s；镜像内Pi16pass/0fail、Python182passed/1warning，日志/tmp/cited-alpha-ml-pr32-backoff-linux-gate.log。随后完整09启动，session15455，输出/tmp/cited-alpha-tesla-2024-canary-09；逐字核对原问题不变。新scope固定64model/128tool/2review/1800秒、外层20秒间隔、研究10/20/40秒退避加jitter、4attempt/SDK总上限264。具体绝对deadline见pacing.json。不是08续接，无预算重置；真实效果及报告待验收。

## 跨来源真实验收材料准备

官方Tesla Q4/FY2024 PDF已下载原件11267189字节/36页，SHA05dfde334f800ec5f0ee140c0dd78409f24ad775e11a0c68f8a6b534b04cafdc；与实际canary07 10-K HTML原件2a5dc1...一并归档contexts/source_materials/cited_alpha_cross_source_tesla_2024。manifest与comparison-case保存来源、哈希、非答案式任务及独立验收条件。

Root渲染并回读PDF物理4/5页：季度与年度表不同，明确Unaudited；可验证期间错配、披露性质、数值/舍入和现金流计算。两份文件同issuer，只证明跨文档/格式，不宣称独立机构相互佐证。36页超过online15页门槛，需完整batch能力，不能截页冒充原始PDF。当前只完成本地原件和验收材料，未进行应用附件授权/DocAI或多来源模型报告，不更新04为完成。

## 完整长PDF batch验证启动

已创建并回读专用私有DocumentAI桶与服务级对象读写授权，详见11。/tmp/cited-alpha-docai-full36-canary.py通过已审ResearchDocumentBatchOperationClient单次提交36页原件，无裁页；session3042，输出/tmp/cited-alpha-docai-full36-01。提交intent与operation分开保存，provider产物最终单独保存；仍非应用Document/Workspace落库证明。完整报告09 session15455仍同一次运行，观察到14model/13tool，尚无证据登记或candidate。

36页PDF提交已成功返回projects/829189946367/locations/us/operations/71526297375386633；session3042随后因poll403终止。安全诊断明确是本地用户ADC缺少quota project，并非提交失败或新IAM缺口。Root使用同ADC的with_quota_project(cited-alpha-20260701)创建仅本进程查询会话，没有改全局ADC。新poll-only脚本/tmp/cited-alpha-docai-full36-poll.py不含提交入口，session48556继续同operation，保留收到operation时起1800秒原deadline，paidResubmissions=0；/tmp/.../poll-resume-audit.json记录依据。后续必须观察同handle/operation，不能重复提交。

同一batch operation最终完成，poll-only session48556 exit0，实际读取36页且page_number恰为1..36，paidResubmissions=0。providerResult SHA ca7ef4e4f9f546146c16e2fdb149949da8f943f2dbd1149ef734cf6bb6c9364c。operation/submit/poll/summary及按SHA保存的provider shards已归档source_materials/.../batch_acceptance。此为真实完整PDF batch与原页顺序证明；尚非应用Document落库、字段定位资格或跨源报告验收。当前长PDF降级页精度仍需后续资格验证，不冒称已支持精确字段高亮。

## 原文版本回读与单请求材料复用（2026-09-11）

session60438已终止且通过：真实GCS保存原PDF、provider JSON和规范化manifest，实际适配器回放得到36页、2198行，第5页年度收入引用可读，定位精度为page。版本dv-436bc437444429f8abc695a4f21c7ddbd3b0ad270de2972bbec862396d427c5f；结果/tmp/cited-alpha-docai-full36-01/version/summary.json。此版本使用手动测试scope，未证明应用附件授权、业务落库或UI。

ML服务层DocumentVersionService将完整校验材料作为请求内结果复用，避免几何计算再次下载PDF和约34MB provider JSON；公开方法与返回合同不变，无跨请求缓存。新增测试证明每次读取恰为三个对象、后续请求重新读取、错误workspace在I/O前拒绝、三类对象篡改均拒绝。15项版本测试及29项几何/路由/工具回归通过，git diff --check通过，模块README同步。精确三文件提交b557c2454449b18fd6d9f0f3ac5cf6eceaf3271a；原分支与其他dirty改动保持。

真实GCS只读复验session83674通过：三个对象各读一次，完整返回值与修改前一致，耗时23.08秒，无付费解析请求。结果/tmp/cited-alpha-docai-full36-01/version/single-read-verification.json。该延迟仍不足以证明交互体验合格，后续需以应用点击实测评估按字段读取的存储组织与缓存策略。

完整报告09结果已回读：status=incomplete、无report、0证据、0计算，modelDiagnostics为provider_quota；此前running表述已被此终态取代。研究退避未解决该次可用性问题，完整报告、多来源应用链路和生产验收仍未完成。

## CI回读及完整09原预算续接（2026-09-11）

b557c24已推送原ML需求分支，Linux run34555457628最终success：Pi16测试、Python185passed/1warning。日志/tmp/cited-alpha-ml-pr32-single-read-linux-gate.log。未合并或部署。

完整09轨迹显示读取了收入、现金流表和风险章节，终止前尚未引用登记；这不同于检索无结果。02:41UTC核对原绝对截止时间02:55:12.198623UTC仍未到，且终态最后四次SDK调用均明确429，无未知调用。为本地canary新增单次续接SDK预算审计：限制4attempt策略不变、连续ordinal、每次已终态、末组四次显式429、无嵌套续接、上限不增加；实际计数与六种拒绝情况测试通过。脚本/tmp/cited-alpha-research-canary/sdk_resume_budget.py，原材料哈希保存在sdk-resume-audit.json。现有prepare_resume继续验证scope、问题、asOf、原deadline、累计逻辑预算、review次数及pendingEffects全部完成。

同任务启动/tmp/cited-alpha-tesla-2024-canary-09-resume-01，session87401。回读确认原任务ID/问题/asOf不变，原64model/128tool上限不变，保留18model/17tool；剩余duration789秒，绝对deadline不变。原SDK上限264、已使用21；续接SDK上限取剩余逻辑预算保守界192，不重置264。02:43左右观察累计21model/19tool，尚待报告结果。仅本地canary续接，不作为生产持久化/UI恢复证明。

## 完整09续接终态及批量引用补读修复

session87401于本轮回读确认为exit0，result incomplete/无report，modelDiagnostics=provider_quota。续接7次SDK尝试中末4次连续429；累计22model/20tool、0证据。没有再次重启付费运行。真实轨迹显示cite_filing_fields在新进程中返回read_required：原表虽在历史上下文中，当前进程未验证，原规则正确拒绝引用。

同时发现批量补读只返回第一个缺失行，容易导致逐行重试。ML service层改为在保留read_arguments兼容字段时返回read_requests：覆盖所有未读目标行，同表按最多20行分组；提示遵循真实返回与截断分页。提示不下载原文、不恢复seen、不登记证据，仍需实际read后通过原校验，原批量原子性和证据ID不变。nearest README同步，26项SEC批量/真实Pi恢复/工具测试通过，diff --check通过。

基于实际失败批次的离线导航审计：9字段/4不同目标行只需一个offset7/limit4读取请求即可覆盖，审计/tmp/cited-alpha-tesla-2024-canary-09-resume-01/batch-repair-plan-audit.json。此为导航计划验证，不是模型执行或完整报告验收；未以此更新04完成状态。

## 受治理的替代模型验证与完整报告10

当前YAML的agent_deep_research和workspace_report_semantic_verifier默认仍为gemini-3.5-flash。按docs/rules/model-policy.md允许的环境变量调试覆盖，本轮仅在隔离进程选择gemini-3.8-flash，不改生产Secret/YAML，不切换已有任务中的模型。官方2026-09-09更新的生命周期及模型页确认3.8于2026-09-02发布、支持global/函数调用/结构输出，属于较短可用期模型，不能据此免除未来生命周期维护：
https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/model-versions
https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-8-flash

两次SDK请求的真实协议探针通过：实际ResearchModelGateway与ResearchVertexClient、原ADC和项目、模型策略覆盖，先调用lookup_field，再带原始assistant函数签名和toolResult续答。限2次SDK尝试/无重试/每次2048输出token上限，4.94秒完成；结果/tmp/cited-alpha-model-availability-38.json。synthetic工具仅验证接入与签名回放，不证明金融报告质量或持续容量。

随后完整10启动，session23349，输出/tmp/cited-alpha-tesla-2024-canary-10。原完整问题不变，writer/reviewer均由本地模型策略选择3.8，64model/128tool/2review/1800秒，外层20秒、最多4attempt退避，SDK总上限264；绝对deadline2026-09-11T03:18:18.763399Z。是显式不同模型的新验收运行，不是09续接，不沿用旧模型签名，不覆盖旧失败证据。尚待实际完整报告与原文/计算验收，04范围不变。

4d778fb23f7c98890db49fde5072b649beb5dc9e的Linux run34555920281已回读success：实际Pi16项测试、Python187passed/1warning。日志/tmp/cited-alpha-ml-pr32-batch-repair-linux-gate.log。三仓尚未合并或部署。
完整10 session23349本轮同句柄确认仍live，累计7model/6tool，正在read_filing；未启动第二个并发付费报告。后续整体验收仍需把实际生成接入真实业务Run/checkpoint/报告版本与Chrome，不拿已有分段MySQL fixture证明完整模型产物交付。

## PDF嵌套字段定位摘要展示（2026-09-11）

发现Web引用摘要仅识别旧扁平cell/line/pdf，对真实新document_field.record中的page_number未展示。展示层现按已识别field_kind(line/cell/span)读取嵌套record的明确页码/行号/表头；不展示原始ID，不以bbox推断高亮精度。API与鉴权合同不变。

30项ResearchReportArtifactView测试通过。Root在Chrome1044432735实际点击来源并截图确认第5页可见；预览使用明确标注的合成报告与HTTP响应，只证明真实组件渲染新定位格式，不冒充实际上传/API/金融报告验收。临时两个preview文件和Vite session88513已清理，标签已关闭。tsc仍有ChatPanel等既有基线错误，当前修改文件无诊断；完整日志/tmp/cited-alpha-web-pdf-locator-tsc.log。

精确三文件提交3677aed；README使用HEAD加本轮追加内容的单独暂存，既有README脏改动及其他68项历史状态保留。完整10同session23349仍在运行，已观察到首批16条真实字段登记，尚无正式报告。

## 总方案主线校准与报告10计算独立复核

2026-09-11再次核对三仓原工作目录、worktree和绑定分支：Backend ca114683、ML 4d778fb、Web 3677aed，历史dirty保持。Web Linux run34556618384回读最终success，包含报告相关验证、SEO检查、生产构建与35路由检查；日志/tmp/cited-alpha-web-pdf-locator-linux-gate.log。未合并或部署。

12补充模块职责图和设计文档权威映射，03标注早期两模板范围由04/06取代，避免设计文档彼此矛盾。没有据此新增服务或改变MVP范围。

完整10沿同session23349继续，观察到39model/38tool、36条证据及6项计算。独立脚本/tmp/cited-alpha-independent-calculation-audit.py从实际progress读取计算，用Decimal重算并核对每个输入与登记XBRL字段的值、单位和身份，6项通过；结果位于该run目录independent-calculation-audit.json并带输入progress哈希。该检查未重新下载原件，不代替完整期间可比性、正文口径和报告质量审查；运行后续新增计算还需最终重跑。

## 完整10终态与真实业务集成下一步

同session23349已终止exit0，result.status=incomplete、accepted=false，无candidate/accepted报告。最终40次模型、39次工具、36条证据和7项计算；独立复算7项通过。最后assistant的vertexFinishReason=MAX_TOKENS、stopReason=length、content为空，SDK最后请求状态response，modelDiagnostics为空，不能归因为已观察429。当前canary写作max_output_tokens=8192；适配器按原安全规则丢弃MAX_TOKENS中的toolCall，不执行截断工具参数。下一步需评估报告生成的输出预算及明确的截断诊断，不能仅扩大运行时长或把中间证据当完成报告。没有启动第二次付费报告，也没有用quota续接脚本绕过此终态。

子任务只读审查由Root回读，已沉淀13。SEC-only实际业务Run可以复用现有依赖注入点，用两个独立本地进程接通真实admission/outbox/Executor/CallbackService/DAO/GCS/模型/reviewer/delivery；临时transport只投送字节并严格校验本地token，生产HTTPS/OIDC客户端保持原样。PDF跨源需真实附件授权及正确owner原文版本，旧手工scope不可嫁接。尚未实现或运行该完整集成。当前设计与局部测试不足以标记04任何完整交付项完成。

## 写作输出预算与显式截断续接（2026-09-11）

ML service/research_agent/model_gateway.py 默认writer输出上限由8192提高到16384，主机显式覆盖仍限32768；MAX_TOKENS记录安全provider_output_limit诊断和配置上限。adapter仍丢弃截断toolCall、保留length终态，无自动重试；模型策略、reviewer上限、Run时间/调用预算不变。26项gateway/Vertex消息/真实Pi→SDK wire测试通过，实际wire验证16384；Web/mobile不消费此private诊断，HTTP终态合同不变。4文件精确提交521effe44ae6b19355c8642ae096255b177aacad推送原分支；Linux34557161874已启动，待终态。旧dirty保持。

原10的截止时间仍为03:18:18.763399UTC。Root新增独立opt-in --resume-output-limit，仅允许首跳、MAX_TOKENS且空可执行content、result incomplete、全部effect已完成、SDK尝试连续且全终态、最后response、未交付候选且剩余预算有效。复用原scope/question/asOf/调用计数/deadline，只将writer单次上限提高为16384；续接单请求最多1attempt，剩余SDK上限26，原40attempt累计不超过264。七项实际输入/拒绝回归及两项deadline/pacing检查通过。不是用quota规则伪装长度终态，也不是生产恢复能力。

实际启动/tmp/cited-alpha-tesla-2024-canary-10-output-resume-01，session32821，audit记录原文件哈希、移除终态、SDK哈希及预算。回读累计42model/40tool、36证据/7计算，仍待报告。原失败数据保留。后续观察必须同session，不因等待超时重启。

真实业务Run临时composition已由子任务实现并由Root读回：/tmp/cited-alpha-business-run-canary，两轮9项零模型preflight通过。真实两进程及MySQL查询、strict本地token、真实ML CallbackClient到Backend route/DAO的拒绝路径，错误token403、缺失Run409、paidguard503；无模型/GCS/业务写入，子进程清理。此处明确未验证生产OIDC/TLS、真实admission或报告交付。后续显式paid launcher仍在准备，当前没有第二个并发付费运行。

521effe的Linux run34557161874最终success，Root回读实际容器Pi16项、Python188passed/1warning，日志/tmp/cited-alpha-ml-output-budget-linux-gate.log。没有合并/部署；完整报告续接session32821仍在同一次实际模型请求中等待，未因观察超时重启。

## 完整报告候选、审稿去重与实际业务Run启动

10-output-resume-01 session32821终止exit1。累计43model/41tool、36证据/7计算；完成完整candidate（5章节、58个摘要/段落/单元格锚点），但check-draft遇到ReviewTechnicalError。Root离线复现根因：展开式review payload472287字符，大于180000上限，reviewCalls=1但实际review模型调用0。没有再续接该unknown check intent，也没有假造成功回执。

ML review_bindings增加无损pack：每条证据/计算按ID共享一次，各anchor保留原本独有的evidence/calculation/input边；还原后与旧展开图逐项完全一致，无原文/口径/顺序丢失，无跨anchor借用。实际输入151723字符，缩小67.87%；原180000限制不变。reviewer版本research-review/v3-compact-anchor-bindings，30项相关测试通过。保留真实未接受candidate作为负向尺寸/关系回归，并加入显式Linux离线manifest。9文件精确提交58dc18e882b7f68a2969ce629ad60a005377258f已推原分支，Linux34557686106待终态。报告/receipt HTTP与Web/mobile合同不变。

同一不可变candidate单独实际独立审稿session68659通过调用并返回rejected（不是报告通过）：10项factual问题，answer3/reasoning2/organization4/readability4/evidence1。输入77128token、输出838、thought5158；一次review，无原文重取/正式保存。主要拒绝项为局部派生计算/摘要来源/因果细节支持缺失。Root另记录税收调整和营业利润混同、现金流到周转推断及未来流动性保证缺证。candidate和verdict归档actual_report_acceptance/full_10，不用作writer答案。

真实业务Run临时harness再通过12项零模型检查，Root阅读真实consumer/DAO签名与SDK审计后显式启动/tmp/cited-alpha-business-run-01，session19411。user business-cc599d2b1903，workspace workspace-1342c9bc-012e-48c5-9a3c-3cc5dd21a0f2，run workspace-run-0d259a7d29b04740839317e1f21fdb40。正常JWT HTTP admission、实际queued outbox、WorkspaceRunTaskConsumer、ResearchRunExecutor与真实MySQL/GCS callbacks；原deadline2026-09-11 03:45:12UTC，64model/128tool/1800秒，66SDK上限、review2、single attempt、20秒spacing、writer16384，writer/reviewer由进程策略选择3.8。生产数据库/配置未修改，本地服务token不证明生产OIDC。

回读真实Run running，checkpoint sequence4/2376bytes，GCS不可变对象指针已持久化，artifact初始V1仍无报告schema。只启动这一条付费业务链路；后续同session继续，禁止因观察超时重复接纳。完整业务报告和浏览器验收仍待完成。

58dc18e的Linux34557686106已回读success：实际Pi16、Python192passed/1warning，日志/tmp/cited-alpha-ml-review-packing-linux-gate.log；PR32说明同步最终实现与真实拒绝边界，未合并。Root另用独立进程从真实MySQL加载Run的checkpoint指针，再由真实ResearchCheckpointStore读取GCS并核对scope/元数据/规范JSON/hash：sequence17、53647bytes、4model/3tool通过，无写入/模型调用。文件/tmp/cited-alpha-business-run-01/independent-checkpoint-readback.json。当前报告仍未生成，不能据此标记D1完整UI恢复通过。

## 真实工作区运行态与checkpoint请求内去重

2026-09-11，Chrome1044432755实际打开隔离业务workspace-1342c9bc-012e-48c5-9a3c-3cc5dd21a0f2。Web18900指向正常JWT API18873，实际User/profile/Workspace/Run/MySQL读取，无报告fixture。测试用户通过正常profile/update设置CitedAlphaReview；临时一次性loopback登录页仅把该真实2小时JWT写入浏览器mindspace.web.auth，没有写入仓库/URL。临时API仅允许读回和该profile setup，研究仍由独立bounded launcher运行。此组成不证明正常生产登录/OIDC/Cloud Tasks链。

实际页面Working后43→58秒是Backend lease剩余秒数，源于heartbeat续租，不是elapsed。Web8962bbc去掉active/waiting租约数字，只保留failed且可Continue的冷却时间；11项banner/observation/stream恢复测试通过，Chrome刷新确认仍同工作区且数字消失。空聊天是本harness后台POST/runs未创建user message；空V1被页面有意隐藏为No version，不能用假聊天/报告掩盖。下一条用户入口验收仍需conversation/stream。15记录根因及边界。

Backend f7e10b1将save_progress已验真previous.documentCaptures显式传给_persist，正常更新由4GET+1POST降为2GET+1POST；仍逐请求验证旧对象并由最终DAO sequence/lease CAS保护，不跨请求缓存。60项checkpoint/DAO/callback/executor/document测试通过，其中实证对象请求数及读后竞争写拒绝；三文件精确提交并推送，35项旧dirty保留，Linux34558561888待终态。此次运行中的旧Backend进程未重启，因此该Run不宣称已受益于新实现。

独立快照52通过实际GCS校验，515252bytes，11model10tool，尚未登记证据/计算。14记录成本拆分：重复details占28.4%持久包但不进Vertex，SDK前11次响应合计43.52秒；其余串行时间没有阶段日志，不能全部归因GCS。实际Run仍running、无完整报告。未改变04验收项或宣称MVP完成。

## 消息重复字段去重与实际MySQL中断

ML4d7bbdeb413115696d4903ae77b6aa95e519dd71仅在持久化副本省略与首text严格JSON等价的details；非等价/非有限/重复键/数值类型差异保留。实时Pi、provider content/signature、完整pendingEffects、catalog和原文不变。42项projection/execution/Vertex/SEC恢复测试通过；实际Pi在工具完成前后消息落盘两中断点不重复工具，provider DTO等价。真实52样本progress514943→368594bytes，减少146349bytes约28.4%，不声明模型input相同幅度下降。五文件精确提交并推送，Linux34558910627成功（Pi16/Python201），日志/tmp/cited-alpha-ml-checkpoint-projection-linux-gate.log。Backend f7e10b1 Linux34558561888成功273passed/1deselected；Web8962bbc Linux34558653797失败1项页面旧倒计时断言（188pass），属相关测试未同步，不归为baseline，修复中。

实际业务Run session19411已terminal exit1：本地MySQL13306突然拒绝连接，观察/status返回500使旧launcher进入finally清理两worker。最后SDK16全response；无report；mysql旧日志没有正常shutdown条目，尚未确定退出原因，不能归因模型或GCS。Root用原my.cnf/原datadir启动daemon mysqld PID31864，崩溃恢复完成且13306重新监听；未重建/删库。独立实际DAO/GCS读取checkpoint77通过739407bytes，run仍running，16model15tool，所有15effects completed、31messages最后toolResult，无checkedCandidate。原deadline03:45:12UTC不变，尚未启动恢复模型。

已提出严格同Run续接：先通过真实控制服务仅恢复该过期lease，再使用真实Executor；SDK旧16次审计累计保留，总上限66及review2不变，不能重置预算/截止时间或重发未知工具。临时launcher还需纠正一次观察500就杀worker的问题，观察失败不应等于业务结果。16记录持久安全进度设计，17记录真实PDF上传/附件授权及当前重复parse缺口，均不作为已验收功能。

## 原Run租约恢复与可见研究进度

Root审阅临时resume launcher后显式启动session69243，输出/tmp/cited-alpha-business-run-resume-01。真实控制服务只对唯一目标Run执行expired lease恢复（checked1/recovered1/failed0），再真实host.execute_run；复用checkpoint77，原scope/question/asOf/deadline03:45:12和累计16SDK均未重置。SDK新审计首存原16条，ordinal/model/kind/status严核，总66/review2及每次单尝试保持；等待前后及实际SDK前均核原deadline。观察500不再直接当业务终态，不重新发起recover。没有新的Workspace/Run，没有移植报告。

Backend1e25ded9ffe624a113b32739a42297b9debc6508新增安全researchProgress：与checkpoint指针同事务CAS，有限活动+登记ID数，不输出模型内容/参数。部署离线门禁285pass/1明确deselect；Webfc1dfb0e7c0b2163a0028fa14c6fbab58e9e527d展示可恢复最近活动，83项完整相关测试通过，陈旧lease断言已同步。两仓原dirty分别35/68项保留，README只精确暂存本次追加。新Linux分别34559451122、34559450184待终态。

Root仅重启独立UI API18873（新session74699），Vite18402及真实JWT保留，Chrome1044432755刷新后实际显示Analyzing/Reading及0登记数。正常JWT Run GET回读researchProgress cursor87/updatedAt2026-09-11T03:42:29.749811Z；字段不经HTTP fixture。独立checkpoint与页面同Run恢复已观察，完整报告、正式生产回调及发布仍未验收。运行末段继续读取材料，不能将已读结果计为已登记证据，尚无reportVersion。


## 2026-09-11：精读登记集成与离线完整门禁

本批沿用 ML 原工作目录及已确认 `feat_codex/financial-report-agent-plan-writer-20260717` 分支，基线 HEAD `4d7bbdeb413115696d4903ae77b6aa95e519dd71`；保留存量未提交改动。本批尚未提交、发布或触发新付费研究。

- service 层的 `read_filing` 增加显式可选字段登记，复用既有精确 cite 和证据身份；单批16条、新增128000 bytes，拒绝时不写入 catalog、不返回悬空 ID。
- `execution_service.py` 接入全部 provider 的当前 catalog 总计数，避免 SEC/PDF 分别计算容量；不修改公开客户端 API、模型场景或报告格式。
- 工具消息 checkpoint 仅在完成回执已持久化且内容可严格恢复时合并一次重复写入；未知字段、非重复 details、assistant 消息和工具意图仍持久化。精确 Pi 消息发出时间不在恢复保证范围内，详见模块 README。
- 真实归档测试独立为 `tests/test_research_sec_registration_archive.py`，避免 portable CI 依赖本机档案或跳过案例。portable manifest 增加登记与 checkpoint 边界测试。

实测：`runtime/research-tests/run_offline.py` 本地完整门禁 **229 passed, 1 warning, 0 skipped**；真实归档 Tesla 10-K 的解析/登记/显式 cite ID 等价测试 **1 passed**。`git diff --check` 通过。前者使用实际 Pi 子进程与替身模型/存储并阻止 Python 外部 socket；后者使用保留的真实 HTML 和离线字节存储。均不代表生产报告验收。

下一步：完成本批 diff 与兼容边界审查、提交及 Linux CI，再通过新建的有界真实业务 Run 验证报告。旧失败 Run 不重置期限和预算。完整报告、跨来源续研、原文点击与生产验收继续按04范围推进。


### 本批提交与真实页面回读

ML提交 `ae0f9e59e08d9c211541c73846710d7b760f8681` 已推送既定分支，11个任务文件，未夹带旧writer/Need改动。额外修正精读登记后的行动提示，明确已有ID无需再次cite；17项登记与模型wire测试通过。Linux CI `34560132028` 当前正在构建，结果待回读。

通过Chrome重新打开真实工作区 `workspace-1342c9bc-012e-48c5-9a3c-3cc5dd21a0f2`：显示 Failed、research execution did not acknowledge completion、No version，导出/保存/分享禁用，Continue按钮可见但未点击。本次只验证失败态正确呈现，不证明Continue恢复成功，也不证明报告正文或引用体验。


### Linux门禁与下一轮业务验收准备

ML `ae0f9e5` 的CI `34560132028` 已成功：候选镜像内Pi16项、Python229项通过。日志保留于 `/tmp/cited-alpha-ml-read-registration-linux-gate.log`。新的临时验证入口通过真实 `/conversation/stream` 持久化用户问题并接纳Run，仍使用原Outbox consumer执行，不自行写聊天或Run状态。观察脚本遇到查询错误继续观察；入场结果未知、进程退出或观察期限到达时保留进程句柄/锁并要求核查同Run，不能直接重新发起研究。3项观察演练、2项SSE transport演练及12项真实双进程零模型preflight通过；这些尚不证明真实SSE业务成功。

真实conversation Run 02已接纳：`workspace-run-bc018da33a804729b0a8b46fa21e3ecf`，工作区 `workspace-e7622833-84f7-47b5-bedc-4774006228ab`。原问题不变，截止UTC 2026-09-11 04:27:11。观察进程session46338；档案 `/tmp/cited-alpha-business-run-02`。首次readback running，consumerDone=false，无consumerError；启动成功不等于产物验收。后续优先查询此session和同Run，禁止重发start。JWT在私有文件，勿输出。


### Run02 对话、刷新及验收基准

独立进程实际读取MySQL指针和GCS checkpoint，sequence9（2 model/2 tool）与23（6 model/5 tool）均通过scope/hash校验。23时尚无登记证据和计算，不等于已完成报告。Chrome tab1044432782展示真实用户问题、Working与持久进度；刷新同URL后问题及进度仍在。使用真实测试JWT的一次性本地bootstrap，不更改服务授权；UI API仍为独立只读宿主18873，因此不把页面Cancel入口视为已验证取消。Vite已从旧session18402切换至新session22728，真实付费session46338未中断。

从归档10-K独立读取2023/2024合并XBRL收入、不同利润口径、经营现金流及资本开支，保存 `/tmp/cited-alpha-business-run-02/independent-fact-baseline.json`。作为人工验收候选基准，须结合原表标签判定口径；不注入研究模型，不将不同利润concept混称为净利润。子任务开始独立PDF正常上传/附件零模型接入准备，隔离于当前运行资源。


### 工具契约与PDF真实入口进展

Run02独立checkpoint44：11次模型调用、10次工具、0登记/0计算，仍running；已发现limit35超过执行上限20的一次请求。SEC参数schema修正未提交，13项focused/wire测试通过，当前运行器不热更新。报告schema约束另行补齐，避免写完整稿后才发现格式上限。

PDF独立环境 `/tmp/cited-alpha-pdf-isolated-MJJV9O` 已完成真实JWT上传、文件回读、Workspace附件授权及越权拒绝；MySQL13316/PG15436/ML18882隔离运行。Root已读result.json与independent-readback.json，确认11267189 bytes/SHA与归档一致，doc仍queued且sha字段null、heldJobs1，未调用模型或DocAI。原字节存储使用明确本地adapter，不能称生产对象存储验收。下一步CallbackService注入真实document client，以及在正常原件上传阶段保存SHA，后者先设计，不以手动补写掩盖产品缺口。


### 工具规格及Callback依赖注入提交

ML提交 `2433fda25ffe1c190e257ae22894aef80e8cb8db`：SEC读取参数边界与报告文本/数组规格对齐，保留确定性及语义校验。修正实际Pi测试的非法空sections fixture，采用最小合法无事实断言正文。完整离线236 passed/1 warning；Linux CI `34560877261`正在执行。Run02使用已加载ae0f9e5，不受后续文件修改影响。

Backend提交 `be1fdc1`：仅callback document client注入、对应7项测试、README与明确CI清单。完整离线292 passed/1 deselected/14 warnings（既有弃用告警）；当前正在推送。真实Run与文档授权、原件reader、版本检查未替换。SHA正常上传跨仓实现另行进行，未夹带进此提交。


### 原文上传完整性与Run02证据登记（2026-09-11 UTC04:12）

ML `ff6e4c5ee7d03b25b2fa2f71c6cf283e811511e2`、Backend `8ae870a3803dd01d986477cb24121db48f3761ea` 已推送绑定分支。Backend按实际上传原件计算SHA，ML内部DTO校验格式，scheduler保留摘要，worker在转换或解析前核对原始字节。旧缺摘要文件仍兼容，不把转换后的PDF摘要混作原件摘要。两提交没有纳入既有Need/writer改动。完整本地门禁分别247 passed/1 warning与296 passed/1 deselected；Linux CI 34561273965、34561274281仍进行中。父提交2433fda与be1fdc1的Linux CI已成功。

独立PDF正常上传预检 `/tmp/cited-alpha-pdf-isolated-MJJV9O/sha-v2` 已验证实际11267189字节经上传链路把SHA保存至queued文档，无operator补写；另一进程SourceFileService回读一致，错误归属与内部token被拒绝。原件使用明确本地存储adapter，调度仍held，未调用DocAI或模型；这不证明生产解析完成。

Run02仍使用旧加载版本ML ae0f9e5/Backend1e25ded。独立MySQL指针和GCS原字节回读checkpoint101通过scope/hash：819366 bytes，25次模型调用、25次工具调用、16条已登记证据、0计算、无checkedCandidate，状态running。登记来自实际cite_filing_fields；不能把此前0登记视为工具不可用，也不能把已登记视为事实审查或正式报告交付。原截止UTC04:27:11保持不变，不重发Run。


### 追加回读

Backend8ae870a Linux CI34561274281成功，296 passed/1 deselected/15 warnings，日志 `/tmp/cited-alpha-backend-upload-sha-linux-gate.log`。PR32/37描述已更新最新提交与实际限制，未合并或发布。Run02 checkpoint114独立回读通过：28 model/28 tool、34证据、0计算、无候选。Chrome同工作区真实页面读到33条登记时点，仍Working/No version。证据101的独立审查文件 `/tmp/run02-evidence-101-audit.md` 确认16条字段内部一致，其中总收入2条与独立基线一致，其他14条未宣称独立验真。


MLff6e4c5 Linux CI34561273965已成功，实际Pi16项、Python247项通过；日志 `/tmp/cited-alpha-ml-upload-sha-linux-gate.log`。跨来源composition另完成云端只读预检：目标processor ENABLED，ADC项目正确，两目标bucket返回objects.get/create权限；未触发解析。剩余验收仍包括真实报告、计算、跨来源版本及生产发布。


### GCS分页与解析复用细化

解析一次、研究按权限绑定的设计已保存19，包含普通上传重试、完整provider分片、版本和unknown提交边界。先完成GCS输出分页修复ML f01419a：原先只读取首列表页，现遍历nextPageToken、空页继续、重复cursor拒绝，完整枚举后才下载。仅provider service/README/7项专用测试/显式CI清单；完整离线254 passed、1 warning。新测试名test_research_document_gcs_pagination.py，未夹带旧改动。正在推送，Linux结果待回读。

Run02 checkpoint131仍running，33 model/32 tool、38证据、0计算/无候选。独立验收侧计算基线已生成10项（不同利润口径分开，FCF定义须说明），未注入模型。实际模型输入第33次164898 tokens；只读统计发现两批引用可去除重复table_context约45KB，但精读历史仍占多数。开始仅模型请求副本的批内可逆共享表示实现，完整rawCatalog/永久引用/保存消息保持不变，当前Run不热更新。


### 批量引用模型视图压缩及真实计算

ML e4d52ae993920b45d725a6ca39b4705cfabb0997已推送：模型gateway前纯函数投影，只处理已知成功cite_filing_fields回执。批内共享完整filing/table_context/headers/footnotes，字段坐标/XBRL/quote保持各自身份；未知或未缩小的结构原样通过。Pi/签名/checkpoint/rawCatalog保持原结构。固定131消息模型副本491441→443995字节，减少47446字节，不能当作实测token或报告质量提升。完整本地264 passed、2 warnings（日志 `/tmp/cited-alpha-model-context-local-gate.log`）；对应Linux CI待回读。

Run02 sequence157独立scope/hash回读：39 model/39 tool、40证据、3计算、无候选。已独立复算收入差额917000000美元、同比0.95%、汽车收入同比-6.49%，均与保存输入/精度一致。该检查不等于报告论证通过。证据 `/tmp/cited-alpha-business-run-02/independent-calculation-readback-157.json`。当前真实运行仍旧版本，无热更新或重发。


### 最新镜像门禁及运行等待

ML e4d52ae的Linux CI34561871259已成功，Pi16/Python264 passed、2 warnings；日志 `/tmp/cited-alpha-model-context-linux-gate.log`。先前f01419a单独CI被新提交并发取消，不能称其独立CI通过；后续e4d52ae包含该改动并通过。Run02 sequence176仍running：44 model/43 tool、40证据、8计算、无候选。已核对实际工具回执含remainingSeconds（285→240→194）及提交报告预留提示，不能将迟迟未写报告归因于完全缺少时间反馈。原截止UTC04:27:11不变。


### Run02终态与未验收草稿（UTC04:27之后）

观察session46338已实际退出（exit1），readback failed/consumerDone=true/reportVersionId=null，未重发。终态active_step_id为空，改由原workspace_agent_execution Step回读checkpoint182并通过GCS scope/hash校验：46 model/44 tool、40证据、9计算、1174544bytes，无checkedCandidate。

模型曾产出5节49引用的完整submit_report参数，但schemaVersion写为financial_results_v1，而Pi工具const要求research-report/v1，因此工具未执行、无事实/编辑审查。第45次SDK约75秒生成该参数；第46次开始修订，但未在原截止前正式交付。草稿原样保留 `/tmp/cited-alpha-business-run-02/unaccepted-model-draft.json`，不将其当正式报告。需要把不应由模型决定的固定协议身份移至宿主，并单独审查实际正文，不能仅改字符串后直接宣称合格。


## 2026-09-11 跨来源接入与原解析恢复

报告v2内容编译两仓CI已通过；后续原文client DI提交3f14ce4的CI34563442478也通过。附件条目ID与原文件ID混淆经真实跨仓输入发现并修复，最新ML8200d05/Backend10b767c已推送，本地296/303项通过，另1项跨仓检查通过。原有dirty写作改动保留。

跨来源business02真实Run在DocAI提交后因ADC quota project回读403失败，模型调用0。原operation已按本进程quota project确认SUCCEEDED，4个generation-pinned原始shards归档，无重复解析。business03已用显式恢复原provider数据方式正常接纳，仍在运行验证中，未形成验收结论。完整证据、Run ID和原截止时间见22。

### 跨来源当前检查（2026-09-11 UTC 04:55）

8200d05/10b767c两仓当前CI均成功。business-03独立checkpoint23验证PDF捕获完成，模型5次/工具5次，仍无正式候选；Chrome刷新能回到同一活动任务，页面仍无报告版本。完整产物、跨来源引用、计算和生产验收继续未完成。详情见22；原生PDF文本定位审查已归档到10的附件，仅候选可行性，不升级定位精度。

### 留存解析页字段视图（2026-09-11 UTC05:18）

三仓实现与独立复验见23；Web e5c25e7、Backend9c26ef5、ML247d52d已提交推送。原PDF页精度不变；解析页支持独立字段高亮。真实8字段、10项拒绝验证通过，当前跨来源Run的执行版本仍为ML8200d05/Backend10b767c，未热更新。最新独立checkpoint130仍running，32证据、0计算、无候选。尚未满足完整报告验收。

### 当前终态与后续改进（UTC05:24）

跨来源business03已deadline失败，独立checkpoint146保留33证据/3计算，无报告，见22。付费worker退出后启动纯只读ML18884，真实GCS字段图返回200、SHA匹配；27.34秒冷读不满足交互体验，见25。Web9ff4c38修复延迟刷新越过卸载/导航生命周期，两例旧代码确定性失败，新页/观察75项通过；ML18afdcf纯模型副本PDF上下文投影14真实结果往返一致，完整343项通过。两提交已推送、CI待回读。Backend9c26ef5与ML247d52d的解析页CI已成功，正式报告双视图和生产验收仍未完成。

### 2026-09-11 UTC05:30 门禁及失败页面

Web9ff4c38的CI34565730512及ML18afdcf的CI34565728032均成功。Web9bc0b23新增截止失败精确本地化，76项页/观察测试通过，Chrome实际failed任务展示time limit及No version，未点击Continue或伪造报告。新标签2797仅因上一验收页已不在Chrome清单而重新打开同工作区，后端任务未重启。材料复用正在实现，完整报告仍未验收。


### 2026-09-11 三仓门禁与下一次真实运行准备

本轮实时核对三仓仍在已绑定分支；Backend5178d5e、ML66ad4b2、Web9bc0b23的CI分别为34566455725、34566454814、34566118644，全部completed/success。当前原工作目录的无关未提交改动保留。Backend减少纯checkpoint重复读取、ML材料缓存与通用批量调用提示已进入上述提交。

已归档实际缓存测量到cross_source_run03_acceptance/actual-cache-performance.json：首次读取24.254秒，随后图像0.809秒、另一字段0.717秒，仍不证明首次查看或整份报告已达标。下一次业务运行前的零模型预检已再次确认真实owner JWT及附件权限、原文SHA/字节数，未创建Run、未调用provider。上次business03终态failed/consumerDone=true且两个worker已不存在；本轮准备使用相同完整问题与预算验证，不缩小验收范围。


### 跨来源business04实际接纳

相同完整问题已通过正常SSE接纳为workspace-run-5850b168228643b9a36128b0e56ccde2；截止UTC2026-09-11 06:10:55。Backend5178d5e、ML66ad4b2已由新进程加载，实际worker5140/5142，launcher session15870。保持64模型/128工具/1800秒预算，复用既有解析分片，不新提交DocAI。Chrome标签1044432801已读到Working及No version；这是活动任务恢复证据，报告仍未产生。

计时审查发现可选日志I/O错误会覆盖业务结果，已在临时composition中修正并通过成功、异常、取消身份及I/O/序列化失败测试；权威SDK预算审计不变。接纳、绑定和审查存于cross_source_run04_acceptance。运行继续观察同一session及Run，观察超时不重发。


### 运行中报告体验已提交

Web dc45c66已提交推送：真实活动保持可见，登记统计移入默认关闭的原生details，active提示采用中性样式；严格空报告区按当前研究Run解释状态，真实research产物标题改为Research report。Root审查后补空HTML、普通聊天成功及多Run状态冲突边界。四文件104项测试通过，diffcheck通过。Chrome实际Run04页面确认Research report / No report delivered yet、运行中说明与收起详情；点击详情后显示真实登记计数，取消入口保持，未发新任务。CI待回读。

同轮生产只读审查已落27/29：现有长请求容量与路由调用身份存在生产阻断。目标复用原三仓业务，仅新增一个ML control部署隔离review/文档读取，Backend API承载callback；仍待实现和真实SA/容量验收，不称已上线。

Web dc45c66的Linux CI34567598305已completed/success，报告/来源/版本/恢复检查、SEO合同与生产资产构建均通过。Cloud SQL本轮只读核实cited-alpha-mysql为RUNNABLE、activationPolicy=ALWAYS；这只说明数据库状态，完整线上研究验收仍未完成。

Run04 checkpoint104独立校验：19模型/32工具，0登记证据/计算，PDF capture完成，仍running。实际成功工具调用显示固定20字段分页耗时，已细化30及离线原型；完整line/text/ID/bbox的p4/p5约36.7KB，32KiB不足，48KiB可一页完整。Root实际查看p5留存图上的原字段框。原型未改变Run04或应用；模型理解和引用注册的集成仍待完成。


## Run04终态与页面读取v3衔接

终态失败，无正式报告，最后独立验证sequence190、42 evidence、4 calculations、checkedCandidate=false。完整证据见32终态记录。Backend已接纳v3并让新capture占位使用v3；v1/v2保存恢复保留原版，禁止运行中升级。checkpoint service及callback I/O离线测试25 passed。页面工具与持久HTTP transport仍在实施，尚无新真实报告或生产发布。


Backend ecc37d045d200d04bf77e45c39141a0f8c3d9c91已提交并推送授权分支，Linux CI34569357453通过。默认两独占checkpoint连接已接通，339项portable与35项focused通过，独立审查无阻塞。Chrome终态实际截图显示Failed、No report delivered yet及禁用报告操作。临时launcher加入pool关闭lifespan；10秒未退出保留进程和锁，不强杀、不声明已清理。真实隔离MySQL/JWT零付费preflight通过，未创建新Run。ML页视图初次361项gate通过；独立审查发现宿主预算尾注可能越过48KiB，正在按最终返回边界修复，修复前不启动下一业务Run。


## 用户优先取得报告并控制token消耗

用户要求先产出报告，暂停方案扩展和其他优化。已用独立核验42证据/4计算整理 reports/tesla_2024_verified_report.md，并打开供阅读；明确为先行整理报告，不替代应用自动交付MVP验收。Run05已启动，完整问题与64/128/1800预算不变，复用既有provider产物；run_id=workspace-run-a18a8b824c344fb3b542c73677af1b65，deadline UTC06:55:38，launcher session60175。加载Backend ecc37d0与ML a5d04b1；之后只跟踪这一轮及检查报告，避免另开优化或追加付费轮次。

用户进一步明确：报告必须由产品自动产出，手工Markdown不算交付；后续避免截图和UI视觉验证，只核对任务、报告正文、版本持久化及引用数据，页面由用户自行验收。当前仅推进Run05，不扩展优化。


## 产品报告交付优先：失败定位与接续

Run05终态research_failed，seq220，54证据/9计算，未生成checkedCandidate或正式版本。禁止手写报告替代产品交付，后续只读数据、用户自行验UI。

发现retry只继承PDF capture，未复用研究成果。Backend fae8d68新增retry_seed：当前附件重新鉴权后，校验父子问题/cutoff/target/grants相同，读取父scope原始checkpoint并新scope保存证据/计算；不继承消息、pending操作、approval。36相关测试通过，已push。实际父数据seed摘要176805bytes，完整原件证据仍保留。

真实JWT retry06复用成功，1次模型调用即生成报告内容，但MAX_TOKENS被正确阻止执行，终态incomplete，无报告。输出记录10540 candidate、13079 thought tokens；没有读取思考正文。

随后Backend c110554提示报告聚焦必要发现，ML 6b9b0a8对Gemini3启用LOW thinking，维持16384输出上限、模型policy和独立审查；27+2相关测试通过。两commit尚未push。retry07已启动，目录/tmp/cited-alpha-report-retry-07，launcher session48229；从retry06接续同54证据/9计算。仅推进报告产出，不启动新研究/新UI视觉验证。


### 2026-09-11 报告交付修复与验收范围

用户明确将本轮验收收窄为接口和持久化数据：报告正文、版本、引用和字段级定位，网页视觉由用户自行检查。继续以产品任务自动生成和入库为交付目标。

真实候选正文仅 8,261 字节，完整证据包约 5.7 MB，被旧 2 MB 整包限制误拒绝。现将完整证据包上限统一为 8 MiB、检查点上限 16 MiB；审查模型输入共享相同来源页的原文和坐标，实际输入由约 252 万字符降为约 24 万字符，完整原始证据保留。Backend 63 项、ML 29 项针对性测试通过。取消任务的显式重试入口与证据恢复已对齐，额外 14 项 admission 测试通过；保留原任务，重新鉴权后创建子任务。

retry-08 在准入前被旧 canceled 限制拒绝，回读确认未创建子任务，所属进程已关闭。修复后 retry-09 已进入真实执行，复用 54 条证据和 10 项计算。尚未取得已审查且持久化的报告版本，不标记交付完成。

本轮最终回读：retry-09 因 MAX_TOKENS 终止；retry-10 将单次输出配置提高至 32768，首次 MALFORMED_FUNCTION_CALL 后由既有框架恢复，真实报告已进入独立审查。审查指出 11 处缺少字段引用或计算绑定；Agent 补至 62 条证据、13 项计算并提交修订稿，但最终执行回执失败（research execution did not acknowledge completion）。真实 MySQL→GCS 校验最后检查点 sequence=43、5942743 字节，checkedCandidate=false；reportVersionId=null，仅原初始化版本1存在。第二次 submit_report 意图已持久化，尚无完成结果，不能宣称报告交付。未继续付费重试，需定位 check-draft 回调失败后再恢复。Backend 修复提交 aaea12f、ML 修复提交 57ab161，尚未推送；原有无关改动保留。


2026-09-11 分层证据首轮实现：参见 31_layered_evidence_and_reference_callbacks.md。check-draft/calculate 使用绑定检查点引用，真实修订稿请求 5,621,131 → 29,955 字节，原证据和计算不变。未做 UI、付费重跑或部署。


### 2026-09-11 成功报告交付（本机产品环境）

后续修复与最终验收见 [32_report_recovery_fixes.md](32_report_recovery_fixes.md)。真实 Run `workspace-run-f8754e6c9bf94678ab1c5550afd69058` 已 succeeded，Tesla 2024 报告版本 2 正式入库，5 章、58 个引用节点、61 条证据、18 条计算；3 项独立检查 passed。全部引用 API、正文、SEC 表格锚点与 PDF 第 5 页原文校验通过；PDF 抽查精度为 page。该结果是本机产品链路成功，不等于 Google Cloud 线上发布验收。

修正前述旧体积测量：标准化证据回调实际 9,449,369 字节，改为检查点引用后约 29,955 字节；完整报告包、检查点存储及 DAO 指针统一 16 MiB 边界。复用原稿的最后一次任务只调用 1 次审查模型、0 次写作模型。
