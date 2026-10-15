# 报告生成、检查与交付实现设计

日期：2026-09-10。L2 设计，依据当前三仓未提交代码读取。本文中的目标接口尚未实现；已实现部分单独标明。对齐总方案与 04 的完整 MVP 范围。

## 用户结果与职责

同一研究任务产出一份可读报告。Agent 可以根据具体检查问题补资料或改写；通过检查的正文、引用、计算和来源快照作为一个版本保存。用户点击引用时，读取该版本的原文，不能被随后重新抓取的页面覆盖。

报告结构可以随问题变化。短核验需要明确答案、口径和来源；完整财报分析需要关键指标比较、业务解释、现金与盈利质量以及具体不确定性。检查依据用户要求，不强制每次包含全部章节。

## 代码现状与合同差异

| 环节 | 当前真实实现 | 需要补齐 |
|---|---|---|
| 草稿提交 | ML `ReportDraftTools` 只接正文和引用，checker 为注入回调 | 真实检查传输、结构化拒绝反馈、候选保存 |
| 内容冻结 | Backend `build_research_report` 从宿主 catalog 取事实并重算派生值 | 与草稿检查使用同一 bundle，不靠模型重组 |
| 原文验真 | Backend `ResearchSourceIntegrityService` 重读 SEC bytes 并重解析字段 | Document 受信 reader 尚未接通；其他来源按支持矩阵扩展 |
| 模型审查 | ML `ResearchReportReviewer` 一次独立上下文给出事实与编辑结果 | Backend authority 当前要求两个 reviewer，与实际接口不一致 |
| 审查反馈 | Backend authority 拒绝时抛通用 ValueError | 给出可修复的 blockId/category/detail，同时区分技术失败 |
| 版本保存 | Backend delivery 再建 bundle、再调用 authority，然后 DAO 原子保存 | 避免草稿通过后重复付费审查以及第二次随机拒绝 |
| 阅读与导出 | Web 新正文、引用面板、计算导出已实现 | 原文 viewer 尚未接通；表格和段内引用尚未定义 |

依据文件：Backend `service/research_report/{contract,calculations,check_authority,delivery,source_integrity}.py`；ML `service/research_agent/{report_tools,report_review,research_session}.py`；Web `services/research-reports.ts`、`components/workspace/research-report-types.ts`。

## 检查边界决策

第一阶段采用一次独立模型审查，同时输出事实支持和编辑质量。独立指审查上下文不包含写作者的自我评价、过程会话或已通过断言。原文完整性、数值计算与模型审查仍分别执行和记录。

理由：当前 ML 已提供两个维度的结果；两次调用都读取同一报告和证据，尚无评测证明收益足以覆盖额外延迟和成本。保留逐项评分与具体问题即可支持后续评测，必要时再拆成两个 reviewer。不能将同一次调用包装成“两次独立审查”。

宿主检查顺序：

1. 授权并校验当前运行租约，取宿主保存的 catalog 和计算请求。
2. Backend 用权威合同构造 bundle，拒绝不存在或未使用的引用、非法结构和不兼容计算。
3. 重读被引用的冻结原文，验证哈希、解析版本、精确坐标和字段上下文。
4. 向独立 ML review 传入用户要求、冻结正文、选中证据及计算，取得事实和编辑结果。
5. 校验审查响应与本次请求身份及 bundle hash 的绑定，由 Backend 形成检查记录。

模型返回 passed 不是保存授权；客户端也不能提交 passed 来升级草稿。hash 只证明内容一致，鉴权与宿主调用关系才能证明检查记录来自受信流程。

### 修订反馈

业务拒绝返回 `status: rejected` 与 `issues`，每条包含 `category`、`blockId`、`detail`。类别为 contract/source/factual/coverage/editorial。提示描述缺了哪个条件或引用错在哪，不把正确答案直接塞给写作者。

技术失败包括来源存储暂不可读、模型调用失败、租约过期。返回可重试类别与安全错误信息；不得冒充“报告事实错误”，也不能默认为检查通过。发现未实现的来源类型，明确标记 unsupported_source，要求换用支持来源或保存未完成草稿。

审查结果必须至少有一条具体问题才可作为修订反馈：例如 supported=false 但 issues 为空时，检查器返回审查输出不完整，而不是让 Agent 无目标地重写。超出输入预算时明确失败或按完整章节分批检查，不能静默截断证据后给整份报告通过结论。

## 检查与原子保存的衔接

选择宿主保存检查结果。每次检查以 run_id、execution_scope、candidate_hash、规则版本为键；通过后保存 exact bundle 与检查记录。Agent 只收到候选 ID 和反馈，不获得可自行签发的发布凭据。

