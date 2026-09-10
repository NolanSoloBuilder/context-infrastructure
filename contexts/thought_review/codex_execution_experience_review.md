# Codex 执行经验启动卡

> 这是默认加载的 L0 热路径文档。目标不是记录所有经验，而是让每次新会话先拿到最稳定、最高频、跨任务通用的协作约束。

## 分层约定

- `L0`：当前文件。默认加载，只保留跨任务、高频、稳定规则。
- `L1`：按需专题卡。只有任务命中对应主题时再读。
- `L2`：冷数据。包括 automation memory、rollout summaries、session/log/sqlite 原始证据，只在追证或周期复盘时读取。

## L1 专题卡

- 工程交付与验证：
  `/Users/xuhao/Documents/Other/context-infrastructure/contexts/thought_review/codex_execution_experience/engineering_delivery.md`
  触发词：修 bug、发布、回滚、MCP、Chrome、数据库、部署、mock、hard-cut、git、worktree、环境修复、系统卡顿、本机性能。
- 产品、UI 与协作偏好：
  `/Users/xuhao/Documents/Other/context-infrastructure/contexts/thought_review/codex_execution_experience/product_ui_and_collaboration.md`
  触发词：UI、文案、产品方案、交互、页面改版、设计评审、解释架构、先讨论方案。
- 敏感研究与外部操作：
  `/Users/xuhao/Documents/Other/context-infrastructure/contexts/thought_review/codex_execution_experience/sensitive_research_and_external_ops.md`
  触发词：金融、开户、股息、邮箱、截图转账、外部资料归档、竞品、license、隐私。
- 周期复盘维护：
  `/Users/xuhao/Documents/Other/context-infrastructure/contexts/thought_review/codex_execution_experience/review_maintenance.md`
  触发词：experience review、automation、session 统计、memory rollout、sqlite 日志范围、文档维护策略。

## 热路径规则

1. 找文件先查 `rules/WORKSPACE.md`；只有任务命中本页列出的触发词，才读取对应 L1，不做全文加载。
2. 任何会变化或风险高的事实都要 live verification；引用、偏好和已执行证据分开表达；选型建议不能写成实际采用事实。
3. 判断问题优先沿真实链路取证，区分实现存在、运行时生效和用户可见结果；历史摘要与后续原始记录冲突时，回读最新结果，单层文案、配置或 symptom 不能直接当根因；查询无结果只说明当前查询未命中，不能据此断言能力或行为不存在。
4. 改动前核对工作区和任务绑定，保护已有脏改动；用户限定分支、worktree 或本地状态时，不能沿用旧 session 的结论。
5. 用户说先讨论或收窄范围时，只做相应层级的分析，列清合同差异和未决点，不擅自编辑或扩展推断。
6. 只要结论未来可能复用，就按 `rules/WORKSPACE.md` 写回合适文档；完成态按用户目标定义，不制造空提交或验证噪音。
7. 不在聊天、仓库或长期规则中记录敏感明文；涉及外部系统时，只报告已核验的能力边界。
8. 专题诊断、发布、UI、金融和外部资料规则一律在 L1；本页不为少数项目或单次案例增加条目。

## 徐昊稳定偏好

- 交流用中文，直接、短、可执行，不要客套和空判断。
- 用户明确说“先产出方案”“先不要改代码”时，完成态就是方案、合同差异和未决点；读代码与对接口可以做，任何编辑都要等明确批准。
- 架构和代码讲解基于当前真实实现；先给可执行结论，再说明证据、假设和未知。
- 文案、状态和字段语义优先尊重用户给定 wording；关键状态和来源必须可核验。
- 产品和 UI 追求克制、可扫描、与真实能力一致，不保留假入口或误导性 fallback。
- 默认把“上下文沉淀”理解为业务规则、状态流、接口契约和回滚约束，不做泛化的知识库堆积。

## 默认加载边界

- 本页目标是让新会话快速选对证据路径和 L1 专题卡；不记录运行统计、案例、长清单或专题操作步骤。
- 条目晋升、降级和周期统计只在 `review_maintenance.md` 维护；默认会话不读取该维护卡。
