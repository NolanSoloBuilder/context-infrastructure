# 真实业务 Run 检索上下文与持久化成本审查

2026-09-11；只读，不调用模型、不触碰运行中 session 19411。固定观察样本为 independent-checkpoints/52.json，而非随时变化的最新 Run。ML 绑定 58dc18e8、Backend ca114683，financial-report-agent-plan-writer 分支；主 Agent 同时进行的 checkpoint 去重变动另标说明。

## 结论

优先消除每次 checkpoint 的重复对象读取，再改善精读选择和模型可见历史；不要把模型响应慢、details 重复与对象存储慢混为一谈。存档的重复确实可量化，但现有日志不能把约一分钟的间隔全部归因于 GCS。原文存储、精确字段 locator、付费操作前 intent 和恢复必要数据均应保留。

## 固定样本证据

- 样本 `/tmp/cited-alpha-business-run-01/independent-checkpoints/52.json`：canonical JSON 515,252 bytes，本地 pretty JSON 675,443 bytes。52 次序号，11 次模型调用、10 次工具调用、21 条消息。
- canonical progress 分量：messages 334,996 bytes；pendingEffects 179,095 bytes；rawCatalog 和 calculations 均空（各 2 bytes）。尚无 checked candidate。
- 10 条工具消息的首个文本 JSON 与 details 全部相等。details 合计 146,239 bytes（占完整包 28.4%）；首个文本字符串本身共 156,171 bytes。差异来自 JSON 序列化空格。10 个 completed pendingEffects 又保存一份 toolResult.content，用于未知中断后的恢复，不是全部可以随意丢弃的冗余。
- Vertex 实际请求只使用 toolResult.content 和 isError，不使用 details。因此删 details 可以减包，不能直接宣称减半模型输入。见 `mindspace/service/research_agent/vertex_messages.py:58-69`；结果构造见 `sec_tools.py:28`。
- 10 次工具中 8 次 read_filing，每次返回 12 个 blocks，共 96 个返回条目（非去重证据数）。表 23 已读取 offset 0/12/24，表 26 读取 0/12；还搜索了运营报表、现金流报表及 Free cash flow。8 次均 has_more=true，但 rawCatalog=0；这些只读结果没有注册为可交付证据。
- broad 查询 total_matches 分别可达 567、613、233。BM25 返回任一词项/邻近标题相关的候选，不代表这些全是回答必需证据。不能把 has_more 理解为必须读完。

## 时间与 I/O：已知和未知

`/tmp/cited-alpha-business-run-01/sdk-attempts.json` 前 11 次 SDK 调用耗时合计 43.520 秒，单次 2.501–6.787 秒；相邻调用开始间隔 37.720–76.719 秒，中位 56.718 秒。从首次开始到第 11 次结束约 568.729 秒，SDK 调用本身约占 7.7%。输入量从 1,549 增至第 10 次 64,089、第 11 次 67,931；此处只记录计数量，不记录模型内部内容。

canary `model_audit.py:10,46-50` 另设首次等待及最小 20 秒调用间隔。SDK 计时在等待之后，不能把等待归因于 SDK；各实际间隔远大于 20 秒也不能说明每轮都另加 20 秒，因为实现是最小间隔而非固定 sleep。

当前 backend.log 只有一行、ml.log 为空，无每次 checkpoint HTTP/GCS 阶段耗时。故目前只能确认串行 I/O 数，不能可信给出每次上传耗时或百分比。后续应记录 scope/sequence/bytes 与 DB load、对象 metadata GET、media GET、upload、CAS 各阶段耗时；不记录消息正文或凭据。

### 每个工具轮的 checkpoint 放大

`execution_service.py:98-122,150-177`：模型调用预算扣减前持久化，assistant message_end 持久化，tool intent 持久化，tool completed 持久化，tool message_end 持久化。典型一模型一工具约 5 次全量快照；52 与 10 个完整工具轮加后续状态一致。每次 deepcopy 全 history，历史增长会放大所有后续写入。

