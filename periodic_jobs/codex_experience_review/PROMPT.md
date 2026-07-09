# Codex Experience Review 周期任务

## 目标

系统性阅读和检索徐昊所有可访问的 Codex 对话记录与执行日志，复盘 agent 执行过程，提炼可复用经验，并更新：

`contexts/thought_review/codex_execution_experience_review.md`

## 必读入口

开始前必须读取：

- `AGENTS.md`
- `rules/SOUL.md`
- `rules/USER.md`
- `rules/WORKSPACE.md`
- `rules/COMMUNICATION.md`
- `rules/skills/INDEX.md`
- `contexts/thought_review/codex_execution_experience_review.md`

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
5. 写入 living document。合并重复条目，保留高价值规则，删除或降级过期内容。
6. 在文档中记录本次复盘范围，但不要写入 secrets、token、cookie、私密消息明文或第三方隐私。
7. 完成后输出简短中文汇报，列出更新了哪些小节、证据范围和未能读取的来源。

## 写作标准

- 使用中文，专有名词保留英文。
- 直接写判断，不要客套。
- 遵守 `rules/COMMUNICATION.md`，避免 AI 味格式化写作。
- 经验必须可执行：不要只写“要严谨”，要写“下次遇到 X，先做 Y，再验证 Z”。
- 规则清单必须能被未来 Codex session 直接遵循。

## 完成标准

- `contexts/thought_review/codex_execution_experience_review.md` 被更新。
- 文档包含执行经验总结、偏好与理念档案、可复用规则清单。
- 更新内容能追溯到真实 Codex 对话、执行日志或 memory rollout summary。
- 没有泄露敏感信息。
