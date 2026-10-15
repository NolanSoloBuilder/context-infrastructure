# 生产接入差距与最小实施方案

2026-09-11，只读快照。Run04由Root运行，本审查未触碰其进程/配置，也未创建Run、调用模型、DocAI、上传或发布。目标是复用当前唯一真实admission→outbox→consumer→Pi→callback→报告交付链，不把/tmp composition变成另一套生产运行器。

## 已实际回读

GCP项目cited-alpha-20260701、region us-central1。脱敏证据 `/tmp/cited-alpha-production-readiness-evidence.json`；只输出配置白名单，未落盘secret正文。源码观察时Backend5178d5e、ML66ad4b2（原financial分支，保留dirty）；这些不是线上镜像commit。

|服务|实际revision|镜像commit|timeout / concurrency / maxScale|
|---|---|---|---|
|Backend API|00047-nfj|24b91fb|300s / 80 / 未在本次表内采集|
|Backend runner|00023-rvm|24b91fb|1800s / 1 / 2|
|ML API|00043-5lv|9a6c7e4|900s / 40 / 未在本次表内采集|
|ML runner|00023-9xq|9a6c7e4|1800s / 1 / 1|

两runner当前均1CPU/2GiB。MLrunner模型开关false(disabled=false)，MLAPI MODEL_CALLS_DISABLED=true。四服务secret挂latest；当前ML secrets白名单没有research-runtime，document-ai项目/位置/processor为空，无batch bucket；模板源码虽已有ML数字secret占位，不能当作部署已生效。当前源码prod.yaml两模型场景仍gemini-3.5-flash；本地canary用3.8，不可默认认为相同模型已验收。

Cloud Tasks workspace-runs RUNNING：maxConcurrentDispatches2，maxDispatchesPerSecond1，maxAttempts5，retryDuration7200s。API启用调度，明确目标是workspace-runner `/api/v1/workspaces/internal/run-task`，audience相同，dispatch专用SA。runner调度开关false正确，避免消费者再次当调度器；不是未接Cloud Tasks。

IAM已补：MLrunner有DocumentAI apiUser、Vertex user、serviceUsageConsumer；DocAI处理桶MLrunner+DocAI代理有creator/viewer。snapshot桶Backend API/runner有viewer，Backend runner仅checkpoint前缀creator；MLrunner有creator及document前缀viewer。组织继承/deny及实际SA权限调用未验证，不把本地个人ADC成功当SA证明。

## 会阻断正常产品链路的差距

1. **回调应用身份缺口。** workspace-runner云IAM已允许MLrunner，但WORKSPACE_RUNNER_ALLOWED_SERVICE_ACCOUNTS仍只有dispatch。MLcallback将被应用拒绝。且直接把ML加入现有全局allowlist会连同run-task能力一并扩大，需先分路由授权。
2. **重入请求容量死锁。** MLrunner唯一请求槽被/execute占据；Backend/check-draft又调用同MLrunner的read-verified和/review，会等不到槽。Backend两个实例各只1槽，queue并发2可同时占满长consumer，使两条MLcallback都无法进入。这里不是仅性能慢，是闭环阻断。Cloud Run水平扩展已被maxScale封顶。
3. **正常Web PDF读取身份缺口。** public Backend API的SA不在MLrunner IAM/应用allowlist；真正Web source/source-page由API请求ML读字段，而本地统一token掩盖了这一点。ML当前role=workspace-runner才挂document routes；MLAPI并未提供可直接替代的只读接口。
4. **运行参数未生产化。** 新镜像尚未部署，runtime YAML默认disabled/callback为空；Backend源码admission默认30模型/100工具/900秒，本地固定64/128/1800；模型SDK本地单attempt/66总尝试/20秒spacing是临时audit约束，生产ResearchVertexClient允许最多4attempt，不具备同一审计策略。参数不能只把/tmp monkeypatch照搬。
5. **普通上传与研究复用未完成。** 本地恢复parser只消费已付费36页真实产物；不是生产parse artifact复用。生产fresh freeze仍可能与普通上传worker重复解析，batch operation结果未知恢复也不能靠/tmp原文件。设计19的持久intent/operation/shard manifest/resolve-bind仍待实现。此次不通过“再parse一次”掩盖缺口。
6. **用户产物验收未闭合。** 当前Run04结果由Root验收；短核验、完整财报、跨源报告、续研版本与Chrome字段/计算/恢复等04条款不能因IAM/CI通过而勾选完成。解析页field与原PDFpage必须继续独立标示。

## 路由级权限：先做这一层，不先扩大统一allowlist

沿用现有OIDC验证得到typed identity.email，新增轻量能力依赖，不能在router重写Google token校验。配置字段名称以下为建议新增，非现有可用env。

