# Agent App Survey 2026-06-15

## 初步结论

用户目标是 Codex App 类产品，不是 CLI。核心评价维度应从 model loop 转到 workspace/task/session/worktree/event/diff/approval/replay。

## 候选项目判断

- `OpenCovibe`: 最像 Codex App 的直接 wrapper。Tauri + Svelte + Rust。强项是把 Claude/Codex CLI 的事件变成可视化 session UI。它抽象了 `SessionProtocol`，把 Claude stream-json 和 Codex app-server JSON-RPC 隔离到 adapter。适合参考 agent protocol adapter 和 session replay。
- `xuanpu`: 最有产品判断。Electron + React + GraphQL + SQLite。强项是 Field Event Stream、Working/Episodic/Semantic memory、现场注入、checkpoint。适合参考产品方向和 context layer。
- `codeg`: 多 agent 聚合器。Tauri + Next + Rust。强项是 ACP manager、delegation broker、sub-agent session、IM channel、server/Docker 部署。适合参考 multi-agent aggregation。
- `kanbots`: 任务板方向最完整。核心模型是 issue/thread/chat session/agent run/worktree/check/preview/promotion/learning。适合参考任务操作台和 review flow。
- `ouijit`: 最底层、最朴素。Electron + SQLite + node-pty + worktree + Lima sandbox。适合参考本地 task/worktree/terminal 生命周期。

## 设计启发

- 产品主轴不应是 chat，而应是 Task/Session/Run/Artifact。
- 底层 agent 执行器应可替换，优先保留 Codex/Claude/OpenCode adapter seam。
- SQLite 是本地应用事实标准；JSONL 适合高频 event log，SQLite 适合索引和 UI 查询。
- worktree 是并行 agent 的默认隔离面；sandbox/VM 是高风险执行的第二层。
- 权限审批必须是一等事件，进入 event stream 和 UI queue。
