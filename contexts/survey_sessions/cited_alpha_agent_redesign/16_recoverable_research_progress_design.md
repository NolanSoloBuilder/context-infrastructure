# 可恢复研究进度：最小 Backend/Web 协议设计

2026-09-11；只读设计，未修改代码、未触碰live Run。依据当前ResearchCheckpointService与DAO、实际Pi工具定义、Web5秒Run观察机制。

## 推荐结论

增加一个由Backend生成、随checkpoint指针同事务保存的`researchProgress`公开投影。Web继续读原Run/Workspace API和原轮询，不建新workflow、事件总线、SSE或第二套调度器。显示当前已知活动与已登记证据数，不显示百分比、不输出模型思考、不把数量叫“已验证事实”。

第一版无需修改ML协议：用两个已验证checkpoint之间的变化推导“最近活动”，不会承诺精确实时状态。模型调用只能叫“分析与组织信息”，不能在没有明确事件时断言“正在撰写报告”。若后续必须细分写作，需要ML host在明确动作处发有限activity enum；不从模型文字/arguments推测，不在第一版扩大实现。

## 最小公开合同

在现有`WorkspaceRun`新增可选字段（旧Run/客户端兼容）：

```
researchProgress?: {
  schemaVersion: "research-progress/v1",
  checkpointCursor: string,
  activity: "preparing" | "choosing_method" | "searching" | "reading"
    | "collecting_evidence" | "calculating" | "analyzing"
    | "submitting" | "checking_report" | "ready_for_delivery" | "researching",
  evidenceRegisteredCount: number | null,
  calculationRegisteredCount: number | null,
  updatedAt: string
}
```

- `checkpointCursor`是host生成的opaque step/sequence身份，可由step_id与sequence组成；只用于对应刷新快照，不供用户展示。旧Step恢复不能拿新Step的同sequence当同一事件。
- `updatedAt`由Backend保存投影时生成timezone-aware UTC并输出Z/offset，表示“该研究进度快照保存时间”。不复用heartbeat时间、不复用已观察到时区不明确的createdAt。
- count只表示当前已保存catalog/计算记录的去重数；未完成/拒绝的calculate不能加数，重复引用同ID不能加数，`read_filing`阅读结果不增加证据数。
- null表示旧/不合规记录无法可靠投影；不可用显示不出现数量，不能用0假装已检查为空。
- 不传query、URL、sourceTitle、tool arguments、toolCallId、messages、draft文本、thought/signature、prompt、token或者GCS URI。第一版连模型/工具调用数也不必给用户。

用户示例：
“最近活动：阅读来源材料 · 已登记33条证据、8项计算”
“最近活动：检查报告 · 已登记33条证据、8项计算”
数量旁简短说明：“登记数量不代表全部通过报告审阅。”可放tooltip；措辞不要把未验证catalog叫已审阅证据。

## 后端落点与原子性

1. 新`mindspace/service/research_runtime/progress_projection.py`，纯函数投影。输入当前已过`_validate_progress`的progress、上个progress、host当前candidate/检查边界；只输出闭合集合字段。不可执行DAO、源读取或模型。
2. `ResearchCheckpointService._persist`（checkpoint_service.py:75）调用投影后，把`public_progress`作为独立host参数送到`save_research_checkpoint`。不允许ML通过progress附加`researchProgress`；PROGRESS_KEYS保持不接收它。
3. `WorkspaceResearchCheckpointDaoMixin.save_research_checkpoint`（workspace_research_checkpoint_dao.py:87）在原Run→Step锁/lease/CAS事务内：保存Step.researchCheckpoint指针，同时merge `run.metadata_["researchProgress"] = validated_projection`。其它metadata原样保留。这样GET不必每5秒从GCS读取MB级transcript，不新增SQL列/表/migration。
4. DAO必须再验证projection schema/enum/count/UTC/cursor与当前pointer绑定。相同pointer的幂等重放不能只更新public progress；same pointer+不一致projection应拒绝，避免无checkpoint依据的漂移。
5. `_run_payload`只在research-v1明确投影顶部researchProgress；不要直接把整个metadata或checkpoint拿来展示。当前metadata本来公开，并不意味着新的内部内容都安全，存入metadata的本字段自身必须可公开。旧客户端忽略新增字段，新Web缺失时保持Working...
6. `lastProgressAt`若要同步必须区别既有heartbeat语义，第一版用独立updatedAt，避免把租约续命当研究进展。

**重要信任边界**：当前`_validate_progress`只保证scope/question/asOf、集合形状和计数，未逐项独立验证rawCatalog每条事实。因此projection必须只声称“登记”。建议只计结构可识别且key==entry.evidence_id的条目；混入malformed条目时返回null而非将任意dict.length当可靠事实数。无需为了进度额外进行字段源码核验；实际事实资格仍由SourceIntegrity/Calculation/ReportCheckAuthority负责。

## 活动映射及推断规则

这些是当前动作标签，允许任意往返；不是必经阶段，更不是进度条。

