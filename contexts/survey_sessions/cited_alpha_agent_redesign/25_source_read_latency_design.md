# 单字段原文打开延迟与安全复用方案

2026-09-11，只读审查。不重发云请求、不创建服务、不改代码、不读取模型思考/签名。

## 结论与实际数据

当前一个字段点击走的是**整份材料完整下载、整份解析重放，再挑一个字段**。内容溯源严格，但重复工作过大。第一步应复用已经完成验证的不可变材料及字段索引，同时保留每次当前用户/附件/报告版本授权；不能去掉manifest/hash校验来换速度。

Root请求对应现存记录 `/tmp/cited-alpha-cross-source-business-03/actual-page-image-readback.json`：HTTP200，elapsedSeconds27.34，返回page5字段3,584，图片395719bytes、hashMatches=true，解析页field而原PDF仍page。这是该记录报告的耗时，不把先前“约1分钟等待”推算成另一精确计时；本次没有重放请求或自行计时网络。

同目录page-image-request.json中已冻结receipt大小：

| 对象 | bytes |
|---|---:|
| raw PDF | 11,267,189 |
| normalized manifest | 12,043,061 |
| provider JSON（含所有页面image base64） | 33,636,011 |
| 合计 | 56,946,261 |

因此该请求为了返回约396KB图，先完整读约56.95MB材料。这里provider实际33.64MB，不能把早期估计49MB当本次测量。没有分阶段trace，不能声称27.34秒中网络/CPU各占多少。先前离线真实8字段审查约3.8秒包含一次normalizer、8次图像/geometry检查，可说明本机CPU处理可运行，但不是本次网络请求准确剖析。

## 当前真实调用链

ML `mindspace/service/research_agent/document_version_store.py`：每个read根据配置bucket/content-addressed前缀、receipt大小读GCS alt=media，iter_content64KB，完整拼bytes后校验length/SHA。没有缓存；chunks列表+b''.join短时有双份bytes。requests timeout30是连接/读等待，不是整个响应30秒deadline；持续有数据的下载可更久。asyncio.to_thread避免阻塞事件循环，但任务取消不一定终止底层同步下载。

`document_version_service.py:_load_verified_materials`：

1. version canonical hash及user/workspace绑定。
2. await读完整raw；再读完整manifest并json.loads。
3. 验manifest source/parser/provider/execution。
4. await读完整provider并json.loads。
5. 用真实DocumentAILayoutParseAdapter重跑所有36页；model_dump完整normalizer结果；将replayed及manifest normalized分别canonical JSON编码比较。
6. `_read_field`遍历全字段找exactID，遍历各集合找page context。
7. derive_field_geometry再次解析raw PDF和算rawSHA，即使batch将回退page也做PDF元数据读取。
8. retained_page_rendition读单page image base64、完整Pillow verify/load并hash；read_verified即使只需字段元数据也做图像验证；read-page-image再base64编码返图。

`/tmp/cited-alpha-cross-run-7YGKhq/ml_readonly_app.py`：每请求factory创建新ReadOnlyDocumentService、DocumentVersionStore、ReadOnlySession/AuthorizedSession，finally关闭session。没有任何跨请求材料复用；临时只读组合固定snapshotbucket与ADCquota/read_onlyscope，不能称连接到错项目。此模式能避免泄露会话，但凭证刷新、连接复用也可能反复产生开销；本次无分阶段记录可量化。

Backend `ResearchDocumentSourceReader` 每请求实际重新检查附件+冻结version及quote/context；source元数据GET与source-page图片GET分别触发ML读，再开另一个字段又完整重复。图片端点采用一次read-page-image完成字段与图片核验，去掉了Backend二次Pillow解码，但仍有上游全材料重复。原PDF source-file还独立下载原PDF作校验，属于另一视图的数据成本。

## 最小长期合理方案：两层缓存，授权在外

### 第一层：已校验对象bytes缓存

放在DocumentVersionStore依赖层，共享给同进程的service实例，不能仅在每请求新建实例内放字典。

- key=(配置storage namespace/bucket, exact object key, receipt sha256, byteSize, mimeType, object schema/storage policy)。读取前每次仍执行receipt结构、配置bucket/前缀/大小检查，拒绝客户端任意URL。不能只用sha或documentId直接信任。
- miss执行当前完整下载与SHA校验后原子发布；只缓存成功完整bytes。超时/取消/不匹配不发布半成品；同key并发single-flight，限制总并发与内存，避免两个请求各下载57MB。
- bytes不可变；只读共享。RAM LRU按**实际bytes**而非对象数量限额；大provider/manifest可优先受限本地内容寻址磁盘缓存，写临时文件、hash核验、原子rename，私有权限。磁盘命中仍校验本地length/hash（或文件句柄持有并严格定义完整性机制），不能把存在路径当校验成功。
- 不缓存授权结论；每请求当前owner/attachment/source-run/report-version仍重验。合法旧不可变snapshot在云被覆盖后本地已验证bytes仍等于冻结receipt：要明确产品语义是按冻结内容读，不是证明对象此刻仍在云。若删除/撤销需要立即使缓存失效，靠业务访问撤销门，而不是依赖偶然GCS404；TTL不是授权策略。
- 存储credential/session不与用户或对象授权缓存混为一体；共享固定只读session需独立考虑thread safety/lifecycle，不能无意共享运行token。

