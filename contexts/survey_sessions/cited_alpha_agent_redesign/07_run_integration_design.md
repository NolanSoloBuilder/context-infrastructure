# L2：通用研究 Run 接入现有执行与交付体系

2026-09-10，状态：基于当前三仓源码的接入设计；本文没有修改应用代码。现有新增纯合同、SEC原文验真、版本DAO、引用GET路由已有离线测试，但完整研究运行接入与生产验收尚未完成。

## 目标与边界

用户提交研究问题后，浏览器观察同一个持久 Run。现有队列投递到 Backend Runner，Runner 驱动 ML 中的 Pi 通用循环；工具读取原文、登记证据、执行计算，Agent 自主写作和修订。Backend 验证原文与独立审稿回执后原子保存报告版本，浏览器断开不影响任务。

保留现有 Cloud Tasks、Outbox、Scheduler、Run/Step lease、权限和版本表，不新建调度系统。新路径不能进入旧 Need/维度/三 Gate 合同，也不能生成假的旧 Receipt。通用循环可有一个持久执行 Step；搜索、阅读和写作以工具事件记录，不转成预先冻结的业务阶段图。

## 当前真实调用链与接入位置

路径以 Backend `/Users/xuhao/Documents/Other/mindspace_backend` 为根。

| 环节 | 现有代码入口 | 新路径处理 |
| --- | --- | --- |
| 接纳 | `service/workspace_run_operations.py:create_run` | 复用owner、workspace/chat绑定、request规范化、idempotency、预算、asOf和ContextPack冻结；把runtime选择从旧TaskIntent构造前分出 |
| 原子创建 | `domain/dao/workspace_dao.py:create_or_get_run`，`_persist_workspace_run_acceptance`调用处 | 复用Run+queued Event/Outbox事务；只让创建赢家dispatch |
| 投递 | `service/workspace_run_dispatch_service.py:dispatch_run/dispatch_pending` | 原样复用；deployed补偿由现有Scheduler承担 |
| 消费 | `service/workspace_run_task_consumer.py:consume` | 保留OIDC外层认证、Outbox/Event/Run身份和execution_scope交叉检查；仍只调用executor.execute_run |
| 执行 | `service/workspace_run_operations.py:execute_run` | 当前一开始解释v2/v3 admission，随后freeze旧Harness contracts；新runtime必须在这里之前分派给独立ResearchRunExecutor |
| Run/Step租约 | `_claim_run_for_execution`、`WorkspaceRunControlService`、`WorkspaceRunLeaseHeartbeat` | 复用claim/transition和同一`workspace_agent_execution` Step，便于现有cancel/watchdog识别；不新增planner/retrieval/writer阶段Step |
| ML传输 | `service/ml_service/ml_workspace_service.py` | 原`run_workspace*`发送到`/agent/v1/workspace-agent/runs*`，均带旧运行合同；新增薄research transport，不改旧接口语义 |
| 交付 | 新`service/research_report/delivery.py`和`domain/dao/workspace_research_report_dao.py` | 已有结构/检查回执/原子版本与终态机制；从新executor直接进入，跳过`_apply_workspace_agent_result`旧合同 |
| 对话终态 | `service/workspace_run_message_finalizer.py`，由TaskConsumer再次幂等调用 | 保留单次assistant终态消息；验证新的`artifact_diff`形态是否被现有finalizer正确投影 |
| 引用读取 | 新`router/v1/research_report/router.py`→`ResearchReportOperations` | 已有owner-scoped GET；原文HTML/PDF查看仍需后续接入 |

## 运行轨道绑定：必须显式冻结

采用现有 `harness_contract_version` 作为唯一持久运行轨道权威，新增值 **`research-v1`**。这遵守现有domain/model README的单权威约束，避免general任务以假的v2记录运行。`WorkspaceRunModel`当前String(8)且CheckConstraint只允许v2/v3，需把列扩为String(32)，并通过向前兼容迁移扩展check；旧行v2/v3原样保留。

