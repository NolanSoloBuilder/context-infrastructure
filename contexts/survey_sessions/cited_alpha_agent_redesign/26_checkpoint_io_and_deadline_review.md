# Business03 截止失败与宿主耗时只读审查

## 范围与结论

只读本地 business03 SDK 审计、checkpoint146 的角色/工具调用/工具结果/预算和当前对应源码。未访问模型私有思考或签名内容；未发网络、模型请求或修改 Run。绑定档案记录 Backend `10b767c`、ML `8200d05`；execution_service、callback_service、checkpoint_store 当前文件与这些运行 commit 的哈希一致。

终态是 deadline_exceeded，无 reportVersion、无 checkedCandidate，仅初始化版本1，不能称成功。35次 SDK 都是 response/STOP，没有 MAX_TOKENS、SDK异常或模型调用预算耗尽。最后模型实际选择 calculate，未生成 submit_report。最终checkpoint已有36个completed effects、33项证据、3项计算，但最后一个计算尚未成为 Pi toolResult message。持久副作用已完成不等于用户报告已交付。

## 可测量时间

Run 预算1800秒，原deadline 05:21:01 UTC。SDK首调04:52:09.547，末调05:19:59.976，末响应05:20:07.885。第一次调用前已用约68.5秒（从deadline减1800秒推导，包含准备/冻结恢复/初始持久化/首次pacing；无法拆分）。

35次SDK累计 233.71 秒，中位 5.68 秒；34个“前一响应完成→后一SDK开始”间隔累计 1444.62 秒，中位 41.83 秒，范围 26.00–65.77 秒。间隔约占首SDK开始至末SDK响应时间86%，不是模型生成本身的耗时。

| 调用序号 | SDK开始UTC | SDK秒数 | 至下一SDK间隔秒 |
|---|---|---|---|
| 1 | 04:52:09 | 4.01 | 65.77 |
| 10 | 04:58:04 | 7.76 | 36.83 |
| 20 | 05:05:45 | 5.95 | 54.02 |
| 30 | 05:14:40 | 8.27 | 45.05 |
| 33 | 05:17:33 | 15.50 | 62.89 |
| 34 | 05:18:51 | 8.34 | 59.74 |
| 35 | 05:19:59 | 7.91 | — |

checkpoint146本地pretty JSON为1,729,319字节，独立GCS pointer canonical byteSize为1,401,063，后者才是上传字节。以下抽样均为本地pretty JSON大小，非上传字节：checkpoint23为62,628字节，93为569,391字节，130为1,221,530字节；完整状态写入负载随研究增长。仅留存9个抽样checkpoint文件，不能把本地mtime当远端写入耗时或假称有146条网络耗时trace。

35条已落Pi工具结果的“assistant工具调用消息timestamp→toolResult timestamp”中位31.03秒。按工具：read_document14次中位27.67秒，read_filing9次32.22秒，cite_filing_fields3次32.62秒，calculate2次48.67秒。这个区间包含assistant checkpoint、tool intent checkpoint、实际工具及completed checkpoint，绝不能全部归因工具实现或GCS。

## 为什么每回合接近一分钟

1. execution_service.guarded_model 在SDK前同步persist；assistant message_end同步persist；工具执行前intent persist、完成后persist。只有严格可重建的toolResult message_end可以省略。普通单工具回合至少4次串行checkpoint，不是只写工具结果一次。
2. **真实重复读取**：Backend ResearchCallbackService.dispatch 对所有含authorizedDocuments回调先 DAO pointer读取→store.load读取整包，只为取得documentCaptures；接着 checkpoint操作调用 ResearchCheckpointService.save_progress→load 再读同pointer及整包→store.save写新包→DAO CAS。每个普通checkpoint是2次完整load（各metadata GET+media GET，共4 GET）+1次POST，而非1读1写。callback层还为纯checkpoint构建未使用的source/check authority/calculator。此前service内部重复load已经去掉，但上层document授权分支又造成重复。
3. 默认 ResearchCheckpointStore 每次load/save各新建 google.auth.default + AuthorizedSession，结束close。含文档普通回合4个checkpoint在代码路径上约8 load（16 GET）+4 POST、12个短生命周期session（不含工具取原件/计算验真）。跨境网络、认证刷新/连接建立与包增长有合理成本，但没有逐spantrace，不给每项编造毫秒贡献。
4. canary model_audit pacing是相邻入口**最小20秒间隔**，不是无条件每次sleep20秒。观察SDK间隔均已超过20秒；通常存储/工具耗时足以耗尽pacing窗，因此不可从总时间直接减去35×20秒。第一次可能有冷启动20秒等待，没有wait日志不能精确量化。
5. read_research_method等轻工具也需23.84秒的包含持久化区间，支持“宿主固定开销显著”的判断，但尚非GCS延迟的直接测量。

