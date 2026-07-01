# Codex App 类开源项目调研

日期：2026-06-15

## 结论

如果目标是做一个类似 Codex App 的产品，最值得深读的不是传统 agent framework，而是这五类项目：

1. `OpenCovibe`：Codex/Claude CLI 的本地桌面可视化壳，适合抄 agent adapter 和 session UI。
2. `玄圃 Xuanpu`：最接近下一代 agent 工作台的产品思路，适合抄 Field Context 和现场注入。
3. `codeg`：多 agent 聚合器，适合抄 ACP、多 agent delegation、远程 server/IM channel。
4. `kanbots`：任务板 + agent run + worktree，适合抄 task/run/review/promotion 模型。
5. `ouijit`：轻量 task/terminal/worktree manager，适合抄本地生命周期和 sandbox。

我的判断是：如果从 0 到 1 做产品，不应该 fork 某一个项目直接改。更合理的是组合它们的架构优点：

- App 外壳：`OpenCovibe` 或 `玄圃` 路线。
- 任务模型：`kanbots` 路线。
- 多 agent adapter：`codeg` 路线。
- 本地 worktree/terminal/sandbox：`ouijit` 路线。
- Context layer：`玄圃` 路线。

## 1. OpenCovibe

Repo: [AnyiWang/OpenCovibe](https://github.com/AnyiWang/OpenCovibe)

`OpenCovibe` 是 Tauri v2 + Svelte + Rust。README 的定位是：把 Claude Code / Codex 这类 CLI 包一层桌面 UI，补上 terminal 没有的 persistent dashboard、visual diff review、cross-session history、multi-provider switching。

它最有参考价值的不是功能清单，而是 backend 抽象。`src-tauri/src/agent/session_protocol.rs` 把不同 agent wire protocol 隔离成 `SessionProtocol`：

- Claude 走 stream-json 和 control request/response。
- Codex 走 `app-server` JSON-RPC。
- actor 负责 mailbox、timeout、cancel、stdin ownership、turn queue。

这对你很重要，因为 Codex App 类产品不能把 UI 绑定死在某个 CLI 的 stdout 格式上。正确 seam 是：

```text
Agent CLI / SDK
  -> Protocol adapter
  -> Canonical event
  -> Session actor
  -> Event store
  -> UI replay
```

`OpenCovibe` 还把 Codex 的新能力接得很细：`thread/compact`、`thread/rollback`、`thread/goal`、`request_user_input`、runtime skills、feature flags、model catalog、MCP、hooks、permissions。这说明它不是简单 terminal wrapper，而是在认真跟 Codex app-server 协议。

风险是它的产品模型仍然偏 chat/session，没有把 task/worktree 作为顶层产品对象。

## 2. 玄圃 Xuanpu

Repo: [slicenferqin/xuanpu](https://github.com/slicenferqin/xuanpu)

`玄圃` 是 Electron + React + GraphQL + SQLite。虽然 stars 少，但它的产品判断最接近你说的方向。README 和 `docs/VISION.md` 的核心是：不是把 AI 塞进编辑器，也不是给终端换皮，而是为 agent 提供现场。

它的关键设计是 Field Event Stream：

- `worktree.switch`
- `file.open` / `file.focus`
- `file.selection`
- `terminal.command`
- `terminal.output`
- `session.message`
- `session.approval`
- `git.status_change`

这些事件进入 SQLite，然后构造成 Working / Episodic / Semantic 三层记忆，再在每次 agent 调用前注入。

代码上，`src/main/field/context-builder.ts` 已经实现了一个可读的 context pipeline：

- privacy gate
- 读取 worktree metadata
- flush event sink
- 读取 semantic memory
- verify checkpoint
- 查询最近 field events
- 推导当前 focus file / selection / last terminal / recent activity

这套东西比普通 agent dashboard 更关键。Codex App 的真正壁垒也不只是能跑 agent，而是 agent 能看到用户正在做什么、刚才做了什么、上一轮断在哪里。

风险是玄圃目标很大，架构也重。它更适合作为产品和 context layer 参考，不适合作为直接 fork 底座。

## 3. codeg

Repo: [xintaofei/codeg](https://github.com/xintaofei/codeg)

`codeg` 是 Tauri + Next.js + Rust，定位是 multi-agent coding workspace。它支持 Claude Code、Codex、OpenCode、Gemini、OpenClaw、Cline、Hermes，并且有 desktop、server、Docker 三种部署形态。

最有价值的部分是 `src-tauri/src/acp`。它不是只 spawn CLI，而是在做统一 connection manager：

- `AgentType`: ClaudeCode / Codex / OpenCode / Gemini / OpenClaw / Cline / Hermes。
- `ConnectionManager`: 管理 agent connection、spawn dedup、handshake timeout、pending questions。
- `delegation`: broker、spawner、listener、companion，支持主 agent 调子 agent。
- `permission`/`question` 作为连接状态的一部分。

这适合参考多 agent 聚合层。尤其是它区分 parent session 和 delegated sub-agent session，这点很重要。否则 UI 会把子任务和用户主任务混在一起，状态会乱。

风险是 `codeg` 很像聚合器，产品焦点容易散。它有 IM channel、pet、server、项目脚手架等很多方向。你如果照着做，容易做成“什么都接一点”的平台。

## 4. kanbots

Repo: [leodavinci1/kanbots](https://github.com/leodavinci1/kanbots)

`kanbots` 是 Kanban board + 多 agent CLI。它的产品模型比 chat 更像真实工作管理：

```text
Issue / Thread
  -> Chat Session
  -> Agent Run
  -> Worktree
  -> Agent Events
  -> Checks / Preview / Promotion / Learning
```

`packages/local-store/src/types.ts` 里能看到它的数据模型：

- `Thread`
- `ChatConversation`
- `ChatSession`
- `Message`
- `Card`
- `AgentRun`
- `AgentEvent`
- `AgentCheck`
- `Promotion`
- `Learning`

这里有几个值得直接借鉴的点：

- `AgentRunStatus`: `starting/running/awaiting_input/complete/failed/stopped`
- `SuccessSignal`: `pending/failed/stopped/aborted_budget/completed_with_failed_checks/completed_clean/promoted`
- `PreviewState`: `idle/booting/live/crashed/stopped`
- `Learning`: 从历史 run 中沉淀 repo convention/gotcha/fragile/decision-rationale

`packages/dispatcher/src/worktree.ts` 还有一个很实际的安全设计：创建 worktree 后写 `pre-push` hook，阻止 agent worktree branch 直接 push。这个细节很值得保留。

风险是 Kanban 不是 Codex App 的唯一交互形态。如果你做个人 agent command center，任务板应该是主视图之一，但不要让产品变成 Jira clone。

## 5. ouijit

Repo: [ouijit/ouijit](https://github.com/ouijit/ouijit)

`ouijit` 是 Electron + SQLite + node-pty，定位更朴素：task and terminal session manager。它支持 Claude Code、Codex、Pi，核心能力是 task、terminal、worktree、lifecycle hooks、Lima sandbox。

它的价值在于简单和工程可落地：

- task 移到 `in_progress` 时创建 worktree。
- worktree 默认放在 `~/Ouijit/worktrees/<project>/T-<taskNumber>`。
- 可以复制 gitignored files 到 worktree，解决 `.env`、本地配置、依赖缓存等真实问题。
- 可以为 task 开 terminal。
- 可以用 Lima VM 做 sandbox。
- 有 recover worktree、trash worktree、merge branch 等本地生命周期。

`src/worktree.ts` 和 `src/taskLifecycle.ts` 很值得看。它没有太多模型抽象，但把本地开发工作流的脏细节处理得比较现实。

风险是 agent 层较薄，更多是“让 CLI agents 有地方跑”。如果你想做 Codex App 级别体验，需要补 session event、diff review、approval、context injection。

## 设计建议

我建议你的产品不要从 chat 开始建模，而是从四个对象开始：

```text
Workspace
  -> Task
  -> Session
  -> Run
  -> Artifact
```

其中：

- `Workspace`: repo、关联 repo、环境、默认 agent、setup/run scripts。
- `Task`: 用户真正要完成的工作，可进入 backlog/running/review/done。
- `Session`: 一个 agent 对话线程，可 pause/resume/fork。
- `Run`: 一次具体执行，有 pid、worktree、status、cost、logs、events。
- `Artifact`: diff、commit、PR、preview URL、test result、screenshot、report。

第一版最小闭环：

1. 选择 repo。
2. 创建 task。
3. 自动创建 worktree。
4. 启动 Codex/Claude/OpenCode 任一 agent。
5. 把 agent stream 转成 canonical events。
6. 展示 activity、terminal、diff、approval。
7. review 后 commit/PR。

## 技术路线

如果做桌面优先：

- Tauri：更轻，适合 Rust backend，参考 `OpenCovibe/codeg`。
- Electron：node-pty、better-sqlite3、GraphQL、terminal 集成更顺，参考 `玄圃/ouijit`。

我的偏好：第一版用 Electron 会更快，因为本地 terminal、PTY、SQLite、文件 watcher、外部 CLI spawn 都是核心路径。Tauri 适合后面追求体积和原生体验。

数据存储建议：

- SQLite 存 workspace/task/session/run/artifact/index。
- JSONL 存高频 event stream。
- 文件系统存大对象：terminal raw output、screenshots、diff patches、agent transcripts。

关键边界：

- agent adapter 一开始就要抽象，避免绑定 Codex。
- worktree 是默认隔离层。
- sandbox 是高风险命令的第二层，不是 MVP 起点。
- permission/request_user_input/question 必须进入统一 event model。
- 所有 event 都要可 replay，UI 不应该只吃 live stream。

## 下一步

继续深读时，优先顺序是：

1. `OpenCovibe/src-tauri/src/agent/*`：抽象 agent protocol adapter。
2. `玄圃/src/main/field/*`：抽象现场事件和 context injection。
3. `kanbots/packages/local-store/src/types.ts` + `packages/api/src/handlers/agent-runs.ts`：抽象任务和 run。
4. `ouijit/src/worktree.ts`：抽象 worktree lifecycle。
5. `codeg/src-tauri/src/acp/delegation/*`：抽象多 agent delegation。