ContextPack只冻结运行参数、实现revision及交叉校验，不再独立选择runtime：

```json
{
  "researchExecution": {
    "schemaVersion":"research-execution/v1",
    "harnessContractVersion":"research-v1",
    "runtimeRevision":"server-selected-release-id",
    "objective":"用户原始问题",
    "asOf":"接纳时冻结的时间",
    "target":{"artifactId":"...","baseVersion":1},
    "authorizedDocumentVersions":[],
    "template":{"id":"financial-analysis","version":"1"}
  },
  "scope":{"userId":"...","workspaceId":"...","runId":"..."}
}
```

`create_run`按Backend配置选择并同事务冻结唯一轨道；客户端requestPayload不能覆盖。worker、retry、resume、watchdog、admission projection、payload及telemetry都按`harness_contract_version`显式识别三种轨道。research-v1跳过旧TaskIntent/Need/Gate构造，只编译新轻量运行参数；ContextPack声称research-v1而Run列不同则拒绝。retry继承父Run轨道，恢复不重新选择当前配置。

部署顺序：先expand数据库约束→部署支持research-v1但接纳关闭的全部消费者→确认没有旧worker仍可认领新轨道→启用单workspace canary。回滚只停止新接纳，不能让旧worker把research-v1当v2或因未知值循环claim；仍须保留可处理research-v1的worker完成/取消已有任务，或先在dispatch/claim层明确隔离。禁止默认fallback到旧writer。

这是主方案审核决策，取代此前ContextPack运行轨道优先的提议。需同步当前model/DAO文档中“只允许v2/v3”的约束、数据库迁移与所有消费者，再启用canary。

## 内部请求与响应

建议 ML 新增受服务身份保护的research endpoint。对外Web仍用既有Workspace Run接纳/观察API。

请求由Backend生成：

```json
{
  "schemaVersion":"research-execution-request/v1",
  "scope":{"userId":"...","workspaceId":"...","runId":"..."},
  "executionScope":"prod",
  "attempt":1,
  "runtimeRevision":"...",
  "harnessContractVersion":"research-v1",
  "objective":"...",
  "asOf":"...",
  "target":{"artifactId":"...","baseVersion":1},
  "authorizedDocumentVersions":[],
  "budget":{"remainingModelCalls":24,"remainingToolCalls":48,"remainingSeconds":600},
  "checkpoint":null
}
```

ML不能据payload绕过自己的服务身份认证。权限文档版本清单来自Backend已授权资料，不能由Agent构造。Model-policy选择仍在Python；Pi subprocess无用户个人凭据，不接受任意shell工具。

响应包含`ready_for_delivery | incomplete | canceled`、当前draft `{document,citations}`、host-owned `evidenceCatalog/calculations`、checkpoint和usage。`ready_for_delivery`只表示写作候选可进入Backend交付，不能让ML直接标Run成功。ML返回的任意pass字符串都不能代替Backend原文验真。

ML已有入口：`service/research_agent/ResearchSession.run`，组合 `PiProcess.run`、工具和 `ReportDraftTools`；其`ready_for_delivery`是草稿状态，尚未持久交付。请求和响应需要在transport层设总bytes与集合上限，不能将16MB subprocess frame上限直接当HTTP/DB无限输入许可。

## 原文检查与独立审稿的边界

当前新增Backend `ResearchSourceIntegrityService` 可按configured bucket读SEC保留对象并独立验证exact cell/paragraph。已有Document路径仍需实际授权版本/原文reader；没有reader时必须明确拒绝，不能用ML工具自报verified_read替代。

