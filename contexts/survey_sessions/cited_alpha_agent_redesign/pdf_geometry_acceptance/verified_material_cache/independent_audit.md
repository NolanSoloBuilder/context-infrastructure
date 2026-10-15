# Verified materials cache 独立审查

**最终生效结论见文末“兼容修订版最终复验”。历史段落中的严格六键直接拒绝已经撤回，不是当前协议。**

2026-09-11。初始设计审查，等待实现冻结后附实际复验。只读应用、不重启服务、不调用云/模型。

## 必须保留的边界

- 每请求ML先重算完整version身份hash、核对user/workspace；key不得只documentId/rawSHA。version中raw/provider/manifest全部receipt身份、scope及parser/verifier规则版本都进入身份。配置bucket/namespace授权不能因缓存跳过。
- Backend每请求saved_source_evidence→source-run→当前附件DAO权限仍执行。ML缓存不是授权证明；已撤附件、换owner或旧report version不因热缓存放行。
- miss必须走现有全材料SHA/manifest scope/真实normalizer replay比对后原子发布；任何失败、半下载、取消未知状态不能写入ready。不能缓存“看起来合法”的外部manifest或模型产物。
- immutable返回值：缓存对象不能被read_verified选中record、context、receipt引用污染。load_verified返回副本，_read_field也不能返回共享嵌套dict。特别rawReceipt/manifestReceipt、context列表、locator、image metadata及provider页面不能泄露可变引用。byte对象可共享。
- DocumentVersionStore.put后read用于证明**实际云对象存在且哈希正确**，不能走材料缓存假通过；freeze后预热若有，必须发生于存储读取证明完成后。读缓存复用旧真实内容不代表云对象此刻存在，需明确语义；GCS删除与用户撤权不能混用。
- 共享任务取消：asyncio.shield仅保护任务不被单一等待者取消，不自动解决底层store.session生命周期。当前readonly finally在请求结束关闭该service持有session；如果共享loader闭包借用首请求store/session，首等待者取消会关闭仍工作的线程，其他等待者失败。必须由缓存加载任务拥有store/session寿命，或者不让任务跨owner请求寿命并安全完成清理。不能只加shield和全局dict。
- asyncio.to_thread取消不等于线程停止；必须证明session.close在底层最后读取结束后。超时响应后继续后台load的选择需有界、可观察，不可无限留线程。
- shared cache跨event loop/worker/测试隔离：asyncio task/lock不能在不同loop复用；容量/TTL/淘汰/生命周期明确，禁止把每请求新实例内cache误称跨请求共享。
- 内存预算按真实对象占用而非仅receipt bytes粗略假定；同一原provider base64字符串、解析dict、normalizer副本、canonical比较bytes会放大。若预算是可说明近似也应留余量并同时限entry/inflight；不存无限版本。single-flight要防不同恶意版本并发加载放大。

## 实现后独立测试清单

1. 真实36页归档材料离线冷/热完全等价；两个service实例注入同cache，三对象只读取一次、adapter只重放一次；跨页与同页另一个字段值/ID/bbox不混。
2. user/workspace不符与修改version hash在loader前拒绝；修改任一receipt或parser/version规则不可命中；不同storage namespace不可跨用。
3. 热结果上修改context、locator、receipts、load_verified manifest，下一读保持原文与hash不变。
4. 首load失败不缓存，下次可重试；并发同key一load；超预算不缓存但正常返回完整验证结果；LRU淘汰后重新验证。
5. waiter A取消、B继续、allwaiters取消、底层线程尚阻塞四类生命周期：B不受影响，不在读取中关闭session；无悬空task异常；只在完成后可安全关闭。
6. put/read的独立存储测试确保即使cache已有材料，云内容缺失/损坏仍使put验证失败。
7. Backend热缓存前置授权测试保留；原PDFpagefallback与解析surface字段图像仍走原校验。

本文件后续追加结果，不将设计承诺冒充通过。

## 最终实现审查与独立复验

已协调实现agent冻结后执行。没有发现仍阻塞这次缓存合入的新增缺陷；下列结论有明确范围，不等于云端热读或完整报告验收。

实现是**单层共享已验证材料缓存**，不是先前双层设计的全部实现。只有_read_field走缓存；load_verified与DocumentVersionStore.put后的self.read保持fresh。每次cache前_validate_version_scope、三份store.validate_receipt当前bucket/路径/size检查。key=(VERIFIER_VERSION,namespace,完整version canonical JSON)。默认router注入共享cache+配置bucket；自定义store不隐式启用。TTL300s、LRU最多4、deep sys.getsizeof预算256MiB、单coldloader、最多16pendingkey；success-only发布。

缓存内部manifest不直接通过API暴露；_read_field最终deepcopy(result)，load_verified深拷贝fresh manifest。Backend当前附件/冻结版本/来源校验代码仍在每请求ML调用之前，没有缓存该DAO授权结论。

### 独立真实材料等价测试

脚本 `/tmp/cited-alpha-verified-cache-review/real_check.py`，结果real-result.json。真实36页Tesla原件及恢复provider，经实际adapter生成**明确离线重构版本/内存store**，再实际完整_load_verified_materials验证。不是伪造生产已封存版本，也没有provider提交。

