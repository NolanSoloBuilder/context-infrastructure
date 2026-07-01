# birdclaw 调研 scratchpad

日期：2026-06-23

调研对象：https://birdclaw.sh/

## 初步判断

birdclaw 是 Peter Steinberger / `steipete` 做的 local-first Twitter/X 个人数据工作台。它把 X archive import、live sync、SQLite/FTS5、本地 Web UI、CLI、OpenAI inbox/digest、reply/moderation、Git-friendly backup 放在一个工具里。

它的真实定位更接近“面向 power user / agent 的个人 X 数据操作系统”，而不是单纯的 archive search CLI。

## Claim Extraction

| Claim | 来源层级 | 验证通道 | 验证状态 |
|---|---|---|---|
| local-first Twitter workspace，数据放本地 SQLite | Tier 1: 官网/README | 源码 `src/lib/db.ts` schema、默认路径文档、package 架构 | 已验证。SQLite schema 覆盖 accounts/profiles/tweets/DM/blocks/mutes/AI scores 等；默认路径为 `~/.birdclaw` |
| CLI + Web + scriptable JSON | Tier 1: 官网/README | `src/cli.ts`、package scripts、CLI spec | 已验证。Commander CLI 注册多个 domain command；web 由 TanStack/React + production server 提供 |
| archive-first + live-aware | Tier 1: docs/spec/sync/auth | docs/auth.md、docs/sync.md、源码 live transport | 已验证。官方文档强调先 archive 建立 account identity，再 live sync；live 依赖 `xurl` / `bird` |
| AI-ranked inbox / streaming digest | Tier 1: docs/inbox、CLI spec | 源码 `src/lib/openai.ts`、`src/lib/period-digest.ts` | 已验证但有产品化边界：prompt 中仍硬编码 Peter 场景 |
| real and usable, not finished | Tier 1: README/官网 | release cadence、issues、源码状态 | 基本可信。2026-04-27 到 2026-06-21 发布 17 个 npm 版本；最新 release 有 CI/test proof；同时 docs 和源码仍有个人化/快速演化痕迹 |
| stable JSON envelopes | Tier 1: 官网/CLI spec | CLI 注册和测试 | 部分验证。测试/文档覆盖多处 `--json`，但未实际运行 CLI，因为本机 Node `v25.2.1` 低于项目要求 |

## 关键事实

- GitHub repo: https://github.com/steipete/birdclaw
- 官网: https://birdclaw.sh/
- 当前 npm latest: `birdclaw@0.8.5`，发布时间 2026-06-21T23:27:50Z。来源：`https://registry.npmjs.org/birdclaw/latest`
- npm package engine: `>=25.8.1 <27`
- Homebrew formula 当前 `brew info steipete/tap/birdclaw` 显示 stable `0.8.4`，落后 npm 一个 patch。
- GitHub API 检索时间：2026-06-23。repo 当时显示约 1.1k stars、100 forks、open issues 1、public、MIT。
- release `v0.8.5`：2026-06-21，声明 141 test files / 1,173 tests passed，90.83% line / 80.45% branch coverage，12 Playwright E2E passed。
- CI run `27920819997`：success，2m29s。
- 本地源码静态检查：`src` 下 355 个文件，其中 TypeScript/TSX 354 个；测试文件 141 个。没有安装依赖，也没有跑测试。

## 源码观察

### 工程形态

- TypeScript + React + TanStack Start + Effect + native `node:sqlite`。
- `package.json` 发布文件包括 `bin/`, `dist/cli/`, `dist/client/`, `dist/server/`，说明 0.8.4 后已经从运行时 TS/Vite 依赖转向 compiled artifact。
- `src/cli.ts` 用 Commander 注册 core/search/analysis/mentions/dms/sync/jobs/moderation/compose/inbox/graph/storage/serve。
- `src/lib/db.ts` 有较大的 baseline schema，使用 `user_version` migrations。
- `.github/workflows/ci.yml` 跑 format/lint/typecheck/coverage/build/Playwright。

### 产品边界

- `src/lib/openai.ts` 的 inbox scoring system prompt 写的是 “for Peter Steinberger”。
- `src/lib/period-digest.ts` prompt 里也有 “whether Peter already joined the conversation”。
- 这说明它仍明显带个人工具属性。如果作为通用工具给其他人用，AI scoring/digest 的默认语义会偏作者本人。

### 安全/隐私边界

- local web 默认无 auth，但 production server 只把 loopback socket 标记成本地 peer；远程访问需要 `BIRDCLAW_ALLOW_REMOTE_WEB=1` 或 `BIRDCLAW_WEB_TOKEN`。
- `bird` 读取浏览器 cookies；docs 明确把 `auth_token` / `ct0` 视作完整账号凭据。
- backup 会把 tweets/DM/profile/follow graph/moderation 等写成 JSONL shards；`backup sync` 会 pull/import/export/commit/push。适合私有 Git repo，不适合误推公开仓库。

## 独立证据

### 支持成熟度的证据

- release 页面包含 package integrity、CI run、测试数量、coverage、Playwright E2E。
- GitHub Actions 最近 main push 和 release CI 成功。
- 有多位外部 contributor 的 PR 被合入，例如 `cavit99`, `peetzweg`, `uwe-schwarz`, `yujiawei`, `devYRPauli`。
- 第三方 issue #45 报告文档命令已记录但未实现；后续 release/changelog 显示修复。
- 第三方 issue #61 报告 JSONL backup 导入遇到 Unicode separator；PR #62 修复并进入 0.8.4 release。

### 支持“还在变”的证据

- 官网/README 直接标注 WIP、schema churn、transport gaps、rough edges expected。
- open issue #65 要求 native List-scoped tweet search，说明高信号 curated subset 仍未覆盖。
- release 节奏快且改动面大，0.8.3/0.8.4 涉及 SQLite writer、schema migration、backup codec、runtime package、query plan 等基础层。
- Homebrew `0.8.4` 与 npm `0.8.5` 存在短暂版本差。

## 同类项目参照

- `dogsheep/twitter-to-sqlite`: 老牌 SQLite 数据导入工具，但 README 仍说明使用 Twitter API v1；GitHub issue #54 显示 2021 年新 export 格式已造成 archive import 问题。
- `DocNow/twarc`: 学术/归档向 Twitter JSON 工具，README 明确 API quota 变化后已不再 active supported。
- `Dicklesworthstone/xf`: 现代 X archive 搜索 CLI，重点是 ultra-fast local search / Tantivy / SQLite / optional semantic，范围比 birdclaw 窄。
- `lhl/tweetxvault`: 更接近现代 archive/sync/search，支持 browser cookie、raw capture、FTS + optional semantic search，但没有 birdclaw 这种 web workspace/reply/moderation/digest 一体化形态。

## 待进一步验证

- 实际 archive import 兼容性：需要用户自己的 X archive 或 sample archive 才能做真实验收。
- `bird` / `xurl` 的当前可用性：`bird` 曾在其它 OpenClaw 生态 issue 中出现 repo/asset 404 问题，但 birdclaw docs 仍把它列为推荐可选 transport；要试用需单独验证。
- OpenAI 默认模型可用性：项目默认/文档中出现 `gpt-5.5`、`gpt-5.2`；不同账号或 API 网关未必可用。
- 大库性能：release 有 quadratic scan 修复，但没有本地大 archive benchmark。

