# Waishnav/devspace 调研：把 ChatGPT 接到本地 workspace 的早期 MCP 桥

日期：2026-06-18

对象：[Waishnav/devspace](https://github.com/Waishnav/devspace)

## 结论

DevSpace 是一个真实可运行的早期项目。它的核心不是再启动一个本地 coding agent，而是把本机文件读写、搜索、编辑、shell、Git worktree、项目指令和 skills 暴露成 remote Streamable HTTP MCP server，让 ChatGPT 这类 MCP host 直接操作用户允许的本地 workspace。

这个方向值得关注，尤其对我们关心的 workspace-scoped conversation、source/artifact/run 回写、AGENTS.md/skill-driven workflow 有直接参考价值。它把 Codex 类 loop 抽成了一个 MCP tool surface：先 `open_workspace`，拿到 `workspaceId`，之后所有 read/edit/bash/show changes 都围绕这个 workspaceId 走。这个设计比把整个本地 agent 隐在后面更可检查，也更贴近 ChatGPT remote MCP 的产品形态。

不过，它现在更像 v1 原型，而不是可以放心长期暴露公网的基础设施。最大问题是 OAuth client/token 状态仍是内存态；服务一重启，ChatGPT 可能继续带旧 `client_id` 进入 OAuth flow，项目已有公开 issue 复现了 `invalid_client`。另外，shell 工具的实际权限接近本地终端，文件 allowlist 不能替代 shell sandbox。依赖链上还有两个 `npm audit` high，需要等上游 `@earendil-works/pi-coding-agent` 或 lock/overrides 修正。

## 它是什么

[README](https://github.com/Waishnav/devspace/blob/main/README.md) 对外说法是 Bring a Codex-style coding workflow to ChatGPT。代码里这个说法基本成立：`src/server.ts` 用 `@modelcontextprotocol/sdk` 起 Streamable HTTP MCP server，注册 `open_workspace`、read/write/edit/search/list/bash、review changes 等工具；`src/pi-tools.ts` 把这些工具委托给 `@earendil-works/pi-coding-agent` 的本地 coding primitives；`src/workspaces.ts` 负责 workspaceId、路径约束、AGENTS.md/CLAUDE.md 载入和 skills discovery。

项目的关键约束写在自己的 [AGENTS.md](https://github.com/Waishnav/devspace/blob/main/AGENTS.md) 里：它不是把任务转交给另一个 local coding agent，而是让 MCP host 通过显式 tool calls 直接读文件、改文件、搜索和跑 shell。这个取向很重要，因为它把决策权留在 host model 上，本地进程主要承担 capability gateway 的角色。

功能面上，它支持：

- approved local roots：只允许打开配置过的本地目录。
- `open_workspace`：为一个项目目录创建 workspace session。
- project instructions：root `AGENTS.md` / `CLAUDE.md` 自动加载，nested instruction 返回路径让模型显式读取。
- local skills：默认从 `~/.codex`、project `.pi/skills`、`DEVSPACE_SKILL_PATHS` 发现 skills。
- file tools：read/write/edit/search/list。
- bash：用于 tests/build/git/package scripts 等。
- managed worktree：在 `~/.devspace/worktrees` 下创建 detached worktree，支持隔离并行工作。
- Apps widget：为 ChatGPT Apps-compatible host 提供 diff/review card metadata。

## 成熟度

GitHub 元数据说明它很新：[repo](https://github.com/Waishnav/devspace) 创建于 2026-06-14，2026-06-16 发布 [`v1.0.0`](https://github.com/Waishnav/devspace/releases/tag/v1.0.0)，2026-06-17 还在改 README 和本地启动说明。2026-06-18 查询时约 434 stars、36 forks，公开 issues 里已有两个直接与使用稳定性相关的问题。

本地验证结果比 README 更有价值：

```text
npm ci             pass, but audit reports 2 high vulnerabilities
npm run typecheck  pass
npm test           first run hit temp .git/ai cleanup race, rerun pass
npm run build      pass
node dist/cli.js doctor  pass, SQLite native dependency ok
serve + /healthz   pass: {"ok":true,"name":"devspace"}
```

CI 侧也有佐证：项目的 [GitHub Actions workflow](https://github.com/Waishnav/devspace/blob/main/.github/workflows/ci.yml) 覆盖 `ubuntu-latest`、`macos-latest`、`windows-latest`，最近 5 次 `CI` run 都是 success。

因此这不是空壳项目。它能安装、构建、跑测试、启动 server，并通过 health check。但我没有验证真实 ChatGPT remote MCP OAuth flow、Cloudflare Tunnel 外网链路和 ChatGPT Apps widget 渲染，所以不能把它评价为端到端 production-ready。

## 关键风险

第一，OAuth 状态持久化缺口已经影响真实用户。[Issue #2](https://github.com/Waishnav/devspace/issues/2) 报告了 Windows + Cloudflare tunnel 下，服务重启后 ChatGPT 复连失败，OAuth 页面返回：

```json
{"error":"invalid_client","error_description":"Invalid client_id"}
```

源码支持这个判断：`src/oauth-provider.ts` 里的 `InMemoryOAuthClientsStore` 用 `Map` 保存 clients，authorization codes、access tokens、refresh tokens 也都是内存 `Map`。与此同时，`src/workspace-store.ts` 只持久化 workspace sessions。也就是说 workspaceId 能从 SQLite 恢复，不代表 OAuth client registration 能恢复。

第二，安装体验还不够稳定。[Issue #3](https://github.com/Waishnav/devspace/issues/3) 是 `devspace not found`。README 和 [gotchas doc](https://github.com/Waishnav/devspace/blob/main/docs/gotchas.md) 已经补了 `npx @waishnav/devspace` fallback 和 npm global bin PATH 提醒，但面向 ChatGPT 普通用户时，这仍会是第一层流失点。

第三，shell access 的风险边界要按本地终端看。项目自己的 [Security Model](https://github.com/Waishnav/devspace/blob/main/docs/security.md) 说得比较清楚：文件工具有 workspace allowlist，但 shell command 以本地用户权限运行。Managed worktree 也只是 workflow boundary，不是 security boundary。

第四，依赖链当前有安全告警。`npm audit --json` 报两个 high，来自 `@earendil-works/pi-coding-agent -> @earendil-works/pi-ai` 下的 `protobufjs@7.5.9` 和 `ws@8.20.1`。`package.json` 虽然写了 overrides 到 `protobufjs@7.6.4`、`ws@8.21.0`，但本地 `npm ls protobufjs ws` 仍显示嵌套依赖停在旧版本。这个问题需要实际修 lockfile 或上游依赖版本，不能只看 `package.json` 里的 overrides。

## 对我们的参考价值

DevSpace 最值得借鉴的是 workspace gateway 的产品边界，而不是具体代码。它没有试图把整个 local agent 封成黑盒，而是把 capabilities 拆成明确 MCP tools，并用 `open_workspace -> workspaceId -> scoped tools` 维持会话上下文。这个模式适合我们后续思考 Mindspace Workspace：workspace 不是一个 UI tab，而是一个带边界、权限、指令、工具和状态恢复的操作上下文。

它对 AGENTS.md 和 skills 的处理也值得参考。root instruction 自动加载，nested instruction 只返回路径让模型按需读取；skills 只允许读 advertised `SKILL.md`，读过后才开放该 skill 目录下的资源。这比全量注入上下文更省 token，也更符合可检查性。

worktree mode 的取向同样有用：它承认 dirty checkout 的存在，只报告 `dirtySource`，不偷偷复制未提交变更。这一点可以迁移到我们自己的 workspace/run 设计里：不要试图替用户修复所有状态，只要把状态差异明确暴露给 agent 和用户。

## 是否值得用

如果目标是研究 ChatGPT remote MCP + 本地 workspace gateway，值得 clone 下来读，也值得在受控本地环境跑。它已经有足够多的真实实现细节，可以作为 reference implementation 看。

如果目标是把它作为日常主力 coding bridge，我会等几个问题处理完：OAuth client 持久化、安装路径稳定性、依赖 audit、以及更完整的 tunnel + ChatGPT 端到端文档。现在更适合作为实验工具，而不是长期在线的本机入口。

对我们来说，下一步最有价值的不是直接采用 DevSpace，而是把它的几个设计点整理进 workspace 技术判断：`open_workspace` 模型、instruction/skill gating、worktree session、review widget、shell 风险边界、OAuth 持久化要求。这些都是后续设计 Workspace Harness 或本地开发环境接入时可以复用的约束。

## 本次产物

- Scratchpad: `tmp/2026_06_18_devspace_survey/scratchpad.md`
- Manifest: `tmp/2026_06_18_devspace_survey/search_manifest.md`
- Clone: `tmp/2026_06_18_devspace_survey/repo`