运行结束后，交付服务在同一受信执行上下文中读取检查过的候选。未改动的候选可复用结果；正文、引用、证据或计算有任何变化都必须重新检查。若跨进程恢复，必须从宿主持久化记录读取并复核 hash 和 scope，不能信任 ML 重传的 receiptHash。

DAO 最终事务核对：owner/workspace/run、活动 lease 与 execution_scope、报告基准版本、候选身份与检查 hash。随后同事务写报告版本、current pointer、Run/Step 终态和事件。两个并发交付中只有一个可推进当前版本；相同 run 与 hash 重试返回同一版本。

需要先检查现有 Run metadata/checkpoint 容量和持久化接口，再决定候选保存位置。逻辑上需要可信候选存储，并不意味着新增一套任务表。07 负责这个具体落点。

## 正文扩展：表格与精确引用

当前研究协议尚未上线。保留段落兼容，在首发前补齐表格块；若发现线上已有该版本数据，采用显式新版本与兼容解析，不原地修改已发布语义。

建议新增 table block：`id/type/caption/columns/rows`，列具有 `id/label`，行具有 `id/cells`。每个 cell 含稳定 `id`、展示文本和 `citationIds`，不能靠“行号第几个”作为永久引用。指标名、期间、单位、金额或增长率分别可追溯。复杂跨行合并首期不支持，优先语义清楚的矩形表。

数值单元格可带 `valueRef`，明确指向 evidence 或 calculation；服务从受信数值按展示单位和精度格式化。禁止让模型同时提交任意金额字符串和一个无关引用后，仅凭引用存在就判定一致。表头中的期间和单位也必须与 valueRef 对应字段兼容。

段落首期可保留段后引用；对于同时包含多个事实的长段落，设计 text/citation 的 inline 节点，使引用紧跟对应断言。不要依赖可漂移的字符偏移。对普通解释文字允许无引用，对可核实事实必须由独立审查检查支持关系。

表格与 inline 扩展必须同步：Backend contract → ML tool JSON schema → 独立 reviewer 输入 → Web type/validator/renderer → Markdown 导出 → 跨仓 golden fixture。仅加前端样式不算支持。

## 模板实现

模板是研究方法和产物默认结构，记录适用问题、需要回答的维度、证据要求、可选表格与质量标准。用户需求形成 task brief；Agent 按 brief 选择和调整模板。模板不负责推进 Run 状态。

首期三份可验收模板：事实核验、财报分析、跨来源比较。其余公司深度、事件影响和估值方法仍在产品目录内，按数据能力逐步完善。不能为了模板齐全生成缺少输入的估值结果。

完整报告的核心质量检查：摘要回答问题；指标表支持正文；分析说明变化机制而非重复同比；区分已披露事实、管理层解释和自身推断；风险具体关联公司和研究期；未知项说明影响哪些结论。正文不暴露内部 schema、Gate 或检查日志。

## 实施顺序与测试

1. 统一 reviewer/authority 接口和拒绝语义，测试 source 失败不调用模型、模型拒绝能反馈、未完成审查不通过。
2. 接入运行宿主的检查候选存储与交付，测试内容修改失效、lease 过期、相同结果重放、并发基准版本冲突。
3. 注册权威计算工具并扩展表格合同，同步三仓 golden fixture 与导出校验。
4. 完成新引用 original viewer，真实 Chrome 检查表头、期间、金额、输入公式及版本隔离。
5. 用真实研究任务验收短报告、完整报告、多来源比较与后续研究；保留失败和修订过程，不用 mock 代替产品证明。

验收样本必须包含：成本数字冒充收入、正确数字但错误期间、同名指标不同单位、重复来源不算独立佐证、公式输入缺失、原文版本变化、表格金额与正文冲突、引用存在但不支持论断。每项检查都需要正确报告的正例，避免系统只会拒绝。

## 尚未证明

独立模型审查的实际准确率、长报告上下文成本、Document 字段原文验真、表格展示与导出、检查候选跨进程恢复，以及真实用户链路都仍未完成。离线通过不等于上述能力已达到 MVP 标准。

## 结构表格实现状态更新

table block已在Backend合同/Markdown交付投影、ML submit_report/review和Web renderer/export实现。实际结构为{id,type:table,caption,columns:[{id,label}],rows:[{id,cells:[{id,text,citationIds}]}]}。2–12列，1–100行，单元格数量与列数一致；所有anchor全文唯一并保留summary。cell引用参与原有证据/计算绑定，不新建平行引用协议。当前仅离线与跨仓合同测试完成，真实模型产物和Chrome表格验收未完成。
