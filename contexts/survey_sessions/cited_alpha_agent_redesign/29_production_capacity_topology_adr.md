# ADR补充：一个新增ML control服务的生产研究拓扑

结论：采纳Root候选，比同时修改MLAPI并新增review服务更小、更清晰。新增一个私有Cloud Run服务 `cited-alpha-research-control`（建议名），复用同ML镜像和现有service，不增加运行器。Backend API挂真实research callback；长consumer留Backend runner；MLrunner保留execute/freeze；现有MLAPI完全维持禁模型及原路由行为。

本次为只读设计，未改源码/配置、未发布、未调用模型/解析或触碰Run04。

## 路由与实际身份

|目标|允许调用身份|允许能力|
|---|---|---|
|Backend runner /run-task|workspace-dispatch SA|消费已持久化outbox|
|Backend API /research callback|ml-runner SA|checkpoint/calculate/check-draft等现有scope/lease/CAS边界|
|MLrunner /execute、document /freeze|workspace-runner SA|执行和授权文档准备|
|research-control /review|Backend API SA；迁移期保留workspace-runner SA|独立审阅，不能执行研究/解析|
|research-control /read-verified、/read-page-image|Backend API SA、workspace-runner SA|冻结文档精确字段/页图只读|

重要细节：回调现在由Backend API进程执行，review HTTP请求实际token也是API SA。因此不能再声称“API SA仅能读，runner才可review”。API进程承担回调权威与用户读入口两种职责，其服务身份必须具备两种control权限；用户JWT不会直接作为服务token，也不会获得/review访问权限。若未来需要把这两种服务能力完全分开，需独立callback部署/SA或可证明的委托凭据，不应凭任意header区分。

保留runner review能力的原因：现有executor和callback均有reviewer factory注入点，迁移时不能假定永远只有callback调用。实现前逐条确认最终调用图；若已证明runner不再发送review，才移除此能力。此范围最多两个明确Backend SA，不包括MLAPI、dispatch或任意用户。

## 不扩大旧接口权限

MLrunner现有WORKSPACE_INTERNAL_AUTH_ALLOWED_SERVICE_ACCOUNTS保持仅workspace-runner；不把Backend API加进去。旧workspace_agent_step继续现状。MLAPI的channel_file及其他接口、服务SA、MODEL_CALLS_DISABLED=true均不动。

新research-control是独立role分支，注册后立即return，仅actuator、review、两条read；不存在execute/freeze/workspace_agent_step/channel_file/旧public model路径。需要把document router按能力拆出read与freeze子router/共享handler，而不是先注册全部再靠URL字符串删除route。原workspace-runner合并相应子router维持原调用；control只引read子router。

认证复用`InternalServiceTokenVerifier`，根据typed identity.email再做route capability限制。control的总allowlist是API+runner，两类route分别取review/read子集。它的role和不可达路由还提供第二道能力边界，不能仅靠共享全局allowlist。Backend的callback独立能力依赖仅MLrunner；原run-task依赖仍只dispatch，不能以扩大WORKSPACE_RUNNER_ALLOWED_SERVICE_ACCOUNTS让ML获得run-task权利。

## 最少连接配置

保留既有Backend `WORKSPACE_ML_RUNNER_URL/AUDIENCE`用于execute和freeze，不改MLWorkspaceService全局目标，避免影响旧workspace_agent客户端。

只新增一组固定目标：`RESEARCH_ML_CONTROL_URL`、`RESEARCH_ML_CONTROL_AUDIENCE`（建议字段，当前尚未实现）。两种control请求复用同一个窄HTTP连接/现有InternalServiceTokenProvider，URL与audience显式验证，不从业务请求取URL。

- MLResearchReviewService默认control连接；测试connection override保持兼容。
- MLResearchDocumentService应保留原`connection`作为显式两路测试覆盖，并增加`read_connection`或等价purpose-specific连接。默认freeze→runner、read-verified/read-page-image→control；不要把整client的_base_url改control导致freeze404。control未配置时生产应fail closed；若需滚动迁移旧目标fallback，必须显式有期限的兼容配置，不能悄悄用runner重新制造重入阻断。
- MLrunner YAML `research-runtime.backend-base-url/backend-audience`改成Backend API的固定HTTPS URL。Backend API增加callback route与对应OIDC audience配置；scope/lease校验仍原服务。其公共allUsers Cloud Run IAM并不放开callback，应用OIDC是此路径必要边界。
- 新control使用自身URL做WORKSPACE_INTERNAL_AUTH_AUDIENCE，两个Backend SA在Cloud Run invoker和应用allowlist均授权；其运行身份是独立control SA，不冒用ml-runner SA。

模型场景仍沿用workspace_report_semantic_verifier，不新造模型policy。control需要MODEL_CALLS_DISABLED=false，但因角色只挂review而不会开启旧MLAPI公共模型路径。MLAPI继续true。建议把review/read能力分组存typed配置；只为control部署加最少2个能力集合，不给所有服务重复一套不消费的配置。

## 原始文档及其他权限