`ResearchReportCheckAuthority`当前代码要求两个reviewer，ML已有 `ResearchReportReviewer.review(question,document,citations,evidence,calculations)` 在一次独立模型请求内返回事实与编辑结果。按[09报告交付设计](09_report_delivery_design.md)的新决策，接入时将Backend改为**一次独立于writer的审查，同时记录事实支持和编辑质量两个维度**。我认可该决策：目前没有证据证明第二次同输入审查足以抵偿成本。每次review绑定最终bundle hash及用户问题，独立上下文不读取writer自评；不得将一次调用描述为两次独立审查。

为让Agent自主修订，建议draft检查走受鉴权的内部回调：ML submit_report→Backend校验Run lease/owner和源→Backend调用一次ML独立review endpoint→返回精确block反馈。回调必须绑定当前Run/attempt、bundleHash和服务身份，不能成为公开通用模型入口。

待通过后，Backend将检查回执保存在受信checkpoint，再执行`ResearchReportDeliveryService`。当前service每次deliver都会调用authority：实现应优先提供可回读、hash+Run绑定的已有authority结果，避免同一已通过draft在交付时重新付费审稿。缓存必须由Backend保管，不能接受浏览器/模型提供的receipt；原文可用性变化时依政策重新验证。

内部回调会形成Backend→ML执行→Backend检查→ML review链，需要Cloud Run并发与timeout预算设计。MVP可用双向事件传输让Backend host承接model/tool回调，减少递归HTTP，但不得为省事放松源验真归属。

## 生命周期、恢复与幂等

### 运行状态

复用queued→leased→running→succeeded/failed/canceled。草稿未通过检查时Run继续running且Agent修订；预算耗尽时保存未交付checkpoint并结束incomplete对应的失败/可重试状态，不能把无产物Run标succeeded。需要等待用户输入时再复用waiting，不能把普通检索零结果当必须等待用户。

### 心跳与取消

现有heartbeat每20秒更新Run及`workspace_agent_execution` Step，只记录`_lost`并在最后assert。新executor需让失租/取消信号主动cancel当前ML调用；ML收到取消时cancel `ResearchSession`，`PiProcess` finally终止child。仅交付前阻止写入仍可能继续消耗模型预算，所以工具和model调用前都应检查截止时间与当前任务取消信号。

取消最终权威在Backend Run，ML断开不能覆盖已经canceled的Run。交付DAO在锁内再次核对lease、cancel_requested_at和deadline。中断后旧worker不能保存checkpoint或交付，即使它稍后得到模型成功响应。

### Checkpoint

ML已有messages恢复参数，尚未证明持久化。建议新增 `research-checkpoint/v1`：runtimeRevision、model/context revision、scope、sequence、messages、tool catalog、calculation requests、usage ledger、last completed tool call、draft/check receipt reference以及完整hash。

落点确定为：**现有 `workspace_run_steps` 的 `workspace_agent_execution.output_json` 保存有界pointer envelope，完整checkpoint与已检查候选作为同一包Backend-owned数据保存于私有不可变内容寻址对象**。不新增任务表、不把每个候选伪装为旧业务阶段。模型定义的JSON列本身没有业务容量上限；现有`transition_run_step`用于状态迁移并会投影事件，缺少running→running的checkpoint序列CAS，不能直接拿来当候选缓存。

新增小DAO方法`save_research_checkpoint`，锁序Run→outer Step，检查owner/execution_scope、Run/Step lease、未取消、deadline、expected sequence；只更新下面的envelope和必要的last_progress_at/usage_summary，不写完整内容进event/outbox：

```json
{
  "schemaVersion":"research-step-state/v1",
  "sequence":7,
  "checkpoint":{"objectKey":"research-runtime/<owner-scope-hash>/<runId>/sha256/<sha>.json","objectSha256":"...","byteSize":12345},
  "candidate":{"candidateId":"...","bundleHash":"sha256:...","reviewRulesVersion":"1","status":"checked"},
  "usage":{"modelCallCount":8,"toolCallCount":15}
}
```