- 两个service实例共享cache：冷读取三个完整对象各一次；热读新增对象读取0。
- 冷/热完整read_page_image响应相等；返回值context、locator、rawReceipt、pageRendition修改后，下一次读未被污染。
- 错user/workspace/versionhash在store读取前拒绝；换namespace重新读取；load_verified仍追加3次fresh读取。
- 原PDFgeometry继续page，surface仍retained_provider_page。
- 本地无网络冷1.744s、热0.059s，只是这个离线实验的CPU/内存路径耗时，不能宣称真实GCS请求将等于此数。
- 两个namespace条目合计262,730,849 retained bytes（每份约131MB）；证明真实Python材料明显大于57MB序列化大小，deep计量有价值。缓存限额不等于进程峰值内存限额：测试构造的原对象、冷replay暂态和响应副本另占内存；生产并发仍需观测。

### 取消/线程/session独立测试

`/tmp/cited-alpha-verified-cache-review/cancel_check.py` 使用实际VerifiedDocumentMaterialCache和DocumentVersionStore，加无socket的可控阻塞response线程。leader重复cancel两次后：请求未完成、第二key未进入loader、底层get计数仍1、session未关闭。释放真实线程后才结束response/close session、取消leader及同keyfollower、允许第二keyloader成功；被取消key不发布，无pending残留。cancel-result.json记录通过。

实现已按审查建议将Store.read线程task shield住；取消后循环等待实际worker结束（含重复取消）再propagate，因此cache冷加载slot和readonlyfinally session寿命不早释放。**行为选型是leader取消后followers一同fail-closed，不是继续完成其他waiters**；前面测试清单里的“B继续”只能指不同key排队工作，不能误称同keyfollower不受影响。follower单独取消仍不取消leader。

read线程有90s单调检查+30s网络I/Otimeout；90s检查发生在chunk边界，不能称精确90s硬总deadline。它限制持续流读取并避免取消立刻遗弃线程；socket/credential层等待仍受各自timeout影响。没有重启运行服务验证这一配置。

### 仓库focused测试

独立运行 `.venv/bin/python -m pytest -q tests/test_research_document_material_cache.py tests/test_research_document_versions.py`：21passed（1.66s）。含TTL/LRU/预算/并发、失败不缓存、重复取消阻塞线程、freshload、put实际读校验。实际Backend授权代码只读确认，未额外新建DAO/authfixture或网络请求。Root仍负责完整gate/部署后有界热读验收。

### Root集中修复后的最终再次复验

上述21focused结果属于首次冻结版本。Root随后要求还原FreshDocumentParser.parse无关整provider deepcopy，并严格化Store receipt六键schema/policy/mime/lower64hex/URIqueryfragment；实现agent完成后，本独立review再次运行三个脚本，均通过：

- receipt_check.py：10项直接真实DocumentVersionStore.validate_receipt负例全部拒绝（额外/缺键、错schema/policy/mime、query/fragment、外bucket、非法digest、boolsize）。这不依赖离线fixture自定义validator。
- cancel_check.py：更新为六键真实receipt后，实际阻塞线程重复取消/session/slot行为仍通过。
- real_check.py：真实36页完整verifier冷/热等价、跨scope/hash/namespace与返回污染仍通过；本轮离线cold1.930s/hot0.059s，非云性能承诺。

`/tmp/cited-alpha-verified-cache-review/final-source-hashes.json`固定本次四个实际源码SHA。各result.json已更新为最后一轮；无代码修改/云请求/服务操作。Root负责本轮完整gate，不能沿用上一轮focused数量当最新完整gate结果。

## 兼容修订版最终复验（最终生效，替代前述strict直接拒绝）

Root确认旧ML冷读取与正式Backend允许的receipt形状比严格六键宽。最新实现恢复旧validate_receipt桶/内容路径/size规则，新增cache_eligible_receipt只决定是否可缓存。非标准receipt走fresh全材料hash/replay，不直接扩大协议拒绝。任意hash不匹配仍由实际bytes校验拒绝；“冷shape兼容”绝不等于字节完整性放宽。

在实现agent明确下一次freeze后，本review再次执行：

- real_check.py已改用**继承真实DocumentVersionStore的validate_receipt/cache_eligible_receipt**，只替换无网络bytes读取。真实36页cold3对象、hot0额外下载、完整响应等价/防污染/scope/namespace均通过；本轮离线cold1.693s/hot0.057s，非云耗时。
- 对manifestReceipt加未来扩展key，以及缩成旧三字段objectUri/sha256/byteSize两类旧形状，重新计算离线versionhash，实际read_verified每类连续两次均正常读回相同原文，每类新增6次完整对象读取、cache entries不增加。证明“兼容fresh，不借热cache”。标准六键receipt仍热命中。
- receipt_check.py直接测真实cache eligibility：额外/缺键、schema/policy/mime差异、query/fragment、非法digest均不获cache资格且保留旧shape校验语义；外bucket和boolsize按原规则拒绝。合法标准receipt eligibility=true。共10项边界通过。
- cancel_check.py六键receipt重复取消/实际线程/session/slot检查继续通过。

real-result.json、receipt-result.json、cancel-result.json与final-source-hashes.json已更新为最终兼容版。没有应用修改、提交、服务/云/模型调用。本次没有重跑仓库完整gate；实现agent报告357passed/0skip由Root独立审核，不混入本review独立测试数量。
