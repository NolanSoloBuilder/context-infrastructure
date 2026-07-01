# Skill: Codex Thread 迁移与 Handoff

## When to Use

当需要把另一个 Codex 会话、Code Space 会话或远端实例里的工作迁移到当前 Codex 实例时使用。

## 能力边界

当前 Codex App 的 thread 工具可以处理本地 host 和已连接 remote host 上可见的 thread。可见 thread 可以通过 `list_threads` 查到，并可用 `handoff_thread` 把 thread 及关联 git 状态移动到当前 host 或匹配的 saved-project worktree。

`handoff_thread` 会中断正在运行的目标 thread。执行前要确认目标 thread 是否还在产出重要内容。

云端 handoff 当前不支持。如果目标会话位于不可见的 GitHub Codespaces、未连接的 Code Space、另一个账号或另一个不可访问的 Codex 实例里，当前实例无法直接移动那条原始 thread。

## 判断步骤

1. 用 `list_threads` 按标题、关键词或最近列表查找目标 thread。
2. 如果目标 thread 可见，读取 `threadId`，确认目标 host 和工作目录。
3. 如果用户明确要迁移，调用 `handoff_thread`，目标为当前 host 时使用 `destinationHostId="local"`。
4. 如果目标 thread 不可见，走手动迁移。

## 手动迁移路径

在原会话里生成一份 handoff 文档，至少包含：

- 当前目标和问题定义
- 已评估方案、判断结论和证据
- 关键文件、分支、commit、未提交改动
- 已运行命令和验证结果
- 未解决问题和下一步建议

文档落点按 workspace 规则选择。调研和方案评估优先放 `contexts/survey_sessions/`，命名为 `yyyy_mm_dd_<topic>.md`。如果涉及代码改动，通过 git commit/push 或 patch 文件把工作树状态带到当前实例。当前实例读取 handoff 文档后继续执行。