Envelope上限建议16KiB，单一完整checkpoint上限8MiB，candidate bundle沿用合同2MB上限；超限明确报错，不截断messages/catalog后继续恢复。具体值应按一份完整研究报告测量确认。同一个checkpoint对象中的Backend-owned candidate区包含exact bundle、用户问题hash、原文验真摘要、一次独立review完整结果和Backend检查回执，避免两个pointer分别更新后出现候选与messages不同步。Run.metadata只保留最终无正文检查摘要或candidateId，用于轻量状态显示，不作为候选权威；此前新增`researchReportCheck`字段应进一步收敛至引用/摘要。

私有对象存储复用已配置private bucket即可，不为MVP再建调度器；新增明确allowlisted `research-runtime/` prefix，独立reader必须校验scope-derived key、raw hash、bytes、JSON schema，不能把任意gs URI当读权限。该prefix与SEC原文prefix分离，禁止沿用source public-publication拷贝路径。消息和catalog含私有研究材料，runtime对象从不公开发布。

先用`ifGenerationMatch=0`写不可变对象再CAS推进DB pointer；对象写失败不能推进sequence；CAS失败可能留下不可达对象，后续按保留策略清理，不能回滚删除可能已被另一次合法重放引用的对象。相同sequence/inputHash重放返回已保存pointer，内容不同拒绝。

跨进程恢复时，Backend新lease owner从owner-scoped Step读取pointer，验证对象bytes/hash/schema与scope，再将messages/catalog/计算/已消耗预算交给ML。候选记录只能由Backend检查服务写入，不能接受ML重传receipt来重建checked状态。恢复发现candidate exact hash已通过且目标版本未变，直接source可用性策略复核后交付，不再付费审稿；若再次submit不同draft则先以CAS失效旧candidate并重新检查；新候选检查失败不能误交付上一次已通过的旧草稿。

最终交付DAO需要在同一Run/Step锁内读取candidate pointer并比较bundleHash、检查规则版本及目标scope，不能只依赖调用方传入的check_receipt。当前新DAO尚未实现该pointer回读，这是上线前必须补齐的权威链。

只在model/tool结果完整落地后推进checkpoint；网络超时表示观察未知，不能立即重发同一工具调用。SEC/document只读抓取可安全重试，但模型调用重复仍计费，usage不能归零。恢复预算=冻结总预算减已持久用量，不能每次重启重新获得24次调用。

### 幂等

- 接纳：沿用owner+workspace+idempotencyKey；增加新运行请求hash比较，相同key不同objective/target应冲突，避免现有仅返回旧Run误导用户。
- 队列：原Outbox与TaskConsumer去重、Run lease排他。
- Tool：callId绑定参数hash和结果；已完成读工具重放返回原结果与证据ID。
- 检查：Run+bundleHash+reviewer version缓存检查结果，不认可writer自评。
- 交付：新DAO deterministic research-version ID由Run派生；sameRun+sameBundle+sameTarget/baseVersion返回原version，变化拒绝。
- 版本冲突：用户已修改目标Artifact时保留研究候选，返回显式冲突，禁止覆盖用户新版本。下一步可让用户选择合并或创建独立报告，不自动重跑整项研究。

## 实施顺序与验收

1. 冻结research-v1唯一轨道、checkpoint、ML执行/review/callback合同，补跨仓schema fixtures；实现轨道列/check的expand迁移及全部消费者支持，接纳开关保持关闭；确定预算/usage归属。
2. 实现新ResearchRunExecutor和薄ML transport；复用TaskConsumer/Dispatch/lease，接假ML离线E2E，验证没有进入旧freeze/Need/Gate。
3. 补Checkpoint CAS、恢复、取消传播和同一Run重投；用进程故障/失租/重复event注入验证。
4. 接真实SEC source verifier与一次独立综合review（分别记录事实支持和编辑质量），再接独立report delivery与message finalizer；单公司窄问题先验完整链，再验完整分析与计算。
5. 补授权Document源验真与多信源报告；读回版本及引用坐标、刷新后恢复、旧版本保持原文。
6. 发布前MySQL并发测试：双worker同Run、双Run同baseVersion、取消和交付竞争、事务中断重投。SQLite不能证明行锁行为。
7. Chrome真实验收报告可读、用户问题被回答、数字可定位、计算可复算；当前源码/单元测试不替代此关。