control只需要snapshot桶`workspace-source-snapshots/documents/sha256/`下原PDF/provider/manifest对象GET（当前DocumentVersionStore.read，无需list/create/delete）。独立SA授最小前缀条件viewer，不授DocAI API、处理桶input/output权限、checkpoint写入或SQL写入。它不读取原始上传的可变bucket，也不补解析，只读已冻结receipts。

review需要Vertex调用及serviceUsageConsumer，固定项目/region和已注册模型；配置secret只提供该role实际需要的参数。ADC quota只在服务配置内设置，不带个人凭据文件。若同一镜像启动仍因为顶层import/lifespan触发PG/MySQL/Mongo/provider初始化，应先调整role启动边界为惰性依赖，不为绕过启动错误给control加整套数据库/DocAI权限。文档只读factory可显式构造只读store，避免默认DocumentVersionService构造未使用的repository/source_reader。

Backend API原有snapshot viewer可继续支撑原PDFsource-file；Backend API承载callback后如某callback实际创建checkpoint，则需和原runner同样的**checkpoint前缀objectCreator**权限。不能遗漏这个权限迁移：callback保存进度/checkedCandidate由API SA写GCS，当前已回读IAM中creator只给Backend runner。仍不授覆盖/delete。

## 容量保证与代价

拓扑切断三条环：consumer占Backend runner不占callback API；execute占MLrunner不占read/review control；control内部read/review不再回调自身。因此无需为了回调给MLrunner开放大量concurrency。新增服务承担源阅读+review的短工作，而非第二个研究执行器。

建议首轮灰度queue并发1、MLrunner concurrency1/maxScale1、Backend runner concurrency1；control候选2CPU/4GiB、concurrency4、maxScale2、minScale按冷启动实测决定。此为压测起点不是承诺资源足够；Pillow/PDF/normalizer解析会与review共享CPU，256MiB验证cache还叠加Python材料与模型上下文。必须测峰值RSS/event-loop延迟，不依据56MB wire大小估算运行内存。

control应用采用独立能力闸门：最多1个read冷验证、最多1个review/实例，超载在重活前立即429/503；不在HTTP槽内无限等锁。缓存单flight的等待数量不是review预留容量，尤其多个同key读等待也要受外层读取闸门限制。路由容量检查后才启动模型/对象读取；模型已开始后不得把超时视为可重发。暖读也受有界请求数/响应体限制。

Backend API仍承载公网业务，不能把concurrency80称callback硬隔离。先按来源分流量闸门/短请求deadline、测最坏公共流量下callback完成时间小于lease余量；若达不到，即使“最多一个新增服务”的目标也必须重新决策Backend独立control池，不能用假保证验收。此候选能保证长consumer不抢callback池；它不自动保证公网流量任意大时callback可用。

review超载导致技术失败应沿原check-draft失败边界保持不交付，不应自动重试付费review。文档读超载可由正常UI显式重试；后台验证仍按原Run期限/unknown结果语义处理。control扩容会带来独立cache冷启动；不要用跨进程共享session或无授权磁盘缓存规避。

## 必做回归及灰度

1. 纯role路由快照：control仅review/read/health；原runner旧workspace_agent保留、执行/准备可用；旧MLAPI路由与禁模型不变。API服务token不得访问MLrunner paid入口，dispatch/ML身份不得进入control；Backendcallback只MLrunner、run-task只dispatch。
2. 两路连接测试：freeze仍runner，read/review均control；URL/audience固定且正确token；control缺配置拒绝；测试override仍工作。错误scope/撤附件/跨版本/篡改receipt保持原有拒绝。
3. 容量回归使用无模型替身持有长execute/consumer，同时走真实HTTPcallback→control字段核验→review；强制read慢线程、同key20并发、review占用、反复取消、实例重启/冷cache。观察callback延迟、队列年龄、active/pending permit数、event-loop lag、RSS以及review调用计数；过载快速拒绝而非等到全局deadline。验证取消不提前释放真实下载资源。
4. 只读候选验证：数字secret版本+镜像digest+role+路由+SA/IAM回读，用服务身份读取已存在的批准原件并检查SHA。阶段不新解析PDF、不发模型、不提交业务Run。
5. Root另行显式允许真实单Run灰度后，通过正常API/SSE→Cloud Tasks→runner/Pi→APIcallback→control→SQL报告交付，再Chrome引用、同Run刷新、双视图和续研版本。现有本地Run04不能替代线上新拓扑的身份/并发验收。

## 涉及文件

Backend：`mindspace/app/launch.py`、`middleware/workspace_internal_service_auth.py`、`router/v1/workspace_run_internal/research_router.py`；新增窄control连接模块（复用现有token provider）；`ml_research_review_service.py`、`ml_research_document_service.py`；API/runner部署模板及数字secret渲染；相应auth/callback/client/CloudTasks测试。

ML：`mindspace/app/launch.py`及runtime-role枚举/生命周期；`core/internal_service_auth.py`能力依赖；`research_review_router.py`、document read/freeze子router；已有只读DocumentVersionService factory注入共享材料cache；新增同镜像control部署模板/发布渲染和最小配置；role/auth/route/超载测试。研究执行器、工具循环、source证据和报告schema不变。

采纳后可作为生产接入ADR补充；本轮仅写/tmp文档，未修改应用或发布。