Backend `checkpoint_service.py` 原 save_progress 先 load，然后 _persist(document_captures=None) 再 load；`checkpoint_store.py:129-175` 每次 load 是 metadata GET + 完整 media GET，save 通常单次 POST（412 幂等回读是额外分支）。SEC 无附件时，原每次 checkpoint 正常路径 4 GET + 1 POST；主 Agent 请求内复用 previous.documentCaptures 的改法降为 2 GET + 1 POST，每轮约省 10 GET、5 次旧包下载和5次 DAO pointer load。若旧包约515KB，则每轮仅去掉的旧包读取约2.6MB，实际早期包更小，不作为整 Run 实测流量。

Document callback 还会为 frozen captures 额外 load 一次，但此次 SEC-only 不走该分支。见 callback_service.py:46-66。不要把此项算入当前 Run。

## 优先级与安全约束

1. **P0 请求内复用已验真 checkpoint**：支持主 Agent 正在实施的 save_progress/check_draft 参数透传。已验真 payload 与 sequence 同源，仍由 SQL 最终 CAS、lease、scope 拒绝竞争写；check_draft 跨独立审查后也必须用 invalidated.sequence 做 CAS。禁止跨请求缓存“最新”状态。保持 host-owned captures/candidate 不能被 ML 覆盖。该项不改变恢复/原文能力，收益最确定。
2. **P1 精读由任务缺口驱动，避免整表遍历**：在已识别表号后组合 table_index + 指标 query，缩小 limit；定位需要的行和期间即调用 cite_filing_field，再按缺口读下一项。遇到 has_more 不默认继续翻页。保留单位、期间、真实表头、例外说明和原始物理坐标。当前 read_view 已有单响应 context_ref 去重和约30KB预算（sec_read_view.py:51-84），不能把该能力当作尚未实现；更多收益在多轮历史边界，而非再做同一个局部去重。
3. **P1 去除持久 transcript 的 details 副本**：模型请求不依赖它；确认 Pi UI/恢复消费者后，在归档投影中剔除重复 details 或换不可变结果引用。固定样本上限约省28.4%，不触动原始 SEC 快照，也不能声称模型输入下降同幅度。
4. **P1 completed effect 压缩需原子确认**：只在对应完整 toolResult 消息已进入同一 durable checkpoint 后，允许把 effect 内容改为已完成标记+消息ID/内容hash/不可变结果引用。intent、模型预算扣减和“已执行但消息未落盘”的结果必须保持恢复能力；不能为了少写而直接删除这些 checkpoint。建议先写中断点测试再考虑将 completed 与 message_end 合并。
5. **P2 模型上下文投影独立于原始存档**：完整工具返回继续归档；模型只保留最近必需读结果及已选择字段/来源句柄。旧精读可以换有界检索摘要和可重新读的 source handle，但不能删改待完成的调用/响应配对、签名绑定部分或让模型无来源地使用摘要数字。需要版本化 context projection，并测试恢复后的同字段再读与引用注册，不采用任意截尾。
6. **P2 checkpoint 增量化/不可变结果对象**：在已有单一 SQL sequence 指针下复用内容寻址结果，保留周期快照+有界日志；不要另造并行状态真源。先完成前3项量测，再决定是否值得引入新恢复格式。

## 验收门槛

- 同一确定性 transcript 重放，预算不回退、pending intent 不被重复执行；在工具完成前后、消息落盘前后、review 后 CAS 竞争各中断点可恢复。
- 对每次 checkpoint 统计真实对象请求数与延迟；秒数改善须重新实测，不能拿请求数直接换算。
- 原始归档 hash 不变，已选 evidence 的 locator、unit、period、sourceIntegrity、citation resolve 不变；报告仍须独立审查。
- 比较同一研究目标完成所需工具数、模型输入量、墙钟时间与最终报告覆盖率；不能以少翻几页或提前输出无引用报告作为优化成功。

本审查未读取或输出模型内部内容、签名、凭据；未改应用代码、未新增模型调用，也未改变 live canary 的 pacing/预算。


## Run02实际模型输入审查（2026-09-11）

# Run02 checkpoint131：模型上下文成本审查

只读固定checkpoint131和SDK审计前33次；不输出模型内部内容、签名或消息正文，不调用模型/网络，不修改代码。统计为UTF-8字节，不能直接当作模型计费单位。

## 实测

累计33 model、32 tool。前33次SDK输入量从1,655增长至164,898；第24次106,168，第25次128,390，第26次139,068，第27次160,134。下表为所有工具text块（含host预算反馈）的累计字节：