## 当前未解决问题

- runtime绑定尚未接纳/执行全链路冻结，不能只增加Pi进程调用即称可上线。
- Backend两个reviewer合同待按09改为一次综合独立review；草稿修订反馈与可信候选pointer尚无真实跨服务通道。
- Checkpoint持久化/CAS、usage恢复及取消传播尚未接通。
- 当前source reader只完整支持SEC HTML；Document独立bytes/字段reader、原文viewer路由仍需完成。
- 新report version的payload读取、版本恢复、编辑、发布都需schema-aware检查；旧financial报告保护不能清空schema绕过。
- 当前交付检查回执记录在Run.metadata，需按本文改为Step pointer→私有不可变候选对象的权威链；完整bundle在version.provenance，敏感rawEvidence不可直接散发到公开页面。
- `artifact_diff`与message finalizer、Web现有SSE恢复投影还需同一真实Run的结果验收。

## 下一条真实 API/DAO smoke 的实际环境缺口（2026-09-10只读）

实时绑定：Backend d191191、ML f0a491c、Web4758ebc，均在用户确认的
feat_codex/financial-report-agent-plan-writer-20260717；不切换、不提交。
本机仅Redis6379和Web8099监听；Backend8079/ML9090/MySQL3306或3307都没有。
cloud-sql-proxy已安装，mysqld/mysql/docker不在PATH。Backend `ENV_MODE=local` 实际
mysql配置是远端34.58.190.182:3306、database=mindspace。**不能直接用此local配置
启动迁移或写验收数据**。本轮没有连接/写数据库，也未运行迁移。

### 最小真实环境与执行次序

1. 准备独立MySQL8数据库与仅该库权限的用户，例如research_api_smoke；可用同项目
   CloudSQL独立库（须Root授权创建），或本机MySQL。不要把生产mindspace当测试库。
   若使用现CloudSQL，代理命令本身只建立隧道：
   `cloud-sql-proxy --address 127.0.0.1 --port 3307 cited-alpha-20260701:us-central1:cited-alpha-mysql`。
   专用secret override必须明确mysql.host=127.0.0.1、port=3307、database=隔离库、
   unix_socket为空，凭据不写命令行/文档；启动前只打印上述非敏感字段确认。
2. 隔离库建立当前完整schema，再运行现deploy/schema_migrations.py注册链；新研究轨道
   注册项是mindspace.script.migrations.expand_workspace_research_track。不能只跑这一项
   假设空库已有workspace_runs。迁移后用INFORMATION_SCHEMA只读核对VARCHAR32和
   v2/v3/research-v1 CHECK，校验step/outbox/artifact版本表存在；不能Base.metadata.create_all
   通过就宣称真实MySQL migration验证。当前没有已核验的隔离schema，因此尚不可执行此步。
3. 在隔离库创建真实测试用户，通过现用户JWT机制获得本地短期token（不落日志），
   正常API创建Workspace/Chat。Research allowlist只包含该workspace，execution_scope=local，
   cloudtasks disabled走现本地outbox dispatcher。不要注入fake DAO或直接构造Run替代admission。
4. Backend本地启动入口确为`mindspace.app.launch:app`：
   `ENV_MODE=local MINDSPACE_SECRETS_YAML_FILE=/受限路径/backend-smoke.yaml .venv/bin/python -m uvicorn mindspace.app.launch:app --host 127.0.0.1 --port 8079`。
   先确认override被settings消费、绝不能回退当前远端库；ML同理9090，用新代码+本项目ADC。