- Backend `middleware/workspace_internal_service_auth.py`继续验证issuer/audience/email；新增能力检查：run-task只dispatch；research callback只MLrunner。建议 `RESEARCH_CALLBACK_ALLOWED_SERVICE_ACCOUNTS` 与既有dispatch配置分离。上层transport allowlist是集合，路由必须再收窄。callback的scope/lease/sequence/receipt检查继续由现有CallbackService执行。
- ML `core/internal_service_auth.py`同样认证后分能力：execute仅Backend runner；freeze仅文档准备的授权执行身份；review仅Backend callback权威身份；read-verified/read-page-image允许Backend runner和API。建议分别 `RESEARCH_EXECUTION_ALLOWED_SERVICE_ACCOUNTS`、`RESEARCH_REVIEW_ALLOWED_SERVICE_ACCOUNTS`、`RESEARCH_DOCUMENT_WRITE_ALLOWED_SERVICE_ACCOUNTS`、`RESEARCH_DOCUMENT_READ_ALLOWED_SERVICE_ACCOUNTS`，或一个typed capability mapping。所有分组默认空/拒绝，不从“能读”推导“能付费”。
- 影响ML三个research routers及Backend `workspace_run_internal/research_router.py`、run-task router。先测试API身份可读而freeze/execute/review403；MLrunner可callback而run-task403；dispatch可consume而callback403。再扩云invoker和transport身份集合。
- 不把ML读取权限当最终用户授权：Backend原owner→workspace→artifact version→citation→evidence→source run→当前附件链每次仍执行；材料cache不缓存这个结论。

## 容量方案：受限单Run灰度与长期隔离分开

### A. 最小受限灰度（复用四个现有服务，不能当普遍容量保证）

先把queue并发降为1（仅灰度环境/明确配置变更），两个runner concurrency建议4，maxScale先维持Backend2/ML1。仅调大concurrency不够，还必须：

- Cloud Tasks身份是唯一consumer入口；应用对同时运行的research executor做真实Run lease和**立即拒绝/重试**的容量闸门，不能拿住HTTP槽排队等待permit。一个实例最大1个模型execute；review最多1、document冷读最多1；其余请求快速503/429可观测。不得对unknown provider请求自动retry。
- 共享材料cache的1个冷loader不能成为HTTP请求无限队列；其16 pending-key上限是内存保护，不是控制面reserved slots。容量闸门必须在读取/验证大对象前执行，等待者不持有稀缺HTTP槽无限期排队。
- Cloud Tasks并发1和唯一消费入口给Backend留下callback余量；ML唯一execute占1，独立read/review占有界剩余槽。静态6路以上并发不是解决办法。测试必须制造最长consumer+checkpoint+source verification+review闭环，证明在冷读/失败/重试负载下callback可在lease前成功。
- 初始资源至少做2CPU/4GiB候选压测评估，不直接声称足够。已知一次完整材料56.95MB，parsed Python对象、normalizer replay、副本、PDF/Pillow、Pi模型上下文及256MiB cache会叠加；上线前测RSS峰值与CPU/event-loop stall，保留至少30%内存余量，再定值。单CPU同步normalizer可能阻塞同loop；必要时将纯验证CPU工作移到受限executor并测deadline，不改权威算法。

A只在“单Run、已认证有界流量、快速容量拒绝”的明示边界可验收；Cloud Run没有按path保留槽，无法给共享公共流量下的callback提供硬隔离。若无法证明这些边界，不开放常规MVP流量，直接B。

### B. 推荐的长期最小隔离（复用已有代码和镜像，不复制运行器）

执行与控制必须在不同Cloud Run容量池。优先利用现有API部署承载控制/阅读，但要认识其代价：

- Backend API新增挂载实际research callback router（当前仅runner挂），以API URL为callback audience；仅MLrunner身份能访问。这让consumer只留在workspace-runner，API回调不会被长consumer占满。API已有JWT流量，需callback较高并发、短时上限和整体限流；如其业务流量无法保障lease延迟，再以同Backend镜像新增research-control角色/部署，仅挂callback，不复制业务服务。
- ML API可以只挂两条实际document-read路由，保留MODEL_CALLS_DISABLED=true，API及runner均按read能力授权；接入shared材料cache。执行/freeze仍只在MLrunner。**独立review不能直接挪入现有MLAPI并取消全局禁模型开关**，否则旧公开模型入口可能被一并开启。
- 因此review长期用同ML镜像一个最小research-control角色/独立部署，仅review与必要读取，权限只Backend callback身份；没有/execute、freeze或旧公共模型路由。若强制不新增服务，必须先使MLAPI旧路由模型闸门与review明确按场景隔离，证明公开入口仍disabled；其改动/回归面比新role部署更大，不建议仅为少一个服务采用。
- Backend ML连接拆分目标，不改执行器：现有 `MLWorkspaceService`固定执行URL；为review与document-read提供purpose-specific固定URL/audience连接配置（建议 `RESEARCH_ML_REVIEW_URL/AUDIENCE`、`RESEARCH_ML_DOCUMENT_READ_URL/AUDIENCE`）。freeze仍执行目标。每个客户端只允许对应固定HTTPS目标和OIDC audience，不接受请求URL。
- 新控制池可初始min1避免冷启动、concurrency按实测、maxScale2；模型review最多1/实例、文档冷验证1/实例、响应体/期限均有界。执行池继续concurrency1/maxScale1做单Run灰度，控制池容量不被/execute占用，才构成结构性保证。代价是额外服务SA/IAM/配置/常驻成本与部署回读；业务算法、数据库、证据合同和唯一consumer全部复用。