| 工具 | 回执数 | text字节 |
|---|---:|---:|
| find_filings | 1 | 711 |
| read_research_method | 1 | 943 |
| read_filing | 22 | 299,829 |
| cite_filing_fields | 2 | 89,842 |
| cite_filing_text | 6 | 8,894 |
| 合计 | 32 | 400,219 |

read_filing占74.9%，两次批量引用占22.4%。因此批量引用重复不是全部膨胀原因，但单次回执很大，属于可无损去重的明确切口。

### 两个16字段批次

| 批次 | items数 | 首text字节 | items canonical字节 | table_context字节 |
|---|---:|---:|---:|---:|
| 1 | 16 | 45,434 | 43,969 | 24,064 |
| 2 | 16 | 43,804 | 42,431 | 24,112 |

两个批次共32个table_context，只有2个不同值；出现次数28和4，累计48,176字节，而每个唯一值各保留一次仅3,020字节。可去掉的纯重复值45,156字节（尚未减引用键开销），约占两批首text50.6%、所有工具text11.3%。跨两个批次共享才达到该上界；仅批内去重收益略低但实现/恢复更简单。

32个filing对象累计8,384字节，实际只有1个不同值262字节。column_headers累计256字节/唯一16；footnotes累计64字节/唯一2；xbrl_facts累计11,266字节、31个唯一值11,264字节，几乎不能去重。不要为追求压缩而删除不同字段的XBRL period/unit/dimensions/value。

所有工具JSON递归字段合计（可能嵌套，不可相加当总大小）：xbrl_facts59,635、source_contexts31,721、其内context22,908、table_context48,176、row_context2,314、column_headers2,990、footnotes64。

## 实际数据路径

- 当前运行对应ae0f9e5的sec_tools._cite_fields将每个单字段details完整放进items，再_result序列化为首text，并另提供details。
- checkpoint_projection只删除持久消息中严格重复details；**不改text，也不改变模型可见副本**。
- vertex_messages.to_vertex_request把toolResult.content全部放function_response；不传details。model_gateway._call直接把contents/config送SDK，无压缩模型视图。
- 因此表上下文确实在实际发送路径的text中重复；删details不能解决这部分输入膨胀。现有read_view已经在每次阅读回执内用source_contexts/context_ref去重，不应重复实现该局部功能。

## 最小无损方案（建议，未实现）

先只对`cite_filing_fields`构造**单回执内可逆模型投影**：

1. 每个items仍保留evidence_id、quote、精确locator的table/row/cell、各自XBRL事实及其period/unit/dimensions、row_context。
2. 把完全相同的table_context/filing（可选headers/footnotes）内容按canonical JSON内容hash放同一回执的shared_contexts，items用明确context_ref指向它。不同表头、单位、脚注或条件必须产生不同hash，不按table_index想当然合并。
3. 共享对象必须把原字段完整保留，禁止摘要或截尾。声明“引用对象包含所有表头、单位、脚注和来源条件”。投影只改变模型输入表示，rawCatalog、原始回执、permanent evidenceID、locator及Backend sourceIntegrity仍按原结构。
4. 最稳妥接入为model_gateway前纯投影（只改toolResult的模型副本），不改变持久化格式、Pi事件或恢复；本批内即可解引用，避免依赖很久以前的上下文。失败/未知结构原样透传，不压缩。
5. 不碰assistant及签名相关部分，不合并toolCall/response配对，不删除hostBudgetRemaining。恢复后由同一版本纯函数重建投影，输出可确定性比对。

必要离线测试：decode(encode(original))精确等于原JSON；同table不同脚注/单位不合并；两个表同时存在；相同数字不同坐标仍独立；实际最终SDK wire含共享完整对象及有效refs；输入rawCatalog/checkpoint/pendingEffects未被修改；恢复前后投影相同；malformed工具结果原样保留。必须量测真实发送JSON字节，不能把唯一值理论上界当已实现收益。

## 收益边界

此项有明确无损收益，但不会把164k输入降为几千。主要历史占比仍为22次阅读回执。进一步减少阅读历史需独立版本化上下文策略和可重读证据句柄；那涉及模型推理可用信息，不应混入本次“小型可逆去重”改动，也不能删除原文留存或把候选自动当事实。
