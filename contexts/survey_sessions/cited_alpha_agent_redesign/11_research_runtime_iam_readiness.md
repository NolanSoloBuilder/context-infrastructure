# Research runtime IAM / 配置只读核查

2026-09-10，固定项目 cited-alpha-20260701。没有权限写入、部署或付费解析。

## 实际状态

- ML runner：`cited-alpha-ml-runner-00023-9xq`，SA
  `cited-alpha-ml-runner@cited-alpha-20260701.iam.gserviceaccount.com`。
- Backend runner：`cited-alpha-workspace-runner-00023-rvm`，SA
  `cited-alpha-workspace-runner@cited-alpha-20260701.iam.gserviceaccount.com`。
- 固定 OCR processor version `projects/829189946367/locations/us/processors/ba7872f1c0ed02be/processorVersions/pretrained-ocr-v2.1-2024-08-07`
  GET 实测 DEPLOYED；online adapter 固定 us endpoint 与本项目 ADC。
  Cloud Run region us-central1 与 Document AI multi-region us 不是冲突。
- 项目 IAM 没有任何 `roles/documentai.apiUser` binding；ML runner 已有
  `roles/serviceusage.serviceUsageConsumer`、Vertex user、CloudSQL client。
  未验证组织级继承/deny；本项目可见授权不足，不能把个人 owner canary 成功等同 runner 可用。
- ML runner 私有服务 invoker 和应用 allowlist 均已允许 Backend runner，反向现有链路已备。
- Backend runner 的 Cloud Run invoker 仅 workspace-dispatch；应用
  `WORKSPACE_RUNNER_ALLOWED_SERVICE_ACCOUNTS` 也仅 workspace-dispatch。
  ML callback 需要这两层都追加 ML runner，保留 dispatch。
- Backend public API 有 allUsers invoker，但应用内部鉴权仍不允许 ML；建议使用私有
  workspace-runner 作为 callback target，不依赖 public API。
- ML runner 的最新 secrets YAML 缺少 `mindspace.research-runtime`；typed defaults disabled，
  callback URL/audience 为空。线上镜像仍是旧 release，不能只补 settings 就声称新代码可用。
- 同一 ML secrets 的 document-ai project-id/location/processor-id/credentials-file 都为空，
  没有 gcs-bucket。新的 <=15页 online 路径不依赖旧 document-ai settings；16..100页
  batch 保留代码但线上缺配置，不能宣称长 PDF 实际已可执行。

## Root 最小应用项（本轮未执行）

1. Document AI：给 ML runner `documentai.processorVersions.processOnline` 自定义角色
   是新 online 最小权限；若保留现 batch，需 processors.processBatch、operation读取等。
   实用预定义最小角色 `roles/documentai.apiUser` 包含这些调用权限，不需 editor/admin。
   可采用项目 IAM binding；如 root 选择更细条件授权，先验证该权限资源条件可用。
2. 私有回调：给 ML runner 在 **cited-alpha-workspace-runner 服务级** 增加
   `roles/run.invoker`，并将该服务 env allowlist 改成
   `cited-alpha-workspace-dispatch@cited-alpha-20260701.iam.gserviceaccount.com,cited-alpha-ml-runner@cited-alpha-20260701.iam.gserviceaccount.com`。
   audience 保持 `https://cited-alpha-workspace-runner-rcbwgbgtcq-uc.a.run.app`。
3. ML settings 的 `mindspace.research-runtime`：

```yaml
enabled: true
node-binary: /usr/local/bin/node
module-root: /opt/pi/node_modules
entrypoint: /app/runtime/pi-research/main.mjs
backend-base-url: https://cited-alpha-workspace-runner-rcbwgbgtcq-uc.a.run.app
backend-audience: https://cited-alpha-workspace-runner-rcbwgbgtcq-uc.a.run.app
```

   在新镜像+消费者兼容后按 canary gate启用；不要先开Backend admission。