5. 真正ML→Backend callback仍要求HTTPS固定URL和OIDC。仅设本地auth bypass不能消除
   ML resolve_research_runtime HTTPS校验/ADC token需求。完整local live要有受信TLS的
   Backend本地入口与双方认证配置，或隔离CloudRun runner与可达Backend；当前没有该入口。
   不应临时放宽生产callback客户端HTTPS规则。新线上revision也尚未部署，不能用旧runner替代。
6. 第一次付费执行前，使用正常POST conversation/stream研究请求（用户请求+明确intent/
   模板参数按现requestmodel），检查SSE queued/runId。相同idempotencykey同payload应复用Run，
   改question冲突；SQL回读Run track/context及Outbox原子存在。到这一步可独立证明接纳DAO。
7. 完整交付必须继续真实executor/lease、ML HTTP与Backend callbacks，不能把04内存候选
   直接插入Artifact冒充。回读Step.output_json.researchCheckpoint小指针、真实私有对象
   hash、候选receipt，再确认ArtifactVersion/current pointer/Run终态一致；GET该保存版本、
   citation和source API都用同user token。最后用不同user token确认owner隔离。
8. 恢复验收在第一次真实checkpoint后有意终止本地worker，等租约后由现dispatcher恢复；
   回读sequence递增且没有重复版本。取消/lease过期阻止旧worker写入。MySQL并发测试需
   两个真实连接竞态，不把SQLite顺序测试当锁证明。生产业务库无任何此类写入。

### 可复用与不可替代

- runbook仍可复用端口、API/SSE/回读顺序；其旧Evidence/Need目标不是新report合同。
- test_research_admission/checkpoint_dao/report_delivery使用SQLite同步session适配，适合
  合同回归，不能称真实MySQL API验收；callback测试也有fake边界。
- workspace_run_preview_fake_ml.py与workspace_report_complete_with_gaps_fake_ml.py明确
  fake ML/旧report，不能作为此次真实链路脚本。
- 当前没有可直接运行的research-v1真实HTTP+MySQL smoke脚本。最小待补产物是隔离库
  bootstrap/配置断言脚本与API smoke driver；应在隔离DB、认证、TLS callback就绪后实现，
  driver只通过HTTP触发业务，SQL仅作为独立回读断言，不伪造candidate/receipt。

结论：下一条真实链路缺口首先是隔离MySQL/schema与双方可达认证callback；不是再造
一个内存canary。此次只读，没有新付费、生产业务数据写入、迁移或部署。

### 本地隔离 MySQL 已按 Root 授权建立

2026-09-10，云SQL只读版本MYSQL_8_0；安装Homebrew mysql@8.0实际8.0.46。
未执行brew services start。Homebrew postinstall自动创建了默认/opt/homebrew/var/mysql
目录，但默认服务未启动；本次实际服务PID59385（exec79625）仅监听127.0.0.1:13306。
独立datadir `/tmp/cited-alpha-mysql-e2e/data/`，数据库research_api_smoke；SQL回读
VERSION/DATABASE/port/datadir与lsof均确认。没有连接或修改云端业务库。

配置/凭据为该目录my.cnf、client.cnf、root-client.cnf、database.json，目录700、文件600；
数据库用户research_smoke只获research_api_smoke库权限。root随机密码也未输出。
Root可读取database.json生成Backend/ML配置override，不能复制当前远端DB目标。
数据库目前为空，**schema初始化/迁移尚未执行**，故不代表DAO已验收。

停止命令（只作用于该隔离socket）：
`/opt/homebrew/opt/mysql@8.0/bin/mysqladmin --defaults-file=/tmp/cited-alpha-mysql-e2e/root-client.cnf shutdown`。
重启命令：`/opt/homebrew/opt/mysql@8.0/bin/mysqld --defaults-file=/tmp/cited-alpha-mysql-e2e/my.cnf`。
不删除数据目录，保留后续验收可恢复性。安装同时按Homebrew依赖要求升级了openssl、
ca-certificates、libevent并安装所需依赖；没有启动其它全局服务。
