# Run04 checkpoint HTTP客户端生命周期审查

结论：**确实存在逐次load/save新建ADC credentials/AuthorizedSession并关闭连接池的重复工作；但现有span不足以证明每次都发生token刷新，也不能把约3秒全部归因于认证。** 最小改进应复用有界、独占借用的持久HTTP client，而不是缓存checkpoint内容或授权结果。仅将Store变成单例不会生效，因为默认_session每次操作仍创建session。

本次只读已有性能日志、应用代码及已安装Google Auth实现，没有新增网络benchmark、云请求、模型或写入操作；Run04与worker不变。

## 实际span（固定读取快照）

源 `/tmp/cited-alpha-cross-source-business-04/performance-spans.jsonl`，截至本次快照最后startedAt **06:07:57.202011 UTC**，541条完整span。原日志仍可能继续追加，以下不是Run终态总计。计算结果 `/tmp/cited-alpha-run04-checkpoint-client-stats.json`。

|kind|count|median s|p95 s|sum s|最前10/最后10 median s|
|---|---:|---:|---:|---:|---:|
|checkpoint_load|181|3.8300|4.8015|682.6996|2.6462 / 4.5709|
|checkpoint_save|181|3.0627|5.6143|609.8352|2.4460 / 5.6406|
|callback_checkpoint|179|6.9835|10.6957|1288.3400|4.9516 / 10.5569|

179个callback均在时间区间内包含恰好1个load+1个save。callback减两子span并集的残差median约0.0212s。checkpoint load/save并集1292.5348s，所有span时间并集1299.1696s。**不能把682.7+609.8+1288.3相加作耗时**；callback含子span，重复相加会近乎翻倍。区间以startedAt+elapsedSeconds计算，存在不同计时源的微小舍入误差，未当分布式trace精确父子ID使用。

已去掉重复load这一事实与当前每callback两个子span吻合。后段越来越慢也与checkpoint从约KB增到MB的方向相符，但这些统计没有分解HTTP/序列化/认证，不能建立单一因果。

## 真实生命周期

Backend `service/research_runtime/callback_service.py`在dispatch中调用store_factory；当前临时backend_app注入`lambda: AuditedCheckpointStore(bucket=...)`，没有session。AuditedCheckpointStore只包围super.load/save计时，并未改变客户端。

Backend `research_runtime/checkpoint_store.py`：

- `__init__`只存bucket与可选_injected_session。
- `_session()`每次load或save执行`await to_thread(_authorized_session)`；后者调用google.auth.default(devstorage.read_write)并构造新AuthorizedSession。
- 同一Store先load再save仍用两个独立session；默认finally关闭session。每callback的新Store不是唯一原因，逐操作_session工厂才是直接原因。
- load:校验pointer/scope→session内metadata GET(timeout15)→media GET(timeout30、bounded stream)→关闭session→SHA/canonical/contents/candidate/sequence校验。
- save:scope/payload/canonical/hash→新session→带ifGenerationMatch=0的POST(timeout30)；412时同session再metadata+media校验existing bytes→关闭session→返回pointer。
- 因此正常无412 callback名义上至少2个GET+1个POST，外加可能认证请求；日志没有HTTP请求计数，不把该推导说成实际抓包结果。

已安装Google Auth的Cloud SDK路径每次通过load_credentials_from_file创建credentials；AuthorizedSession.request调用credentials.before_request，并可在认证失败后refresh/replay。由此支持“失去上一个credentials/session缓存”的机制判断；仍未观测本Run每次credentials来源、valid状态、refresh调用数、DNS/TLS时间，不能断言362次操作等于362次token刷新。Cloud Run metadata身份路径与本地个人ADC的认证延迟不同。

