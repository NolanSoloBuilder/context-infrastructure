# Workspace 执行指南

## 启动与按需读取

- 默认只读 `contexts/thought_review/codex_execution_experience_review.md`（L0）；当前上下文已包含且文件未变时直接复用，不重复读取。
- 闲聊和基于当前对话的追问直接回答；仅在事实或背景有缺口时查资料。
- 按下表读取必要材料，不预先全文加载 `rules/`，不为熟悉的任务重复查索引。

| 任务 | 入口 |
| --- | --- |
| 找文件、选择产物落点 | 先查 `rules/WORKSPACE.md`，再在目标目录搜索；新项目缺失时补充路由 |
| 用户身份、对外名称、背景 | `rules/USER.md` |
| 正式文稿、对外内容、翻译 | `rules/COMMUNICATION.md` |
| 价值观与协作原则 | `rules/SOUL.md`；需要历史依据时再检索 |
| 需要尚未掌握的能力 | 先用当前可用 Skill；本地能力查 `rules/skills/INDEX.md` |
| 深度调研 | `rules/skills/workflow_deep_research_survey.md` |
| 准备委派独立子任务 | `rules/skills/workflow_parallel_subagents.md` |
| 安装、迁移、升级 Skill | `rules/skills/skill_scope_management.md` |
| 首次配置工作区 | `setup_guide.md` |

## 任务与记录

- 主 Agent 可按独立性、规模和实际收益主动委派，无需用户再次点名；运行环境有额外限制时遵循其限制。模型与 API 按当前环境选择。
- 明确决策、重复故障处置、接口/状态/回滚合同及用户明确指定的长期偏好，写回已有对应文档；只有现有落点不足时新建。
- 一次性解释、闲聊和临时纠正无需额外落盘；单项目事实留在项目内，不升为全局约束。落点按 WORKSPACE 选择。
- 不记录凭据或第三方隐私。对外发送及不可逆操作遵守用户授权，已有授权不重复询问。

## 验证

- 按改动后果选择定向验证，保护已有脏改动与其他聊天的进程；本机重任务调度和工具隔离继承全局规则。
- 涉及 Mindspace Workspace Harness、workspace-scoped conversation、memory/source/artifact/run 回写、checkpoint、Agent Plaza evidence bridge 或三仓联动时，先读 `contexts/survey_sessions/2026_06_18_workspace_harness_e2e_smoke_runbook.md`。
- 上述链路优先 Backend API E2E 与离线契约 E2E，覆盖 SSE、checkpoint 续接、Workspace Memory、runtime references、artifact provenance 与 ML evidence pack；显式需要真实链路时再开三服务 live smoke。
- 本地 Mac/SwiftUI App 界面、文案或交互修改后，必须重建或重新打包，关闭旧 App 再打开验证。

## 会话与记忆

- `【长期】` 精确前缀表示需长期保留；其他已结束会话可进入删除候选，排除运行中的聊天和 automation。
- 批量删除先做只读 dry-run，报告保留数、候选数、预计空间及异常标题；用户确认当次清单后才删除。优先原生删除，不单删 rollout 留下悬空索引。
- 动态观察按需查 `contexts/memory/OBSERVATIONS.md`，个人原则按需查 `rules/axioms/INDEX.md`。历史 observer/reflector 位于 `periodic_jobs/ai_heartbeat/`；任务是否运行以当前状态为准。