4. 长PDF batch 的 document-ai 配置另补本项目/us/processor ID和限定GCS input/output bucket。
   还须检查GCS写入/列举/读取及DocumentAI服务代理访问权限；当前未以付费batch验收，
   不给笼统“所有存储管理员”。旧batch endpoint调用processor默认版本而非固定version，
   因此目前不具备field geometry资格，显示page符合合同。

## 准确代码入口

- ML `research_agent/document_online_provider.py`：固定版本、ADC项目验证、一次post。
- ML `core/settings/research_runtime.py`：runtime开关/绝对路径/HTTPS callback校验。
- ML `research_agent/callback_client.py`：ADC OIDC token与固定目标URL，不接受请求URL。
- Backend `middleware/workspace_internal_service_auth.py`：env audience+email allowlist。
- ML `research_agent/document_version_service.py`：15页内 online，较长batch，manifest绑定。

原始secret内容未写文档/日志；只读取并展示上述非敏感配置字段。没有读取其它项目。

## 后续配置/发布权威核查（IAM 已由 Root 补齐）

Root 已补齐 DocumentAI apiUser 和 Backend runner 服务级 invoker 并回读。
本节不要求重复授权。2026-09-10 再次只读：ML secrets 最新仍是数字版本 **2**
（2026-07-02 创建），research-runtime缺失，DocumentAI目标仍为空，Vertex credentials-file
未配置；未输出任何密钥值。

### 配置权威及消费时点

`core/settings/constants.py` 选 ENV_MODE=prod 的 `/app/resources/prod.yaml`，然后读取
MINDSPACE_SECRETS_YAML_FILE 指向 `/secrets/prod.secrets.yaml`。
`yaml_loader.py` 深合并，后一个 YAML 覆盖同键；列表整体替换。
`load_app_settings()` 将合并payload作为init settings（优先级高于一般env settings）；
`get_mindspace_config()` lru_cache，首次读取后本进程不自动刷新。
research-runtime仅 PI_NODE_BINARY、PI_MODULE_ROOT 有显式env覆盖；enabled/callback
不能随意发明 RESEARCH_* env替代YAML。ADC属于凭据发现，不是这个YAML模型字段。

当前workflow `.github/workflows/docker-build-deploy.yml` 在main push/manual运行，
构建精确checkout镜像后先通过cloud_run_release.py发布ML API候选，再render/replace
`deploy/cloudrun/prod.workspace-runner.service.yaml`。Runner当前是直接replace，不等同
API的零流量候选流程。两个模板及bootstrap均把同一secret挂为 **latest**。
workflow不会创建secret版本，也不会自动合并新research键；仅在容器启动/第一次
settings读取时消费挂载配置。API与runner共用secret，新键会同时进入两者进程；
实际research执行还由runtime role、内部鉴权、Backend admission gate共同约束。

### 最小差异

- 在现有完整version2内容上只补上文 `mindspace.research-runtime`，保留其它配置。
  `enabled:true`只能与支持此合同的新镜像同时进入隔离runner；Backend admission继续关。
- OnlineOCR不需要再写document-ai目标：代码固定processorVersion/us/online/options。
  使用CloudRun绑定SA的ADC；不设置 GOOGLE_APPLICATION_CREDENTIALS、DOCUMENT_AI_CREDENTIALS_FILE
  或任何其它项目credentials-file。其本项目检查会fail closed。
- LongPDF batch另外需要下列非敏感键（bucket值需Root先选定并核对访问权限）：

```yaml
mindspace:
  document-ai:
    project-id: cited-alpha-20260701
    location: us
    processor-id: ba7872f1c0ed02be
    credentials-file: ""
    gcs-bucket: <本项目经核验的处理桶>
    gcs-input-prefix: document-ai/research/input
    gcs-output-prefix: document-ai/research/output
    batch-timeout-seconds: 1800
    batch-poll-interval-seconds: 5
    batch-chunk-page-limit: 50
    batch-max-chunk-concurrency: 1
```