## 具体实施文件与配置顺序

1. 完成上述能力依赖和role注册：两仓auth文件、ML `mindspace/app/launch.py`、Backend同名launch、三类MLresearch router、Backend callback/run-task router。配套测试身份矩阵、错误audience、disabled配置、公开用户不能越权、unknown callback仍CAS拒绝。
2. 部署模板：两仓 `deploy/cloudrun/prod.workspace-runner.service.yaml`、现有API模板/发布渲染器；如B新增同镜像control-role模板。修改`.github/workflows/docker-build-deploy.yml`及renderer只负责发布角色和固定secret版本，不把自动运行付费canary加入deploy workflow。API/runner/control必须明确commit+image digest+数字secret版本绑定，禁止latest漂移造成生产partial rollout。
3. 配置新ML runtime：enabled及Node绝对路径、Pi模块/app entry、固定Backend callbackURL/audience。先新候选运行器+控制面，Backend research-enabled仍false。新镜像离线Pi/SDK/契约gate通过不等于部署加载成功；用非付费auth/schema/health验收确认路由与依赖。
4. 固定模型/预算策略：沿用注册的两个model-policy场景，决定正式模型是否与3.8canary一致；显式设置SDK总attempt、retry与review上限、取消unknown语义；admission预算用typed配置冻结到Run，不在临时composition里替换。Cloud Tasks/HTTP/Run deadline要预留交付余量：30分钟Run与1800秒HTTP同边界不能确保最后callback/SQL交付有时间；可保持900秒默认或短于dispatch deadline的显式研究上限。
5. 存储/解析：checkpoint/doc/SEC前缀按实际reader/writer SA只读/创建授权，readback采用真实SA无敏感内容的权限检查。现有IAM“看起来有”不是实际服务身份读取证明。NoPDF新解析灰度可先使用已审核的合格历史产物，必须显式historical-import/resolve来源，不能生产引用/tmp或谎报fresh parse。普通上传+多Run复用按19方案做持久产物协调，再进行一次上传/两次研究的真实POST计数验收。
6. 最后仅开放单owner/workspace allowlist，以正常JWT/SSE接纳、真正Cloud Tasks消费、真实OIDC往返、真实GCS+SQL checkpoint和报告版本回读。先短任务再完整财报/跨源；允许结果未知时调查同Run，不能因HTTPtimeout重开新Run。通过后再扩大并发/用户范围。

## 验证与回滚条件

- 零付费：候选路由能力矩阵、默认disabled、错误scope、真实SA对已存在对象只读、Cloud Tasks目标配置/重复消费合同、secret版本和镜像回读；不发送会触发新provider/model的业务请求。
- 离线饱和：模拟consumer持有、callback/check-draft反向review、文档冷读、多个cancel、超载拒绝，确认不会因请求槽或cache waiter饿死；测RSS/event-loop lag，不是只用健康GET作容量证明。
- 显式付费灰度：Root另行启动真实短答/财报/跨源与续研。报告可读、事实/期间/单位/冲突、字段/原件hash、公式、刷新同Run及新版本全部按04验收。当前Run04仅本地真实业务链路证据，不替代这些线上身份/调度验收。
- 回滚先关admission，排空/标明仍运行和unknown的任务，再回镜像/数字secret；不能把v2 checkpoint交给不识别v2的旧runtime，也不能回滚后自动重放unknown付费intent。

本轮没有生产NoPDF解析、模型、DocAI或发布操作。配置读取、IAM/队列回读及代码差异已验证；产物质量、线上SA实调用、生产队列闭环和容量SLO仍待验证。

优先扩展已有测试入口而非重建harness：Backend `test/test_workspace_internal_service_auth.py`、`test/test_research_callback_routes.py`、`test/test_workspace_run_cloud_tasks_transport.py`、`test/test_workspace_run_task_consumer.py`、`test/test_research_callback_document_client.py`；ML `tests/test_internal_service_auth.py`、`tests/test_research_execution_transport.py`、`tests/test_research_document_version_routes.py`。另加纯role注册/固定目标能力矩阵和有界并发闭环fixture，加入两仓现有portable gate显式manifest。