## 最后一分钟与预算一致性

最后SDK开始离绝对截止约61秒，7.91秒后响应选择第3次growth_rate计算，未submit。checkpoint146最后effect completed，预算回执 remainingSeconds=18，但对应工具结果尚未进入messages；计算完成后还必须await completed checkpoint，再回Pi，才可能下一模型。余下18秒不足时仍在存储/消息返回路径耗尽，是目前证据最吻合的解释；缺少callback开始结束trace，不能定位超时发生于具体HTTP还是CAS。

ML ExecutionClock与Pi timeout共享本次单调deadline。Backend executor在真正发ML前将durationSeconds裁剪为原Run剩余整数秒，外层仍有原deadline timeout。**HTTP router未向ExecutionClock传absolute_deadline**，故真实回执timeBudgetScope=host_attempt_allowance；它从ML开始重新计剩余allowance，传输/初始化会产生微小相对漂移，Backend最终截断仍权威。不是重新获得完整1800秒，但也不能说ML直接持有原UTC截止。

工具预算反馈是在completed persist之前生成，SDK预算反馈在model预算persist之后生成。前者被持久化网络等待变旧；例如倒数几次工具的剩余230/154/85秒展示时已消耗额外存储时间。模型收到较大剩余调用数（最后仍29 model/92 tool）与很少wall time共存是合法的多约束预算，不代表还能完成这些调用。可明确报告“剩余时间按反馈生成时刻，不含随后持久化”；更合理是传原绝对deadline并在下一模型入口生成最新预算。

## 多工具是否能减少回合

支持同一assistant含多个toolCall：首回合search_documents + find_filings已经实际执行，35个model对应36个tools。本Run后续基本一回合一工具。Pi runner明确toolExecution='sequential'，同轮多个工具可以减少模型回合与assistant/model预算写入，但工具intent/completed持久化仍逐个执行。cite_filing_fields已有批量，实际3次使用，属于成功复用而非缺能力。

不能直接改parallel：共享effects/catalog/expectedSequence、单指针CAS和模型后续依赖必须保持有序；并发checkpoint可能互相冲突或丢状态。优先明确通用工具说明允许将互不依赖的读取/已知字段计算放在同一模型回合；需要并行时再为只读工作引入有界执行和单写入者，不复制运行调度器。不得把固定“财报先收入再现金流”等流程写死。

## 最小优先改进及验证

P0：先给callback/store增加结构化性能span：run/sequence/operation、旧新byteSize、DAO load/CAS、GCS GET/POST、session建立、source verify、SDK前pacing实际wait；不记录消息正文、token或签名。把实测与模型时间分离。

P1：纯checkpoint回调无需构造document source reader和reviewer，保留run/lease/sequence验证，让save_progress单次load负责保留host captures。check/calculation需要源验真时才读取captured版本。或在同一次请求中传已验证旧snapshot给service，保留最终DAO CAS；不做跨请求状态缓存，不让ML覆盖host字段。最小路径从每checkpoint2load+1POST降1load+1POST（HTTP 4GET降2GET），每单工具回合省4个load即8个GET，原件/字段定位/unknown effects语义不变。

P1：在已授权生命周期内复用认证session/连接池（同bucket、同凭据边界），保持请求大小限制、哈希验真及immutable generation precondition；不得放宽付费调用重试。

P1：将绝对Run deadline作为受信HTTP字段贯穿Backend/ML；预算提示同一权威时钟，工具持久化后重新生成实时提示或提供明确asOf。原持久effect的回执必须保持可重建，不为刷新提示修改已存副作用。

P2：利用模型已有多tool能力和批引用减少无必要回合。只有实测和断点测试证明安全才继续合并checkpoint；不删除assistant持久化、intent或completed，尤其submit authority不能被延迟得失去防重复保障。

验收：同一代表性研究范围不缩水，记录完整报告通过独立check并保存version；比较SDK/IO/walltime分布。离线需覆盖含PDF/无PDF、并发CAS/租约失效、completed工具恢复不重做、submit意图清空旧candidate、截止发生于GET/POST/计算、连接错误与未知效果。宿主吞吐优化通过后再付费真实研究，不能以原文读取通过替代报告交付。

## 文件定位

ML：service/research_agent/execution_service.py（persist/event/guarded_model/durable_tool）、execution_clock.py、router/v1/research_execution_router.py、runtime/pi-research/runner.mjs。
Backend：service/research_runtime/callback_service.py、checkpoint_service.py、checkpoint_store.py、executor.py。
临时实际治理：/tmp/cited-alpha-cross-run-7YGKhq/model_audit.py。