| 已有host信号 | activity | 用户文案 |
|---|---|---|
| 尚无checkpoint，Run queued | preparing | 等待开始 |
| 新的read_research_method intent | choosing_method | 选择研究方法 |
| find_filings / search_documents intent | searching | 查找来源材料 |
| read_filing / read_document intent | reading | 阅读来源材料 |
| cite_filing_field / cite_filing_fields / cite_filing_text / cite_document_field intent | collecting_evidence | 登记来源证据 |
| calculate intent | calculating | 计算指标 |
| budgetUsage.modelCalls相对前checkpoint增加 | analyzing | 分析与组织信息 |
| 新submit_report intent（check callback尚未进入） | submitting | 准备检查报告 |
| Backend check_draft真实进入并持久化旧candidate失效 | checking_report | 检查报告 |
| Backend验证receipt并保存checkedCandidate | ready_for_delivery | 保存报告 |
| 多个不同活动并行/未知tool/无法确定当前 | researching | 继续研究 |

具体约束：
- 不根据pendingEffects对象“最后一个key”猜当前活动。用与上个checkpoint的差集，查新增/状态变化effect；多个不同类型同时出现降为researching，宁可不精确。
- intent与completed都可保留同一个“最近活动”标签；Web不要把completed活动说成当前仍执行。新的modelCalls增加覆盖最近tool为analyzing。
- 同一checkpoint若有新tool intent和model增量，优先新tool；旧悬空intent不能压过新动作。若存在未知未完成effect且host进入恢复，应由Run失败/等待状态覆盖动词，不假装正在重新执行。
- `read_research_method`不计证据，不显示具体method参数；方法只是可选能力。
- `submit_report`intent只能说明尝试提交，不是审阅开始/通过。`check_draft`初次invalidating `_persist`可通过host-only参数标记checking_report，包含schema/source/semantic/editorial检查，不假称全部同时运行。
- receipt通过后保存candidate只是ready_for_delivery，不得显示任务完成；真实Run succeeded/artifact version事务才决定完成。
- 审阅拒绝后的持久checkpoint仍是checking_report“最近活动”，之后新模型调用变analyzing；若希望即时“根据反馈修订”，须增加一个host确定的rejected投影写入并绑定新checkpoint，第一版不必新增额外存储写入。不能从issue原文推测。
- 首次模型调用已被budget-before-call checkpoint覆盖；虽然不含当前思维/写作内容，analyzing已足够表达在推进。

## Web最小接线

- `src/app/services/workspaces.ts`增加可选类型及小型schema guard；未知schema/enum/malformed counts/无timezone updatedAt降级为无研究进度，不能throw导致整页丢失。
- 沿用`useWorkspaceRunObservation`5秒轮询与Workspace初次GET，刷新恢复立即显示已持久投影。无需新增计时器/订阅；旧响应受现有组件卸载/runKey处理约束，新增状态与runId绑定，不跨Run继承数量。
- 在现有RecoveryBanner新增可选`progress`或已本地化文案slot；在page层用t()映射封闭enum。不要用后端自由文本直接innerHTML。
- 每次poll若cursor与payload相同，不触发live region重复播报；更新用`aria-live=polite`，不要每5秒朗读Working。
- 它不是报告内容。右侧没有artifact时可以复用同一snapshot显示“报告尚未生成”，不要造占位正文或恢复空V1。
- 首版无需点开原始events/transcript。证据列表和来源点击仍依赖正式citation路径，不能从progress count生成可点来源。

## 状态优先级/恢复

1. 真实Run终态最高优先级：succeeded=报告已交付；failed/canceled=任务失败/取消，可附“最后活动：X”和保留登记数。不能因旧activity为checking_report继续spinner。
2. waiting采用现有waitingReason/resumeCondition用户可操作合同，progress仅“上次活动”。不能自动重试工具或调用模型。
3. running=“最近活动：X”；较久无新checkpoint可标“最后更新于…”，不可单靠阈值判断失败/模型卡死。
4. heartbeat不断续租但checkpoint未变时updatedAt保持不变。lease与研究进度分开。
5. 同Run进程恢复沿用已保存progress；new retry Run不复制父run metadata冒充新进度。初始无字段显示准备中，后续按新Run catalog真实计数；通过既有授权机制继承文档不等于继承证据数量。
6. 业务不因UI projection失败而伪造完成：恶意/新格式投影可降级null，但合法scope/CAS/原文/receipt错误仍按现有fail-closed。投影只读展示不改变原运行决策。

## 验收与兼容测试

Backend纯投影：方法read不加证据；find/read不加证据；batchcite重复ID去重；calculate拒绝不加数；model计数变化=analyzing；unknown tool/multiple effects保守降级；malformed entry count=null；submit intent不等于passed；host receipt保存才ready_for_delivery。恶意query/thought/signature内容不出现在任何public JSON字符串中。

DAO契约：同事务pointer+metadata；scope/lease/CAS冲突两者均不更新；GCS写成但CAS失败不显示新进度；相同pointer幂等不能改projection；原metadata保留；旧checkpoint加载不要求progress字段；终态payload覆盖活动。

Web状态：已有researchProgress首屏恢复；轮询改变活动/count；没有字段/未来schema降级Working；active不显示lease秒数；failed保留最后活动且无spinner；同Run旧响应不覆盖新状态；切换workspace/run清除；精确中英文文案；DOM不含raw参数。

实际链路：在下一条授权真实Run中观察方法/检索/读取/证据计数/检查；刷新保持同cursor/count，禁用网络再恢复只读刷新；成功后用真实artifact/citation验收，不把count当验收结果。离线模拟SQL+真实服务contract先行，不为进度UI额外开paid Run。

跨端：API仅新增可选字段，Mobile现有Run解析忽略未知字段应实查；不改变status/resultSummary/retryAfterSeconds已有语义。最多Backend+Web两仓代码和i18n，ML和Node loop第一版均可不改。