`batch_options.py` 的prefix/timeout/chunk相关 DOCUMENT_AI_* env会覆盖YAML；bucket
则显式constructor > YAML > env。当前CloudRun无这些env，配置前需再次回读以免漂移。
大文档可能分成多个chunk，每个chunk一次提交不等于整份只有一次provider调用。
另外只读发现legacy `_session()` 使用 AuthorizedSession，它默认可能在401刷新后重放；
research单submit修复仅删除业务5次重试，还需关闭这一层auth重放才满足严格未知结果边界。
本轮未修改代码，Root已收到此问题。

### Secret切换与回滚顺序（操作说明，未执行）

1. Root在受限临时文件中读取version2并深合并上述白名单字段；不输出文件内容。
   本地用当前新代码做settings纯校验，不初始化网络client；记录非敏感变更摘要。
2. 新增secret版本N，不覆盖/disable旧2。**先把部署模板/渲染参数改为数字N**，包括
   API与runner需要各自的版本选择，不能继续依赖latest。此处是待实施发布配置差异。
3. 新revision绑定镜像digest+secret数字版本+SA+非敏感env。先runner隔离验证内部鉴权、
   runtime路径与只读健康；Backend admission仍关，root决定何时单用户canary。
4. 失败时停止新接纳，将流量/runner回到记录的旧image+**secret版本2**组合；回读revision
   的volume.key确为2。仅把流量切回仍挂latest的旧revision不能保证配置回滚：旧revision
   新实例可能读新secret。保留已有research Run的消费者兼容与恢复能力，不让旧worker认领。
5. 不销毁secretN或旧版本，不反复重新付费解析；未知capture intent保持恢复审计状态。

本轮没有secret写入、IAM写入、部署或付费调用。

### 授权的后续 auth 重放修复已完成

Root 后续授权修复后，research `document_single_submit.py` 对实际 AuthorizedSession
创建独立付费提交session，`max_refresh_attempts=0`、禁止redirect；不修改旧polling
session，不改变其它业务策略。真实Google AuthorizedSession + fake HTTP 401测试
确认只有一个POST、原session仍保留默认2次refresh配置。相关11项测试通过。
此代码改动不涉及secret/IAM/部署，仍未发起付费请求。

### 2026-09-11 部署账号元数据授权

当前ML发布workflow已经固定enabled数字Secret版本，替代前述latest部署目标。Root核对GitHub变量GCP_DEPLOY_SERVICE_ACCOUNT为github-ml-deployer@cited-alpha-20260701.iam.gserviceaccount.com。已在cited-alpha-ml-prod-secrets-yaml单Secret范围添加roles/secretmanager.viewer并独立回读，满足版本元数据查询的显式授权；不包含secretmanager.versions.access，没有新增读取内容权限。现有Secret version2不变。

本机impersonation验证在iam.serviceAccounts.getAccessToken处被拒绝，未扩大代入权限；不能宣称部署身份已实际调用成功。后续GitHub WIF发布的Freeze one enabled ML Secret version步骤提供最终调用证据。此次没有merge、部署、Secret值写入或生产admission变更。

### 完整PDF batch专用桶与权限（2026-09-11）

Root通过services identity create回读DocumentAI服务身份service-829189946367@gcp-sa-prod-dai-core.iam.gserviceaccount.com，uniqueId113119993046865481723。直接IAM describe被Google管理身份权限拒绝，不等于身份不存在；未追加TokenCreator。

在当前项目创建gs://cited-alpha-20260701-document-ai，location US、uniform_bucket_level_access=true、public_access_prevention=enforced并独立回读。ML runner与上述DocumentAI服务身份只增加此桶的objectCreator/objectViewer；无项目级Storage Admin或删除授权。正式不可变源快照仍使用原source-snapshots桶。长PDF配置gcs-bucket应采用此专用桶，input/output分别research/input与research/output；当前未写生产Secret或发布。

完整36页Tesla原始PDF batch canary启动session3042，/tmp/cited-alpha-docai-full36-01；代码实际使用DocumentAIBatchService+ResearchDocumentBatchOperationClient，50页chunk上限确认只有1chunk且字节完全不变，maxPaidSubmissions1、poll10秒/timeout1800秒。operation收到即持久化，未知提交结果不得盲目再发。个人ADC发起只证明该调用路径，不能替代CloudRun运行身份端到端验收。
