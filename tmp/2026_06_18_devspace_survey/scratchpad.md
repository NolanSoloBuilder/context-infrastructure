# DevSpace 调研 Scratchpad

日期：2026-06-18

对象：[Waishnav/devspace](https://github.com/Waishnav/devspace)

## 基本事实

- GitHub repo 创建于 2026-06-14，默认分支 `main`。
- GitHub 描述是 "Turn ChatGPT into Codex"。
- 2026-06-18 查询时，GitHub repo 为 434 stars、36 forks、2 个 open issues；最近 push 为 2026-06-17。
- 最新 GitHub release 是 [`v1.0.0`](https://github.com/Waishnav/devspace/releases/tag/v1.0.0)，发布时间 2026-06-16。
- npm 包 [`@waishnav/devspace`](https://www.npmjs.com/package/@waishnav/devspace) 的 latest 是 `1.0.1`，发布时间 2026-06-16。
- License: MIT。

## Claim Extraction

| Claim | 来源 | 验证通道 | 验证状态 |
|---|---|---|---|
| DevSpace 把 ChatGPT 变成类似 Codex 的本地 coding workflow | [README](https://github.com/Waishnav/devspace/blob/main/README.md) | 源码看 MCP server、工具注册、Pi SDK adapter | 部分成立。它暴露 read/write/edit/search/bash/worktree 等工具，但能力取决于 MCP host 是否支持 remote MCP、OAuth、tool calls 和 Apps widget metadata。 |
| 它不会上传代码到第三方，用户通过自控 tunnel 暴露本机 | [README](https://github.com/Waishnav/devspace/blob/main/README.md), [Security Model](https://github.com/Waishnav/devspace/blob/main/docs/security.md) | 源码看 Express server、本地 path allowlist、publicBaseUrl | 代码路径与声明一致：server 在本地起 Express/MCP endpoint，自行配置 public URL；但一旦暴露 tunnel，本质就是把本机 shell/file access 授权给 MCP client。 |
| 支持 OAuth owner approval | [PR #1](https://github.com/Waishnav/devspace/pull/1), [oauth-provider.ts](https://github.com/Waishnav/devspace/blob/main/src/oauth-provider.ts) | 源码看 provider 和 store | 成立，但当前 OAuth client/token 状态是内存态。服务重启后 client_id 会丢失。 |
| 支持 workspace session 持久化 | [workspace-store.ts](https://github.com/Waishnav/devspace/blob/main/src/workspace-store.ts) | 源码看 SQLite schema 和恢复逻辑 | 成立。workspace session 使用 `better-sqlite3` + Drizzle 保存；但这不覆盖 OAuth client/session transport。 |
| 支持 AGENTS.md / CLAUDE.md 和 skills | [README](https://github.com/Waishnav/devspace/blob/main/README.md), [chatgpt-coding-workflow.md](https://github.com/Waishnav/devspace/blob/main/docs/chatgpt-coding-workflow.md) | 源码看 `workspaces.ts`、`skills.ts` | 成立。root instructions 自动加载，nested instructions 返回路径；skills 支持 `.codex`、project `.pi/skills` 和 `DEVSPACE_SKILL_PATHS`。 |
| 支持 managed Git worktree | [chatgpt-coding-workflow.md](https://github.com/Waishnav/devspace/blob/main/docs/chatgpt-coding-workflow.md), [git-worktrees.ts](https://github.com/Waishnav/devspace/blob/main/src/git-worktrees.ts) | 源码和测试 | 成立。worktree 模式从 Git repo 创建 detached managed worktree；dirty source 只报告，不复制未提交变更。 |
| CI 覆盖 Linux/macOS/Windows | [ci.yml](https://github.com/Waishnav/devspace/blob/main/.github/workflows/ci.yml) | GitHub Actions run list | 成立。最近 5 次 `CI` workflow 都是 success。 |

## 本地源码验证

Clone 路径：

```text
tmp/2026_06_18_devspace_survey/repo
```

执行结果：

```text
npm ci
  added 363 packages
  npm audit: 2 high severity vulnerabilities

npm run typecheck
  pass

npm test
  first run failed with ENOTEMPTY on temporary .git/ai/working_logs
  rerun pass

npm run build
  pass

node dist/cli.js doctor
  Node v25.2.1 supported
  Git available
  Bash available
  SQLite native dependency ok

node dist/cli.js serve + curl /healthz
  {"ok":true,"name":"devspace"}
```

第一次 `npm test` 失败路径是：

```text
/var/folders/.../T/devspace-workspace-test-.../git-project/.git/ai/working_logs
```

复跑通过。因为失败目录是 Codex/AI 环境写入的 `.git/ai` 日志目录，不是 DevSpace 测试主动创建的业务文件，判断为本机环境副作用，而非稳定失败。

## 代码结构

- `src/server.ts`: Express + Streamable HTTP MCP server，注册 tool、OAuth router、Apps resource/widget。
- `src/oauth-provider.ts`: single-user OAuth provider。client/code/access/refresh token 都是内存 `Map`。
- `src/workspaces.ts`: workspace registry，加载 `AGENTS.md`/`CLAUDE.md`，开放 workspace path resolution。
- `src/workspace-store.ts`: SQLite 持久化 workspace sessions。
- `src/pi-tools.ts`: 对 `@earendil-works/pi-coding-agent` 的 read/write/edit/grep/find/ls/bash 工具做 MCP adapter。
- `src/git-worktrees.ts`: managed worktree 创建。
- `src/skills.ts`: skills discovery 和 skill read gating。
- `src/ui/*`: ChatGPT Apps compatible diff/review card UI。

## 已知问题和风险

1. OAuth client store 是内存态。
   - 对应公开 issue: [#2 OAuth client_id becomes invalid after server restart](https://github.com/Waishnav/devspace/issues/2)
   - 源码证据：`InMemoryOAuthClientsStore`、`codes`、`accessTokens`、`refreshTokens` 都是 `Map`。
   - 影响：服务重启后，ChatGPT 可能继续使用旧 client_id，从而拿到 `invalid_client`。

2. 安装路径仍有人踩坑。
   - 对应公开 issue: [#3 devspace not found](https://github.com/Waishnav/devspace/issues/3)
   - 文档已补 `npx` fallback 和全局 npm bin PATH 提醒，但对普通 ChatGPT 用户仍是 onboarding friction。

3. shell 工具不是强沙箱。
   - 官方 security doc 也明确说 shell 命令以本地用户权限运行。
   - 文件工具有 allowlist，shell 命令的实际能力接近本地终端。

4. audit 有两个 high。
   - `protobufjs <=7.6.2` via `@earendil-works/pi-coding-agent -> @earendil-works/pi-ai -> @google/genai`
   - `ws >=8.0.0 <8.21.0` via `@earendil-works/pi-coding-agent -> @earendil-works/pi-ai`
   - `package.json` 写了 overrides：`protobufjs: 7.6.4`、`ws: 8.21.0`，但 `npm ls` 仍显示 nested dependency 是 `protobufjs@7.5.9` 和 `ws@8.20.1`。说明当前 overrides 没有覆盖到嵌套依赖，或 lockfile/resolution 未生效。

## 初步判断

DevSpace 是一个真实可运行的早期项目，不是 README demo。它的核心价值在于把 ChatGPT remote MCP 接到本地 workspace，并把 Codex 类工作流的几个关键能力组织成一个 MCP surface：workspaceId、AGENTS.md、skills、文件编辑、bash、managed worktree、review widget。

但它还不到可以长期无人看管暴露公网的成熟度。OAuth 持久化、安装体验、依赖安全、shell 风险边界是当前最需要处理的部分。