这层先降低重复网络，仍每次JSON parse/replay，作为低风险过渡可实施，但单独缓存56MB blobs不会彻底解决CPU/峰值内存。

### 第二层：已验证版本读取索引

在DocumentVersionService构造一个可注入、进程共享、受限 `VerifiedDocumentMaterialCache`，key=(完整documentVersionId, raw/provider/manifest receipts, verifier/parser实现版本)。校验version scope/hash在cache查找前；backend当前授权也在请求链每次完成。version包含user/workspace/document/file；不能跨owner拿已验证上下文索引。

首次miss仍原样完成_load_verified_materials：三个原件SHA、scope、providerexecution、真实adapter replay和canonical比较。完成后缓存不可变VerifiedReadView：

- exact(kind,id)→唯一record；检测重复ID则保留ambiguous状态/拒绝，不能dict覆盖。
- pageNumber→原有context集合（逐字相同顺序和完整字段，不因缓存压缩截断）。
- pageNumber→已验证provider image引用、image metadata，及从原PDF得到的固定viewBox/Rotate/UserUnit。
- 可选(pageNumber,imageSha,decoderVersion)→已解码校验通过的image bytes+metadata；同page不同field只重新取各自polygon，不让一个字段bbox污染同页其他field。单张图片bytes只存一份，不给每个字段都复制396KB。

缓存仅发布验证成功结果且不暴露可变dict；给调用方只复制选中record/context/response，禁止deepcopy整个57MB材料图。失败不污染旧正确项；key含实现规则版本，代码升级/normalizer规则变化不复用旧“已核验”标记。淘汰后重新完整验证是安全回退。

应把旧`_load_verified_materials`保持为统一冷路径，新增cache不另写一套“快速弱验证”。也不能省manifest replay只信某个已写入mutable解析表。缓存字段view本身不能被模型tool返回值或外部JSON任意灌入。

## 冷读后续优化：不可变分页面材料索引

缓存只能优化热读。生产首开若仍下载57MB，应在统一parse artifact阶段生成带哈希的root manifest索引：原件receipt、完整provider原输出receipt继续保留，每页image对象receipt、页内normalized字段对象receipt、field→page位置索引、normalizer/derivation版本以及生成校验证据。首次创建时完成全provider重放；读单field验证root和指定page/field分片，后台审计仍可重放全原输出。

这是新的不可变artifact/manifest协议，不能在当前旧manifest上偷改含义。旧版本用完整验证+cache；新版本可渐进页级读取。不能单独将JSON拆开后默认其证明原provider等价：必须有可信构建/哈希根、对象完整性与derived版本规则。原PDF下载仍按原件receipt读取，解析page-image不强制每次下载整个PDF只是为了重取page box；page元数据从已验证新artifact绑定获得。

短期不建议先并行下载三个对象：这只能压延迟、放大并发带宽与内存，未解决重复IO；先有single-flight、缓存预算、阶段计时，再决定冷读并行。

## 验收和可观测性

不记录token/quote大正文/私有签名。记录受限对象类型、bytes、phase耗时、cache hit/miss/singleflight、normalizer版本、readiness与错误类别。

- 冷读：三个对象下载计数一次，完整SHA/replay照旧；热同field/同page另一field不再下载或重放，返回quote/context/locator/geometry与冷路径canonical等价。
- 重复数值跨字段各bbox准确；同scope换DocumentVersion不能误命中；变receipt/manifest/rawhash、错误parser版本、同ID重复都拒绝。
- 授权撤销/换user/换artifact/citation每次即时拒绝，即使对象/版本缓存热；禁止通过单独图片cacheURL绕过。
- 同时点击多个字段同key只有一个冷加载；等待者取消不误删其他等待者结果；shareddownload可取消策略明确，failed/partial不缓存。
- LRU淘汰/进程重启/磁盘损坏/规则版本升级均回冷路径，不返回陈旧或不完整内容；峰值内存和CPU在并发下有界。
- 分别测元数据GET→图片GET、同页多field和跨页三种场景，显示首开/热开p50/p95及字节量。本次只确认27.34s一条真实记录，不能预先声称缓存后<1秒。

此优化不增加模型、不改事实审查、不改变原PDF与解析页面surface区分。下一步最小代码范围是store缓存依赖、service verified-readview缓存/索引及离线等价/授权边界测试；临时readonlyapp只负责注入共享实例，不应承载业务缓存实现。

## 当前实施（2026-09-11）

ML66ad4b2实现一层共享的完整验证材料cache，避免叠加两份重合存储；冷路径仍完整验证，当前授权每请求保留。256MiB按递归Python对象大小计量，TTL300s/LRU/单冷加载/取消生命周期有界，旧receipt不合缓存资格仍fresh读取。Store.put发布验证不使用缓存，load_verified亦保持fresh。完整离线357项通过，独立真实材料与取消/兼容复验通过，见[独立审查](pdf_geometry_acceptance/verified_material_cache/independent_audit.md)。真实GCS冷/热耗时验收另行回读。