关于“SecSnapshotWriter”：当前Backend checkpoint并不调用ML的SEC writer；相关ML实现实际名为`_GcsSecEdgarSnapshotStore`，持有session，`SecEdgarSnapshotCaptureService.capture`默认每次capture调用_default_gcs_store创建新ADC/session。它没有出现在本次checkpoint span链上，不能拿其行为解释这些span。Backend SEC reader另用workspace_source_snapshot_object_service._authorized_gcs_session(read_only)；与checkpoint读写scope不同，不宜不分权限地共用同一个session。

## 最小持久client候选

采用一个进程级`CheckpointHttpClientPool`基础设施组件（建议名，不是已经实现），Store保留轻量、无scope状态：

1. 应用lifespan启动时创建pool（或首借惰性创建）；每slot持有独立AuthorizedSession及其credentials。初始2slot、有限等待队列、明确等待timeout；一slot只服务一个完整load/save操作。先从1slot受限灰度测，再按并发callback需求调到2；不设无界pool。
2. 一次借用覆盖整个同步HTTP操作：load的metadata+media，save的POST以及412完整readback。同slot可绑定单线程executor，让session构造/request/close都在线程内串行执行。不把requests Session声明为任意线程并发安全，也不让多个slots共享可变credentials刷新状态。
3. token在同slot credentials内按有效期正常复用，Google Auth继续处理到期；不手工保存bearer、不越过audience/scope、不把Authorization写到全局日志。多个slot各自最多有一份token缓存，是否值得共享credentials需另测和同步，不是本次必要优化。
4. pool只复用传输资源，不复用scope、pointer、payload、candidateHash、source authorization。每次仍运行scope_hash、完整URI匹配、metadata/size/SHA/canonical/版本/sequence校验；POST precondition和412实际bytes回读不能删除。Store实例可以继续按callback创建，只注入同pool即可。
5. 取消要保持**实际底层线程结束后**才能归还slot。现在直接await to_thread被取消时线程可能仍工作，随后_session finally关闭session；改成跟踪worker future、shield等待，包括反复cancel，再传播取消。绝不能“async任务结束就放回池”，否则下一请求可能与未完成上传/下载共用session，并越过真实连接上限。
6. 同步操作设置明确整体deadline+各次I/O timeout、stream bytes上限；截止时间应计入metadata/POST/412分支及认证，不声称requests timeout30代表操作总长30秒。若底层不可即时中止，取消请求延迟到有界worker退出；quarantine不可复用的slot直到真实结束。仅限制队列长度不解决悬挂线程资源。
7. lifespan关闭先停止新借用、等待有界active操作结束，再逐slot关闭session和executor；不要在仍有线程写入时关闭session。异常失败slot可丢弃并下次重建，但不自动重发unknown POST。既有注入fake session语义保留，调用者负责其生命周期。

这比“所有Store持有同一个未经同步的全局AuthorizedSession”更明确；也比给每个scope建session缓存更小，不累积用户级连接/授权状态。pool无需改变任何数据库CAS或checkpoint格式。

## 验证证据与观测建议

先离线、后Root授权的一次小规模真实对照，不能现在为诊断反复写云：

- 传输构造计数：多次load/save只创建≤slots个session；成功/失败/412返回值与旧实现一致，跨scope/伪造pointer仍拒绝。
- 阻塞真实线程fixture：slot1请求双cancel，slot2/后续借用不能越过上限；释放线程前无session.close/reuse；lifespan shutdown也等待真实完成。读失败/上传unknown不重试。
- 非敏感细分span：pool等待、credential/session构造、before_request刷新计数及elapsed（只计数/时间，不记录token）、metadata GET、media GET、POST、bytes、canonical验证耗时。避免嵌套相加；记录父span或明确区间关系。
- 小规模对照固定相同checkpoint大小和同scope、有界合法读写次数；比较冷/暖session。成功标准是观测连接/refresh次数减少及总时延改善，不预设“3秒会全部消失”。Checkpoint逐渐变大仍会增加下载、上传、canonical和模型上下文成本，client复用不能消除这些成本。

本轮未实施pool、未改变worker或重新读取GCS。支持连接生命周期重复的代码证据明确；token刷新占比、生产收益及负载容量尚未验证。
