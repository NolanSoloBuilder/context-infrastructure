# Codex Experience Review 周期任务

## 目标

系统性阅读和检索徐昊所有可访问的 Codex 对话记录与执行日志，复盘 agent 执行过程，提炼可复用经验，并按分层策略更新：

- `contexts/thought_review/codex_execution_experience_review.md`（L0 启动卡，默认加载）
- `contexts/thought_review/codex_execution_experience/`（L1 专题卡，按需加载）

## 必读入口

开始前必须读取：

- `AGENTS.md`
- `rules/SOUL.md`
- `rules/USER.md`
- `rules/WORKSPACE.md`
- `rules/COMMUNICATION.md`
- `rules/skills/INDEX.md`
- `contexts/thought_review/codex_execution_experience_review.md`
- `contexts/thought_review/codex_execution_experience/review_maintenance.md`

## 数据范围

优先读取并交叉验证：

- `/Users/xuhao/.codex/sessions/`
- `/Users/xuhao/.codex/archived_sessions/`
- `/Users/xuhao/.codex/memories/MEMORY.md`
- `/Users/xuhao/.codex/memories/rollout_summaries/`
- `/Users/xuhao/.codex/logs_2.sqlite`
- `/Users/xuhao/.codex/sqlite/logs_2.sqlite`

可以读取当前 workspace 的 `contexts/`、`rules/` 和 `periodic_jobs/` 作为长期规则对照。

## 执行步骤

1. 建立索引：统计可读 session、archived session、memory rollout summary、sqlite 日志库的数量和时间范围。
2. 抽样与定向检索结合：优先检索包含“失败、修复、回滚、缓存、验证、AGENTS.md、偏好、UI、文案、Chrome、数据库、部署、MCP、skill、mock、hard-cut”等关键词的记录。
3. 对每个候选经验抽取四类信息：触发场景、问题做法、正确做法、可复用规则。
4. 对用户偏好单独归类：UI 设计偏好、产品设计理念、交互原则、沟通偏好、工程验证偏好。
5. 先决定写入层级，再落文档：
   - `L0` 只放跨任务、高频、稳定规则和核心偏好。
   - `L1` 放主题规则卡，按任务类型拆分。
   - `L2` 放 automation memory、rollout summary 和原始证据。
6. 新发现默认先进 `L2`；只有满足“重复 2 次以上 / 高风险 / 稳定偏好”之一，才升到 `L1`。
7. 只有满足“跨任务通用 + 高频命中 + 不读就容易反复犯错”三项，才升到 `L0`。
8. `codex_execution_experience_review.md` 不是周报，也不是总档案。不要把 session 统计、样本清单、空数据源说明和逐轮变更历史写进 `L0`。
9. `review_maintenance.md` 负责记录本次复盘范围、数据源状态和维护策略；运行级细节、续跑锚点和新增候选经验写入 automation memory。
10. 默认优先删减、合并和降级，而不是追加。没有新的长期规律时，只更新 `review_maintenance.md` 和 automation memory。
11. 完成后输出简短中文汇报，列出更新了哪些层、哪些小节、哪些来源未能读取。

## 写作标准

- 使用中文，专有名词保留英文。
- 直接写判断，不要客套。
- 遵守 `rules/COMMUNICATION.md`，避免 AI 味格式化写作。
- 经验必须可执行：不要只写“要严谨”，要写“下次遇到 X，先做 Y，再验证 Z”。
- 每一层都要控制体积：`L0` 追求最小热路径，`L1` 追求专题密度，`L2` 承接细节。
- 规则必须能被未来 Codex session 直接遵循；不能直接执行的背景材料留在 `L2`。

## 完成标准

- `contexts/thought_review/codex_execution_experience_review.md` 或 `contexts/thought_review/codex_execution_experience/*.md` 被按需更新。
- `review_maintenance.md` 与实际复盘范围一致。
- 更新内容能追溯到真实 Codex 对话、执行日志或 memory rollout summary。
- 没有泄露敏感信息。
- 文档没有新增按日期堆积的运行日志式尾巴，也没有把冷数据重新塞回 `L0`。
